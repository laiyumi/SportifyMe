import React, { useState } from 'react';
import ResultPage from './ResultPage.jsx';
import StartScreen from './StartScreen.jsx';
import TaskPage from './TaskPage.jsx';

const App = () => {
  const [currentPage, setCurrentPage] = useState('start');

  // handle page navigation
  const handleNavigation = (page) => {
    setCurrentPage(page);
  }

  // collect data from each task
  const [formData, setFormData] = useState({
    task1: '',
    task2: '',
    task3: ''
  });

  // #qiaohui: Add a new state to store video URLs
  const [videoUrls] = useState({
    task1: '/videos/Set_up.mp4',
    task2: '/videos/deep_squats.mp4',
    task3: '/videos/Single_leg_balance.mp4'
  });

  // Function to collect data from each task page
  const handleDataChange = (taskName, data) => {
    setFormData((prev) => ({
      ...prev,
      [taskName]: data,  // Update specific task data
    }));
  };

  // After completing all tasks, map the task results to the three aspects
  const getTaskResults = () => ({
    strengthEndurance: formData.task1,
    flexibility: formData.task2,
    balanceCoordination: formData.task3
  });

  // Displaying data on the frontend
  return (
    <div>
      {currentPage === 'start' && <StartScreen
        onStart={() => handleNavigation('task1')}
      />}
      {currentPage === 'task1' && <TaskPage
        title="Task 1: Step Up"
        content="Do as many step-ups as possible in 10 seconds."
        onNext={() => handleNavigation('task2')}
        onDataSubmit={(data) => handleDataChange('task1', data)}
        videoUrl={videoUrls.task1}  // #qiaohui: Add this line
      />}
      {currentPage === 'task2' && <TaskPage
        title="Task 2: Deep Squat"
        content="Do as many as deep squats in 10 seconds."
        onNext={() => handleNavigation('task3')}
        onDataSubmit={(data) => handleDataChange('task2', data)}
        videoUrl={videoUrls.task2}  // #qiaohui: Add this line

      />}
      {currentPage === 'task3' && <TaskPage
        title="Task 3: Single Leg Balance"
        content="Balance on one leg for as long as possible."
        onNext={() => handleNavigation('results')}
        onDataSubmit={(data) => handleDataChange('task3', data)}
        videoUrl={videoUrls.task3}  // #qiaohui: Add this line
      />}

      {currentPage === 'results' && (
        <ResultPage
          results={getTaskResults()}
        />
      )}
    </div>
  );
};

export default App;