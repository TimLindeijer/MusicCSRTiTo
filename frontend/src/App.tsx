import React, { useEffect, useState } from 'react';
import axios from 'axios';

// Define the type for the data you expect to receive
interface ApiResponse {
  message: string;
}

function App() {
  // Define the state type as string or null
  const [data, setData] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get<ApiResponse>('http://localhost:8000/api/data');
        setData(response.data.message);
      } catch (error) {
        console.error("Error fetching data: ", error);
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      <h1>React with FastAPI</h1>
      <p>{data ? data : 'Loading...'}</p>
    </div>
  );
}

export default App;
