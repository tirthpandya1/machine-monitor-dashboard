import pytest
from httpx import AsyncClient
from app.main import app, machine_monitor

def generate_test_data():
    """Ensure test data is generated for all machines."""
    for machine_id in machine_monitor.machines:
        # Clear existing data and generate new data
        machine_monitor.machines[machine_id] = []
        for _ in range(10):
            machine_monitor.generate_machine_data(machine_id)

@pytest.mark.asyncio
async def test_list_machines():
    """Test listing all machines."""
    generate_test_data()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/machines")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_get_machine_metrics():
    """Test retrieving metrics for a specific machine."""
    generate_test_data()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Assuming the first machine is named 'machine-0'
        response = await ac.get("/machine/machine-0/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "machine_id" in data
        assert "temperature" in data
        assert "cpu_usage" in data
        assert "memory_usage" in data
        assert "timestamp" in data

@pytest.mark.asyncio
async def test_get_machine_history():
    """Test retrieving historical metrics for a specific machine."""
    generate_test_data()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/machine/machine-0/history?limit=50")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 50
        
        # Check that each entry has the required fields
        for entry in data:
            assert "machine_id" in entry
            assert "temperature" in entry
            assert "cpu_usage" in entry
            assert "memory_usage" in entry
            assert "timestamp" in entry

@pytest.mark.asyncio
async def test_nonexistent_machine():
    """Test behavior when querying a non-existent machine."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/machine/nonexistent-machine/metrics")
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data

@pytest.mark.asyncio
async def test_machine_analysis():
    """Test machine data analysis endpoint."""
    generate_test_data()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/machine/machine-0/analysis")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check anomaly detection results
        assert "anomaly_detection" in data
        assert "total_records" in data["anomaly_detection"]
        assert "anomaly_count" in data["anomaly_detection"]
        assert "anomaly_percentage" in data["anomaly_detection"]
        
        # Check statistical summary
        assert "statistical_summary" in data
        assert "temperature" in data["statistical_summary"]
        assert "cpu_usage" in data["statistical_summary"]
        assert "memory_usage" in data["statistical_summary"]
        
        # Check trend prediction
        assert "trend_prediction" in data
        for metric in ["temperature", "cpu_usage", "memory_usage"]:
            assert metric in data["trend_prediction"]
            assert data["trend_prediction"][metric] in [
                "increasing", "decreasing", "stable", "insufficient_data"
            ]

@pytest.mark.asyncio
async def test_analysis_nonexistent_machine():
    """Test analysis endpoint for a non-existent machine."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/machine/nonexistent-machine/analysis")
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
