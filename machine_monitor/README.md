# Machine Monitor Application

## Overview
This is a full-stack machine monitoring application with a Python FastAPI backend and React frontend.

## Prerequisites
- Python 3.12
- Node.js 18+
- pip
- npm

## Setup and Installation

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

## Running the Application

### Option 1: Separate Terminal Windows
1. Start Backend (Port 8000):
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. Start Frontend (Port 3000):
   ```bash
   cd frontend
   npm start
   ```

### Option 2: Using Concurrently (Recommended)
1. Install concurrently globally:
   ```bash
   npm install -g concurrently
   ```

2. In the project root, create a `package.json`:
   ```json
   {
     "scripts": {
       "start": "concurrently \"npm run start:backend\" \"npm run start:frontend\"",
       "start:backend": "cd backend && source venv/bin/activate && uvicorn app.main:app --reload",
       "start:frontend": "cd frontend && npm start"
     }
   }
   ```

3. Run both services:
   ```bash
   npm start
   ```

## Accessing the Application
- Backend Swagger Docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`

## Development Notes
- Backend uses FastAPI with async support
- Frontend uses React with Material-UI
- Real-time metrics updated via WebSocket and REST API

## API Endpoints
- `/machines`: List all machines
- `/machine/{machine_id}/metrics`: Get current machine metrics
- `/machine/{machine_id}/history`: Retrieve historical metrics
- `/machine/{machine_id}/analysis`: Perform comprehensive machine data analysis
- `/ws/machine/{machine_id}`: WebSocket for real-time updates

## Technologies
- FastAPI
- Prometheus
- Kafka
- Scikit-learn
- Pandas
- WebSockets

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.
