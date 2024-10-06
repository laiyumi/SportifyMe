
import React, { useState, useEffect, useRef } from 'react'; // #qiaohui: 添加 useRef
import VideoStream from './VideoStream';


const TaskPage = ({title, content, onNext, onDataSubmit, videoUrl, sportType}) => {

    const [timer, setTimer] = useState(10); // 10-second timer
    const [isCameraLive, setIsCameraLive] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false); // #qiaohui: add video control button
    const videoRef = useRef(null); // #qiaohui: add video control button

    // Countdown timer logic
    useEffect(() => {
        if (timer > 0) {
        const interval = setInterval(() => {
            setTimer((prevTimer) => prevTimer - 1);
        }, 1000);
        return () => clearInterval(interval); // Clean up interval on component unmount
        }
    }, [timer]);

    // Simulate turning on the live camera
    useEffect(() => {
        setIsCameraLive(true); // Camera goes live when the page loads
    }, []);

    const [inputData, setInputData] = useState('');

    // Handle input changes
    const handleInputChange = (e) => {
      setInputData(e.target.value);  // Update the state as user types
    };

    // Function to handle "Next" button click
    const handleSubmit = () => {
      if (onDataSubmit) {
        onDataSubmit(inputData);  // Pass the input data to parent via onDataSubmit
      }
      onNext();  // Navigate to the next page
    };

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

    // Add this near the top of your component body
    console.log('Current video URL:', videoUrl);

    return (
        <div className="flex-row h-screen p-16"> {/* Changed to a flex container for two columns */}
          <div className="flex flex-col justify-center items-center mb-6">
              <h3 className="text-2xl font-bold">{title}</h3>
              <h4 className="text-lg">{content}</h4>
          </div>
          <div className="flex flex-grow">
              <div className="flex flex-col justify-center items-center w-1/2 p-4"> {/* Left column for video */}
                  <h5 className="text-2xl font-bold mb-6">Demo Video</h5>
                  <video
                      ref={videoRef}
                      width="320"
                      height="240"
                      controls={false}
                  >
                      <source src={videoUrl} type="video/mp4" />
                      Your browser does not support the video tag.
                  </video>
                  <button 
                      className="btn btn--accent text-lg mt-4" 
                      onClick={toggleVideo}
                  >
                      {isPlaying ? 'Pause Video' : 'Play Video'}
                  </button>
              </div>

              <div className="flex flex-col justify-center items-center w-1/2 p-4"> {/* Right column for other content */}
                    <h1 className="text-2xl font-bold mb-6 text-center">Timer: {timer}s</h1>
                      <VideoStream sportType={sportType} />
                        <input
                          type="text"
                          placeholder="How many have you done?"
                          className="input input-bordered input-primary w-full max-w-xs"
                          value={inputData}
                          onChange={handleInputChange} />
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
}

export default TaskPage