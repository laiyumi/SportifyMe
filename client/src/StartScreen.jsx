import React from 'react';


function StartScreen({ onStart }) {
  return (
    <div className="flex flex-col justify-center items-center h-screen bg-base-200">
      <h1 className="text-2xl font-bold mb-6">Hi, there!</h1>
      <h1 className="text-4xl font-bold mb-6">SportifyMe</h1>
      <h1 className='text-2xl mb-10'>Unlock your potential in sports with our ultimate AI coach.</h1>
      
      <button 
        className="btn btn-secondary"
        onClick={onStart}
      >
        Start
      </button>
    </div>
  );
}

export default StartScreen;