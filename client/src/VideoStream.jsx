import React, { useState, useEffect } from 'react';

const VideoStream = ({ sportType }) => {
  const [isStreaming, setIsStreaming] = useState(true);

    // Function to start the video feed
    const startVideoFeed = async () => {
        try {
          const response = await fetch(`/api/video_feed/start_feed/${sportType}`);  // Call the Flask endpoint to start the feed
          const data = await response.json();
          console.log(data.message);
          setIsStreaming(true);
        } catch (error) {
          console.error('Error starting video feed:', error);
        }
      };

  // Function to stop the video feed
  const stopVideoFeed = async () => {
    try {
      const response = await fetch(`/api/video_feed/stop_feed`);  // Call the Flask endpoint to stop the feed
      const data = await response.json();
      console.log(data.message);
      setIsStreaming(false);
    } catch (error) {
      console.error('Error stopping video feed:', error);
    }
  };


    // Automatically start the video feed when the component mounts
    useEffect(() => {
        startVideoFeed();
      }, []);


  return (
    <div className='flex flex-col justify-evenly items-center w-full h-full'>
        <h1>Live Pose Detection</h1>
            {isStreaming ? (
                <div className="relative w-full max-w-[375px]"> 
                    <img
                        src={`/api/video_feed/${sportType}`} 
                        alt="Live Video Feed"
                        className="w-full h-auto"
                    />
                </div>
            ) : (
                <p>Video feed has been stopped.</p>
            )}

      <button 
        className="btn btn-primary-outline" 
        onClick={stopVideoFeed} 
        disabled={!isStreaming}>
        Stop Video Feed
      </button>

    </div>
  );
};

export default VideoStream;