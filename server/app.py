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


@app.route('/api/process_pose_data', methods=['POST'])
def process_pose_data():
    # Process all JSON files and extract key data
    for filename in os.listdir('.'):
        if filename == 'pose_data_session_setup.json':
            step_up_times = get_step_out_num(filename)
        elif filename == 'pose_data_session_squats.json':
            squats_times = get_squat_num(filename)
        elif filename == 'pose_data_session_jumping_jack.json':
            jumping_jack_times = get_jumping_jack_num(filename)

        key_data = {
            "session": filename,
            "set_up_times": step_up_times,
            "squat_times": squats_times,
            "jumping_jack_times": jumping_jack_times,
        }
        # Insert into MongoDB
        collection.insert_one(key_data)

    return jsonify({"message": "Pose data processed and stored in MongoDB."}), 200

if __name__ == "__main__":
    app.run(debug=True)
