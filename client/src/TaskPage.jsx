import React, { useState, useEffect, useRef } from "react"; // #qiaohui: 添加 useRef
import axios from "axios";

const TaskPage = ({
  title,
  content,
  onNext,
  onDataSubmit,
  videoUrl,
}) => {
  const [timer, setTimer] = useState(10); // 10-second timer

  // Countdown timer logic
  useEffect(() => {
    if (timer > 0) {
      const interval = setInterval(() => {
        setTimer((prevTimer) => prevTimer - 1);
      }, 1000);
      return () => clearInterval(interval); // Clean up interval on component unmount
    }
  }, [timer]);

  const [isPlaying, setIsPlaying] = useState(false); // #qiaohui: add video control button
  const videoRef = useRef(null); // #qiaohui: add video control button

  // #qiaohui: add toggle video function
  const toggleVideo = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  // #qiaohui: Add this useEffect to handle video changes
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.load(); // #qiaohui: Reload the video when the URL changes
      setIsPlaying(false); // #qiaohui: Reset the playing state
    }
  }, [videoUrl]);

  const [inputData, setInputData] = useState("");

  // Handle input changes
  const handleInputChange = (e) => {
    setInputData(e.target.value); // Update the state as user types
  };

  // Function to handle "Next" button click
  const handleSubmit = () => {
    if (onDataSubmit) {
      onDataSubmit(inputData); // Pass the input data to parent via onDataSubmit
    }
    onNext(); // Navigate to the next page
  };

  const imgRef = useRef(null);
  const [isRecording, setIsRecording] = useState(false);
  const [task, setTask] = useState('');

  const handleStartRecording = () => {
    setIsRecording(true);
    setTask(title);
  };

  const handleStopRecording = async () => {
    setIsRecording(false);
    try {
      const response = await axios.post("/api/stop_recording", task, {
        headers: {
          "Content-Type": "application/json",
        },
      });
      console.log(response.data.message);
    } catch (error) {
      console.error("Error stopping video feed:", error);
    }
  };

  useEffect(() => {
    if (imgRef.current) {
      if (isRecording) {
        imgRef.current.src = "/api/start_recording";
      } else {
        imgRef.current.src = "https://placehold.co/600x400?text=Hello+World";
      }
    }
  }, [isRecording]);
  

  return (
    <div className="flex-row h-screen p-16">
      {" "}
      {/* Changed to a flex container for two columns */}
      <div className="flex flex-col justify-center items-center mb-6">
        <h3 className="text-2xl font-bold">{title}</h3>
        <h4 className="text-lg">{content}</h4>
      </div>
      <div className="flex flex-grow">
        <div className="flex flex-col justify-center items-center w-1/2 p-4">
          {" "}
          {/* Left column for video */}
          <h5 className="text-2xl font-bold mb-6">Demo Video</h5>
          <video ref={videoRef} width="320" height="240" controls={false}>
            <source src={videoUrl} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
          <button
            className="btn btn--accent text-lg mt-4"
            onClick={toggleVideo}
          >
            {isPlaying ? "Pause Video" : "Play Video"}
          </button>
        </div>

        <div className="flex flex-col justify-center items-center w-1/2 p-4">
          {" "}
          {/* Right column for other content */}
          <h1 className="text-2xl font-bold mb-6 text-center">
            Timer: {timer}s
          </h1>
          <div
            className="flex flex-col justify-evenly items-center w-full h-full"
          >
            <h1 className="text-2xl font-bold">Live Pose Detection</h1>
            <div className="w-300 h-200 overflow-hidden border-2 border-solid border-gray-200">
              {isRecording ?(
                <img ref={imgRef} alt="Video Feed" className="object-cover w-full h-full" />
              ): (
                <img src="https://placehold.co/600x400?text=Video+Stream" alt="Placeholder" className="object-cover w-full h-full" />
              )}
            </div>
            <div className="flex flex-row gap-4">
              <button
                onClick={handleStartRecording}
                className="btn btn-info btn-sm"
              >
                Start Recording
              </button>
              <button
                onClick={handleStopRecording}
                className="btn btn-success btn-sm"
              >
                Stop Recording
              </button>
            </div>
          </div>
          <input
            type="text"
            placeholder="How many have you done?"
            className="input input-bordered input-primary w-full max-w-xs"
            value={inputData}
            onChange={handleInputChange}
          />
          <button
            className="btn btn-primary text-lg mt-4"
            onClick={handleSubmit}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaskPage;
