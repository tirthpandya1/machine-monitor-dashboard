import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from datetime import datetime, timedelta
from app.data_analysis import MachineDataAnalyzer

def generate_sample_machine_data(num_samples=10):
    """Generate sample machine data for testing"""
    return [
        {
            "machine_id": f"machine_{i}",
            "timestamp": datetime.now() - timedelta(minutes=num_samples - i),
            "temperature": 30 + i * 0.5,
            "cpu_usage": 20 + i,
            "memory_usage": 40 + i * 2
        }
        for i in range(num_samples)
    ]

def test_anomaly_detection():
    """Test anomaly detection functionality"""
    analyzer = MachineDataAnalyzer(contamination=0.1)
    machine_data = generate_sample_machine_data()
    
    result = analyzer.detect_anomalies(machine_data)
    
    assert "total_records" in result
    assert "anomaly_count" in result
    assert "anomaly_percentage" in result
    assert "anomalies" in result
    assert result["total_records"] == 10

def test_statistical_summary():
    """Test statistical summary generation"""
    analyzer = MachineDataAnalyzer()
    machine_data = generate_sample_machine_data()
    
    summary = analyzer.generate_statistical_summary(machine_data)
    
    assert "temperature" in summary
    assert "cpu_usage" in summary
    assert "memory_usage" in summary
    
    for metric in summary:
        assert all(key in summary[metric] for key in ["mean", "median", "std", "min", "max"])

def test_trend_prediction():
    """Test trend prediction functionality"""
    analyzer = MachineDataAnalyzer()
    machine_data = generate_sample_machine_data()
    
    trends = analyzer.predict_trend(machine_data)
    
    assert "temperature" in trends
    assert "cpu_usage" in trends
    assert "memory_usage" in trends
    
    # Expect increasing trend due to data generation method
    assert trends["temperature"] == "increasing"
    assert trends["cpu_usage"] == "increasing"
    assert trends["memory_usage"] == "increasing"

def test_empty_data_handling():
    """Test handling of empty or insufficient data"""
    analyzer = MachineDataAnalyzer()
    
    # Test empty list
    empty_result = analyzer.detect_anomalies([])
    assert empty_result["total_records"] == 0
    
    # Test single data point
    single_point_result = analyzer.detect_anomalies([generate_sample_machine_data(1)[0]])
    assert single_point_result["total_records"] == 1
    assert single_point_result["anomaly_count"] == 0
