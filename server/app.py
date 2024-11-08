import json
import certifi
from flask import Flask, jsonify, Response, request
from pymongo import MongoClient
from datetime import datetime, timezone  # Import timezone
from bson.objectid import ObjectId
import random
import os
import replicate
import cv2
import mediapipe as mp
from process_json import get_squat_num, get_step_out_num, get_jumping_jack_num, get_squat_num_performance, get_jumping_jack_num_performance, get_step_out_num_performance
app = Flask(__name__)

# 从上一级目录加载配置文件
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
with open(config_path) as config_file:
    config = json.load(config_file)

# MongoDB 连接配置
uri = "mongodb+srv://yhack:whyhackatyhack@cluster0.lphxsva.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, tlsCAFile=certifi.where())  # 全局客户端变量

# Get the path to the static folder
static_folder = os.path.join(os.getcwd(), 'static')

# Check if the static folder exists
if not os.path.exists(static_folder):
    # If not, create it
    os.makedirs(static_folder)

@app.route("/api/test_connection", methods=["GET"])
def test_connection():
    try:
        # Attempt to retrieve one document from the collection
        user = collection.find_one()
        if user:
            return jsonify({"message": "Successfully connected to MongoDB!", "user": str(user["_id"])}), 200
        else:
            return jsonify({"message": "Connected to MongoDB, but no documents found."}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to connect to MongoDB: {str(e)}"}), 500

# Replicate API token
os.environ["REPLICATE_API_TOKEN"] = config.get("REPLICATE_API_TOKEN") 

# MongoDB 数据库和集合
db = client.YHack
collection = db.videos

# Set up MediaPipe Pose solution
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Initial camera
def init_camera():
    global camera
    camera = cv2.VideoCapture(0)

# Store pose data for each session
is_recording = True
frames =[]

def generate_frames():

    global is_recording, frames

    while is_recording:
        # Read video frame
        success, frame = camera.read()
        if not success:
            break
        # Convert the frame color from BGR to RGB for MediaPipe processing
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame to detect body pose
        result = pose.process(frame_rgb)

        # Extract pose landmarks data
        pose_data = []
        if result.pose_landmarks:
            for landmark in result.pose_landmarks.landmark:
                pose_data.append({
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                })
            frames.append(pose_data)

        # Draw the pose landmarks on the frame
        if result.pose_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Convert the frame back to BGR (so OpenCV can display it)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame as a response to the browser
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    return b'--frame\r\n\r\n'


@app.route("/api/start_recording/")
def video_feed():
    global is_recording, frames
    is_recording = True    
    init_camera()

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stop_recording', methods=['POST'])
def stop_recording():
    global is_recording
    is_recording = False
    camera.release()
    
    task_name = request.get_json()
    # reformat task name
    task_name = task_name.replace(":", "").replace(" ", "_").lower()
    filename = f"{task_name}.json"
    
    with open(os.path.join(app.static_folder, filename), 'w') as f:
        json.dump(frames, f, indent=4)

    frames.clear()

    return jsonify({"message": "Recording stopped and saved data!"}), 200

# add fitness metric to mongobd
@app.route("/api/add_metric", methods=["POST"])
def add_metric():
    key_data = process_pose_data()
    print(f"Key data to be added: {key_data}")  # Log the key data

    result = collection.update_one(
        {"_id": "ObjectId('6700a4ba530c1f6c2d553999')"},
        {"$push": {"metrics": key_data}}
    )
    print(f"Update result: {result.raw_result}")  # Log the update result

    if result.modified_count > 0:
        return jsonify({"message": "Metric added successfully"}), 200
    else:
        print("User not found or metric not added")
        return jsonify({"error": "User not found or metric not added"}), 404

# data process
@app.route('/api/process_pose_data', methods=['POST'])
def process_pose_data():
    step_up_times = squats_times = jumping_jack_times = 0  # Initialize variables
    for filename in os.listdir(os.path.join(app.static_folder)):
        if filename == 'task_1_step_up.json':
            step_up_times = get_step_out_num(os.path.join(app.static_folder, filename))
        elif filename == 'task_2_deep_squat.json':
            squats_times = get_squat_num(os.path.join(app.static_folder, filename))
        elif filename == 'task_3_single_leg_balance.json':
            jumping_jack_times = get_jumping_jack_num(os.path.join(app.static_folder, filename))

    key_data = {
        "date": datetime.now(timezone.utc),  # Use timezone.utc for UTC time
        "set_up_times": step_up_times,
        "single_balance_time": jumping_jack_times,
        "deep_squats_times": squats_times,
    }
    return key_data  # Return the dictionary directly

@app.route('/api/get_performance_metric', methods=['POST'])
def get_history_performance_metric():
    document = collection.find_one({"_id": "ObjectId('6700a4ba530c1f6c2d553999')"})
    if document:
        # Extract the metrics array
        metrics = document.get("metrics", [])
        # Prepare a list to hold the formatted metrics
        formatted_metrics = []
        
        for metric in metrics:
            formatted_metrics.append({
                "date": metric.get("date"),
                "set_up_times": [metric.get("set_up_times"), get_step_out_num_performance(metric.get("set_up_times"))],
                "single_balance_time": [metric.get("single_balance_time"), get_jumping_jack_num_performance(metric.get("single_balance_time"))],
                "deep_squats_times": [metric.get("deep_squats_times"), get_squat_num_performance(metric.get("deep_squats_times"))],
            })
        print(formatted_metrics)
        return jsonify({ "metrics": formatted_metrics}), 200
    else:
        return jsonify({"error": "object not found"}), 404



if __name__ == "__main__":
    app.run(debug=True)
