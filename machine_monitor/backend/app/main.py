import asyncio
import random
import socket
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import prometheus_client
from prometheus_client import Counter, Gauge
import logging

from app.config import settings
# from app.kafka_producer import KafkaProducer
from app.data_analysis import MachineDataAnalyzer

# Prometheus Metrics
MACHINE_TEMPERATURE = Gauge(
    'machine_temperature', 
    'Temperature of the machine', 
    ['machine_id']
)
MACHINE_CPU_USAGE = Gauge(
    'machine_cpu_usage', 
    'CPU usage of the machine', 
    ['machine_id']
)
MACHINE_MEMORY_USAGE = Gauge(
    'machine_memory_usage', 
    'Memory usage of the machine', 
    ['machine_id']
)

class MachineData(BaseModel):
    machine_id: str
    temperature: float
    cpu_usage: float
    memory_usage: float
    timestamp: datetime
    human_timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))
    
    def format_timestamp(self, relative: bool = False) -> str:
        """
        Generate a human-friendly timestamp
        
        :param relative: If True, return relative time (e.g., '2 hours ago')
        :return: Formatted timestamp string
        """
        now = datetime.now()
        
        if relative:
            diff = now - self.timestamp
            
            # Less than a minute ago
            if diff < timedelta(minutes=1):
                return "just now"
            
            # Less than an hour ago
            if diff < timedelta(hours=1):
                minutes = int(diff.total_seconds() / 60)
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            
            # Less than a day ago
            if diff < timedelta(days=1):
                hours = int(diff.total_seconds() / 3600)
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            
            # More than a day ago
            days = int(diff.total_seconds() / (24 * 3600))
            return f"{days} day{'s' if days > 1 else ''} ago"
        
        # Default absolute timestamp
        return self.timestamp.strftime("%Y-%m-%d %I:%M:%S %p")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }

class MachineMonitor:
    def __init__(self):
        self.machines: Dict[str, List[MachineData]] = {}
        # self.kafka_producer = KafkaProducer()
        self.data_analyzer = MachineDataAnalyzer()
        
        # Initialize machines
        for i in range(settings.NUM_MACHINES):
            machine_id = f"machine-{i}"
            self.machines[machine_id] = []
    
    def generate_machine_data(self, machine_id: str) -> MachineData:
        """Generate mock machine data with more realistic and varied constraints."""
        # Machine-specific baseline and variation
        machine_baselines = {
            'machine-0': {  # Server
                'temp_base': 50, 'temp_var': 15,
                'cpu_base': 40, 'cpu_var': 30,
                'mem_base': 60, 'mem_var': 20
            },
            'machine-1': {  # High-performance workstation
                'temp_base': 65, 'temp_var': 10,
                'cpu_base': 70, 'cpu_var': 25,
                'mem_base': 75, 'mem_var': 15
            },
            'machine-2': {  # Edge device
                'temp_base': 40, 'temp_var': 5,
                'cpu_base': 20, 'cpu_var': 15,
                'mem_base': 40, 'mem_var': 10
            }
        }

        # Get machine-specific baseline
        baseline = machine_baselines.get(machine_id, {
            'temp_base': 50, 'temp_var': 15,
            'cpu_base': 50, 'cpu_var': 25,
            'mem_base': 50, 'mem_var': 20
        })

        # Introduce more realistic randomness with machine-specific variations
        data = MachineData(
            machine_id=machine_id,
            temperature=round(
                baseline['temp_base'] + random.uniform(-baseline['temp_var'], baseline['temp_var']), 
                2
            ),
            cpu_usage=round(
                baseline['cpu_base'] + random.uniform(-baseline['cpu_var'], baseline['cpu_var']), 
                2
            ),
            memory_usage=round(
                baseline['mem_base'] + random.uniform(-baseline['mem_var'], baseline['mem_var']), 
                2
            ),
            timestamp=datetime.now()
        )
        
        # Clamp values to realistic ranges
        data.temperature = max(30, min(data.temperature, 95))
        data.cpu_usage = max(0, min(data.cpu_usage, 100))
        data.memory_usage = max(0, min(data.memory_usage, 100))
        
        # Update Prometheus metrics
        MACHINE_TEMPERATURE.labels(machine_id=machine_id).set(data.temperature)
        MACHINE_CPU_USAGE.labels(machine_id=machine_id).set(data.cpu_usage)
        MACHINE_MEMORY_USAGE.labels(machine_id=machine_id).set(data.memory_usage)
        
        # Append data to machine's data list
        self.machines[machine_id].append(data)
        
        return data
    
    async def start_data_generation(self):
        """Continuously generate and publish machine data."""
        while True:
            for machine_id in self.machines.keys():
                # Generate new data
                data = self.generate_machine_data(machine_id)
                
                # Limit historical data
                self.machines[machine_id] = self.machines[machine_id][-1000:]
                
                # self.kafka_producer.publish(
                #     settings.KAFKA_TOPIC_MACHINE_METRICS, 
                #     data.model_dump_json()
                # )
            
            # Wait before next update
            await asyncio.sleep(settings.METRICS_UPDATE_INTERVAL)

    def analyze_machine_data(self, machine_id: str):
        """
        Perform comprehensive data analysis for a specific machine
        
        :param machine_id: ID of the machine to analyze
        :return: Dictionary with analysis results
        """
        if machine_id not in self.machines:
            return {"error": f"No data available for machine {machine_id}"}
        
        machine_data = self.machines[machine_id]
        
        # Convert Pydantic models to dictionaries
        machine_data_dicts = [
            {
                "machine_id": data.machine_id,
                "temperature": data.temperature,
                "cpu_usage": data.cpu_usage,
                "memory_usage": data.memory_usage,
                "timestamp": data.timestamp
            } for data in machine_data
        ]
        
        # If no data, return error
        if not machine_data_dicts:
            return {"error": f"No data available for machine {machine_id}"}
        
        return {
            "anomaly_detection": self.data_analyzer.detect_anomalies(machine_data_dicts),
            "statistical_summary": self.data_analyzer.generate_statistical_summary(machine_data_dicts),
            "trend_prediction": self.data_analyzer.predict_trend(machine_data_dicts)
        }

