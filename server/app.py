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
from process_json import get_squat_num, get_step_out_num, get_jumping_jack_num
app = Flask(__name__)

# 从上一级目录加载配置文件
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
with open(config_path) as config_file:
    config = json.load(config_file)

# MongoDB 连接配置
uri = "mongodb+srv://yhack:whyhackatyhack@cluster0.lphxsva.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, tlsCAFile=certifi.where())  # 全局客户端变量

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

# Capture video from webcam
camera = cv2.VideoCapture(0)

# Store pose data for each session
session_count = 0

def generate_frames(sport_type=""):
    global session_count
    all_pose_data = []

    while True:
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
            all_pose_data.append(pose_data)

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

    # Save pose data to a JSON file after stopping the feed
    session_count += 1
    with open(f'pose_data_session_{session_count}_{sport_type}.json', 'w') as f:
        json.dump(all_pose_data, f, indent=4)

@app.route("/api/video_feed/start_feed/<sport_type>", strict_slashes=False)
def video_feed(sport_type):
    return Response(generate_frames(sport_type), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/video_feed/stop_feed', strict_slashes=False)
def stop_feed():
    camera.release()
    
    # Save pose data to three separate JSON files based on different metrics
    # Assuming you have logic to differentiate the metrics
    # This is a placeholder for the actual implementation
    save_pose_data_to_json()  # New function to save data
    
    return "Video feed stopped and data saved!"

def save_pose_data_to_json(setup_pose_data, jumping_jack_pose_data, squats_pose_data):
    # Logic to save pose data into three different JSON files
    # For example:
    with open('pose_data_session_setup.json', 'w') as f:
        json.dump(setup_pose_data, f, indent=4)
    with open('pose_data_session_jumping_jack.json', 'w') as f:
        json.dump(jumping_jack_pose_data, f, indent=4)
    with open('pose_data_session_squats.json', 'w') as f:
        json.dump(squats_pose_data, f, indent=4)

@app.route("/api/users", methods=["GET"])
def get_users():
    cursor = collection.find()
    users = [dict(user) for user in cursor]

    for user in users:
        user["_id"] = str(user["_id"])

    return {"users": users}

@app.route("/api/users/<user_id>", methods=["GET"])
def get_user_metrics(user_id):
    try:
        object_id = ObjectId(user_id)  # Convert user_id to ObjectId
    except:
        return jsonify({"error": "Invalid user ID format"}), 400

    user = collection.find_one({"_id": object_id})
    if user:
        user["_id"] = str(user["_id"])
        return user
    else:
        return jsonify({"error": "User not found"}), 404

# add fitness metric
@app.route("/api/add_metric", methods=["POST"])
def add_metric():
    try:
        object_id = "ObjectId('6700a4ba530c1f6c2d553999')"
    except Exception as e:
        print(f"Error converting user_id to ObjectId: {e}")
        return jsonify({"error": "Invalid user ID format"}), 400

    key_data = process_pose_data()
    print(f"Key data to be added: {key_data}")  # Log the key data

    result = collection.update_one(
        {"_id": object_id},
        {"$push": {"metrics": key_data}}
    )
    print(f"Update result: {result.raw_result}")  # Log the update result

    if result.modified_count > 0:
        return jsonify({"message": "Metric added successfully"}), 200
    else:
        print("User not found or metric not added")
        return jsonify({"error": "User not found or metric not added"}), 404


@app.route('/api/process_pose_data', methods=['POST'])
def process_pose_data():
    step_up_times = squats_times = jumping_jack_times = 0  # Initialize variables
    for filename in os.listdir('.'):
        if filename == 'pose_data_session_setup.json':
            step_up_times = get_step_out_num(filename)
        elif filename == 'pose_data_session_squats.json':
            squats_times = get_squat_num(filename)
        elif filename == 'pose_data_session_jumping_jack.json':
            jumping_jack_times = get_jumping_jack_num(filename)

    key_data = {
        "date": datetime.now(timezone.utc),  # Use timezone.utc for UTC time
        "set_up_times": step_up_times,
        "single_balance_time": jumping_jack_times,
        "deep_squats_times": squats_times,
    }

    return key_data  # Return the dictionary directly


if __name__ == "__main__":
    app.run(debug=True)
