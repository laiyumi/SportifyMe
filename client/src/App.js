import React, { useState, useEffect } from 'react';
import axios from 'axios';
import StartScreen from './StartScreen.jsx';
import TaskPage from './TaskPage.jsx';
import ResultPage from './ResultPage.jsx';

const App = () => {
  // const [data, setData] = useState([{}]);
  // const [loading, setLoading] = useState(true); // Track loading state
  // const [error, setError] = useState(null); // Track error state

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

  // Fetching data from backend
  // const fetchData = () => {
  //   setLoading(true);
  //   fetch('/api/users')
  //     .then(res => res.json())
  //     .then(data => {
  //       setData(data);
  //       setLoading(false);
  //     })
  //     .catch(error => {
  //       console.log(error);
  //       setError('Error fetching data');
  //       setLoading(false);
  //     });
  // };

  // Call fetchData on component mount
  // useEffect(() => {
  //   fetchData();
  // }, []);

  // Click the button to send a POST request and refresh data
  // const handleAddMetric = () => {
  //   const userId = '6700a5db530c1f6c2df55392'; // The user_id is hardcoded here

  //   axios.post(`/api/add_metric/${userId}`)
  //     .then(response => {
  //       console.log(response.data);
  //       alert(response.data.message); // Show success message in alert
  //       fetchData(); // Re-fetch data after metric is added
  //     })
  //     .catch(error => {
  //       console.error('There was an error adding the fitness metric!', error);
  //       alert('Error adding fitness metric');
  //     });
  // };

  // Displaying data on the frontend
  return (
    <div>
      {currentPage === 'start' && <StartScreen
        onStart={() => handleNavigation('task1')}
      />}
      {currentPage === 'task1' && <TaskPage
        title="Task 1"
        content="Do as many step-ups as possible in 10 seconds."
        onNext={() => handleNavigation('task2')}
        onDataSubmit={(data) => handleDataChange('task1', data)}
        videoUrl={videoUrls.task1}  // #qiaohui: Add this line
        sportType="step-up"
      />}
      {currentPage === 'task2' && <TaskPage
        title="Task 2"
        content="Do as many as deep squats in 10 seconds."
        onNext={() => handleNavigation('task3')}
        onDataSubmit={(data) => handleDataChange('task2', data)}
        videoUrl={videoUrls.task2}  // #qiaohui: Add this line
        sportType="deep-squat"

      />}
      {currentPage === 'task3' && <TaskPage
        title="Task 3"
        content="Stand on one leg and balance for as long as possible."
        onNext={() => handleNavigation('results')}
        onDataSubmit={(data) => handleDataChange('task3', data)}
        videoUrl={videoUrls.task3}  // #qiaohui: Add this line
        sportType="single-leg-balance"
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