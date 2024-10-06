import React from 'react';

function ResultPage({ results }) {
  return (
    <div className="flex flex-col justify-start items-center h-screen bg-base-200 p-16">
      <h1 className="text-3xl font-bold mb-6">Good Job!</h1>
      <h2 className="text-2xl mb-6">This is how your performance looks like:</h2>

    <div className="flex gap-4 justify-center align-center">
      <div className="card w-full max-w-md bg-primary shadow-lg p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">Strength and Endurance</h2>
        <p>{results.strengthEndurance || 'No data available'}</p>
      </div>

      <div className="card w-full max-w-md bg-secondary shadow-lg p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">Flexibility</h2>
        <p>{results.flexibility || 'No data available'}</p>
      </div>

      <div className="card w-full max-w-md bg-success shadow-lg p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">Balance and Coordination</h2>
        <p>{results.balanceCoordination || 'No data available'}</p>
      </div>

    </div>

      <div>
        <h2 className="text-xl font-bold mb-4">Greeting from your AI coach</h2>
            <div className="chat chat-start">
                <div className="chat-image avatar">
                    <div className="w-10 rounded-full ">
                        <img
                            alt="Tailwind CSS chat bubble component"
                            src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" />
                    </div>
                </div>
                <div className="chat-bubble ">Hi there! </div>
            </div>
            <div className="chat chat-start">
                <div className="chat-image avatar">
                    <div className="w-10 rounded-full">
                        <img
                            alt="Tailwind CSS chat bubble component"
                            src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" />
                    </div>
                </div>
                <div className="chat-bubble">My name is Lucy, your personal virtual coach for exploreing and enjoying sports.</div>
            </div>
            <div className="chat chat-start">
                <div className="chat-image avatar">
                    <div className="w-10 rounded-full">
                        <img
                            alt="Tailwind CSS chat bubble component"
                            src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" />
                    </div>
                </div>
                <div className="chat-bubble">Based on your current fitness level, these sports are a great fit for you. I encourage you to give them a try!</div>
            </div>
            <div className="mt-4">
                <span className="loading loading-ring loading-lg"></span>
            </div>
      </div>
    </div>
  );
}

export default ResultPage;