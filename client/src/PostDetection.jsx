import React, { useRef, useEffect, useState } from 'react';
import '@mediapipe/pose';
import { Camera } from '@mediapipe/camera_utils';
import { Pose } from '@mediapipe/pose';

function PoseDetection() {
  const videoRef = useRef(null);
  const [poseData, setPoseData] = useState([]);

  useEffect(() => {
    if (!videoRef.current) return;

    const pose = new Pose({
      locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
      },
    });

    pose.onResults((results) => {
      const landmarks = results.poseLandmarks.map((landmark) => ({
        x: landmark.x,
        y: landmark.y,
        z: landmark.z,
        visibility: landmark.visibility,
      }));
      setPoseData((prevData) => [...prevData, landmarks]);
    });

    const camera = new Camera(videoRef.current, {
      onFrame: async () => {
        await pose.send({ image: videoRef.current });
      },
      width: 640,
      height: 480,
    });

    camera.start();

    return () => {
      camera.stop();
    };
  }, []);

  const handleStopAndSave = async () => {
    // Transform `poseData` into a JSON file and send it to your Flask backend as shown in the previous response.
    await fetch('http://localhost:5000/save_pose_data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ poses: poseData }),
    });
  };

  return (
    <div>
      <video ref={videoRef} autoPlay muted style={{ display: 'none' }}></video>
      {/* Display video or pose landmarks as needed */}
      <button onClick={handleStopAndSave}>Stop and Save</button>
    </div>
  );
}

export default PoseDetection;
