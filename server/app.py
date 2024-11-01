import json
from flask import Flask, jsonify, Response, request
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import random
import os
import replicate
import cv2
import mediapipe as mp
from process_json import get_squat_num, get_step_out_num, get_jumping_jack_num
from flask_cors import CORS

app = Flask(__name__)

# 从上一级目录加载配置文件
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
with open(config_path) as config_file:
    config = json.load(config_file)

# MongoDB 连接配置
uri = "mongodb+srv://yhack:whyhackatyhack@cluster0.lphxsva.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)  # 全局客户端变量

# Replicate API token
os.environ["REPLICATE_API_TOKEN"] = config.get("REPLICATE_API_TOKEN") 

# MongoDB 数据库和集合
db = client.YHack
collection = db.Videos

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


@app.route("/api/start_recording/", methods=["GET"])
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

    # Create a unique filename for each session
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"recording_{timestamp}.json"

    with open(os.path.join(app.static_folder, filename), 'w') as f:
        json.dump(frames, f, indent=4)
    
    frames.clear()
    
    return jsonify({"message": "Recording stopped and saved data!"}), 200

# def save_pose_data_to_json(setup_pose_data, jumping_jack_pose_data, squats_pose_data):
#     # Logic to save pose data into three different JSON files
#     # For example:
#     with open('pose_data_session_setup.json', 'w') as f:
#         json.dump(setup_pose_data, f, indent=4)
#     with open('pose_data_session_jumping_jack.json', 'w') as f:
#         json.dump(jumping_jack_pose_data, f, indent=4)
#     with open('pose_data_session_squats.json', 'w') as f:
#         json.dump(squats_pose_data, f, indent=4)


# @app.route('/api/process_pose_data', methods=['POST'])
# def process_pose_data():
#     # Process all JSON files and extract key data
#     for filename in os.listdir('.'):
#         if filename == 'pose_data_session_setup.json':
#             step_up_times = get_step_out_num(filename)
#         elif filename == 'pose_data_session_squats.json':
#             squats_times = get_squat_num(filename)
#         elif filename == 'pose_data_session_jumping_jack.json':
#             jumping_jack_times = get_jumping_jack_num(filename)

#         key_data = {
#             "session": filename,
#             "set_up_times": step_up_times,
#             "squat_times": squats_times,
#             "jumping_jack_times": jumping_jack_times,
#         }
#         # Insert into MongoDB
#         collection.insert_one(key_data)

#     return jsonify({"message": "Pose data processed and stored in MongoDB."}), 200

if __name__ == "__main__":
    app.run(debug=True)