async def retrieve_machine_metrics(
    machine_ids: Optional[List[str]] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> List[MachineData]:
    """
    Retrieve machine metrics based on optional filters
    
    :param machine_ids: Optional list of machine IDs to retrieve
    :param start_time: Optional start time for retrieval
    :param end_time: Optional end time for retrieval
    :return: List of machine metrics
    """
    machine_monitor = MachineMonitor()
    machine_metrics = []
    
    for machine_id in machine_monitor.machines.keys():
        if machine_ids and machine_id not in machine_ids:
            continue
        
        machine_data = machine_monitor.machines[machine_id]
        
        if start_time or end_time:
            filtered_data = []
            for data in machine_data:
                if (not start_time or data.timestamp >= start_time) and (not end_time or data.timestamp <= end_time):
                    filtered_data.append(data)
            machine_data = filtered_data
        
        machine_metrics.extend(machine_data)
    
    return machine_metrics

# FastAPI Application
app = FastAPI(
    title="Machine Monitor API",
    description="Real-time machine monitoring system",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global machine monitor instance
machine_monitor = MachineMonitor()

def find_free_port(start_port=9090, max_attempts=10):
    """Find a free port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find a free port between {start_port} and {start_port + max_attempts}")

@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup."""
    # Manually generate initial data for each machine
    for machine_id in machine_monitor.machines:
        # Ensure at least 10 data points for each machine
        while len(machine_monitor.machines[machine_id]) < 10:
            machine_monitor.generate_machine_data(machine_id)
    
    asyncio.create_task(machine_monitor.start_data_generation())
    
    # Start Prometheus metrics server with port fallback
    try:
        metrics_port = find_free_port()
        print(f"Starting Prometheus metrics server on port {metrics_port}")
        prometheus_client.start_http_server(metrics_port)
    except Exception as e:
        print(f"Failed to start Prometheus metrics server: {e}")

@app.get("/machines")
async def list_machines():
    """List all monitored machines."""
    return list(machine_monitor.machines.keys())

@app.get("/machine/{machine_id}/metrics")
async def get_machine_metrics(machine_id: str):
    """Get the latest metrics for a specific machine."""
    if machine_id not in machine_monitor.machines:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    machine_data = machine_monitor.machines[machine_id]
    
    # If no data, generate some
    if not machine_data:
        machine_monitor.generate_machine_data(machine_id)
        machine_data = machine_monitor.machines[machine_id]
    
    return machine_data[-1]

@app.get("/machine/{machine_id}/history")
async def get_machine_history(machine_id: str, limit: int = 100):
    """Get historical metrics for a specific machine."""
    if machine_id not in machine_monitor.machines:
        return {"error": "Machine not found"}
    
    machine_data = machine_monitor.machines[machine_id]
    
    # If no data, generate some
    if not machine_data:
        for _ in range(10):
            machine_monitor.generate_machine_data(machine_id)
        machine_data = machine_monitor.machines[machine_id]
    
    return machine_data[-limit:]

@app.get("/machine/{machine_id}/analysis")
@app.get("/machines/{machine_id}/analysis")
async def get_machine_analysis(machine_id: str):
    """
    Perform comprehensive data analysis for a specific machine
    
    :param machine_id: ID of the machine to analyze
    :return: Dictionary with analysis results
    """
    try:
        # Ensure the machine exists
        if machine_id not in machine_monitor.machines:
            # Check if machine might not exist due to 0-based or 1-based indexing
            potential_machine_ids = [
                f"machine-{machine_id}",
                f"machine-{int(machine_id)-1}",
                f"machine-{int(machine_id)+1}"
            ]
            
            for potential_id in potential_machine_ids:
                if potential_id in machine_monitor.machines:
                    machine_id = potential_id
                    break
            else:
                raise HTTPException(status_code=404, detail=f"Machine {machine_id} not found")
        
        # Get machine data
        machine_data = machine_monitor.machines.get(machine_id, [])
        
        # If no data, generate some
        if not machine_data:
            machine_monitor.generate_machine_data(machine_id)
            machine_data = machine_monitor.machines[machine_id]
        
        # Perform analysis
        analysis_result = machine_monitor.analyze_machine_data(machine_id)
        
        return analysis_result
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid machine ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis")
async def get_multi_machine_analysis(
    machine_ids: Optional[List[str]] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None)
):
    """
    Perform comprehensive machine data analysis
    
    :param machine_ids: Optional list of machine IDs to analyze
    :param start_time: Optional start time for analysis
    :param end_time: Optional end time for analysis
    :return: Comprehensive machine metrics analysis
    """
    try:
        # If no machine_ids specified, use all machines
        if not machine_ids:
            machine_ids = list(machine_monitor.machines.keys())
        
        # Validate machine_ids
        invalid_machines = [mid for mid in machine_ids if mid not in machine_monitor.machines]
        if invalid_machines:
            raise HTTPException(status_code=404, detail=f"Invalid machine IDs: {invalid_machines}")
        
        # Perform analysis for each machine
        analysis_results = {}
        for machine_id in machine_ids:
            # Retrieve machine data with optional time filtering
            machine_data = machine_monitor.machines[machine_id]
            
            if start_time:
                machine_data = [data for data in machine_data if data.timestamp >= start_time]
            
            if end_time:
                machine_data = [data for data in machine_data if data.timestamp <= end_time]
            
            # Skip if no data after filtering
            if not machine_data:
                continue
            
            # Perform analysis
            analysis_results[machine_id] = machine_monitor.analyze_machine_data(machine_id)
        
        return analysis_results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/machine/{machine_id}")
async def websocket_machine_metrics(websocket: WebSocket, machine_id: str):
    """WebSocket endpoint for real-time machine metrics."""
    await websocket.accept()
    
    try:
        while True:
            # Get latest machine data
            if machine_id in machine_monitor.machines:
                machine_data = machine_monitor.machines[machine_id]
                
                # If no data, generate some
                if not machine_data:
                    for _ in range(10):
                        machine_monitor.generate_machine_data(machine_id)
                    machine_data = machine_monitor.machines[machine_id]
                
                latest_data = machine_data[-1]
                await websocket.send_json(latest_data.dict())
            
            # Wait before next update
            await asyncio.sleep(settings.METRICS_UPDATE_INTERVAL)
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for machine {machine_id}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )
