import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Any

class MachineDataAnalyzer:
    def __init__(self, contamination=0.01):
        """
        Initialize the data analyzer with configurable anomaly detection parameters
        
        :param contamination: Expected proportion of outliers in the dataset
        """
        self.isolation_forest = IsolationForest(
            contamination=contamination, 
            random_state=42
        )
    
    def detect_anomalies(self, machine_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect anomalies in machine metrics using Isolation Forest
        
        :param machine_data: List of machine data dictionaries
        :return: Anomaly detection results
        """
        if not machine_data:
            return {
                "total_records": 0,
                "anomaly_count": 0,
                "anomaly_percentage": 0,
                "anomalies": []
            }
        
        # Convert data to DataFrame for easier processing
        df = pd.DataFrame(machine_data)
        
        # If only one data point, return it as a non-anomalous record
        if len(df) == 1:
            return {
                "total_records": 1,
                "anomaly_count": 0,
                "anomaly_percentage": 0,
                "anomalies": []
            }
        
        # Select numeric columns for anomaly detection
        numeric_columns = ['temperature', 'cpu_usage', 'memory_usage']
        
        # Prepare data for Isolation Forest
        X = df[numeric_columns]
        
        try:
            # Fit and predict anomalies
            anomaly_labels = self.isolation_forest.fit_predict(X)
            
            # Identify anomalous records
            anomalies = df[anomaly_labels == -1]
            
            # Additional strict filtering
            def is_extreme_value(row):
                for col in numeric_columns:
                    # Check if value is beyond 3 standard deviations
                    mean = df[col].mean()
                    std = df[col].std()
                    if abs(row[col] - mean) > 3 * std:
                        return True
                return False
            
            strict_anomalies = anomalies[anomalies.apply(is_extreme_value, axis=1)]
            
            return {
                "total_records": len(df),
                "anomaly_count": len(strict_anomalies),
                "anomaly_percentage": len(strict_anomalies) / len(df) * 100,
                "anomalies": strict_anomalies.to_dict(orient='records')
            }
        except Exception as e:
            print(f"Error detecting anomalies: {e}")
            return {
                "total_records": len(df),
                "anomaly_count": 0,
                "anomaly_percentage": 0,
                "anomalies": [],
                "error": str(e)
            }
    
    def generate_statistical_summary(self, machine_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """
        Generate statistical summary of machine metrics
        
        :param machine_data: List of machine data dictionaries
        :return: Statistical summary of metrics
        """
        if not machine_data:
            return {
                "temperature": {},
                "cpu_usage": {},
                "memory_usage": {}
            }
        
        # Convert data to DataFrame
        df = pd.DataFrame(machine_data)
        
        # Compute statistical summary
        summary = {}
        for metric in ['temperature', 'cpu_usage', 'memory_usage']:
            summary[metric] = {
                "mean": float(df[metric].mean()),
                "median": float(df[metric].median()),
                "std": float(df[metric].std()),
                "min": float(df[metric].min()),
                "max": float(df[metric].max())
            }
        
        return summary
    
    def predict_trend(self, machine_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Predict trends for machine metrics
        
        :param machine_data: List of machine data dictionaries
        :return: Trend predictions for each metric
        """
        if len(machine_data) < 2:
            return {
                "temperature": "insufficient_data",
                "cpu_usage": "insufficient_data",
                "memory_usage": "insufficient_data"
            }
        
        # Convert data to DataFrame and sort by timestamp
        df = pd.DataFrame(machine_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Compute trend for each metric
        trends = {}
        for metric in ['temperature', 'cpu_usage', 'memory_usage']:
            # Linear regression to determine trend
            trend_line = np.polyfit(range(len(df)), df[metric], 1)
            slope = trend_line[0]
            
            # Classify trend based on slope
            if abs(slope) < 0.1:  # Very small slope considered stable
                trends[metric] = "stable"
            elif slope > 0:
                trends[metric] = "increasing"
            else:
                trends[metric] = "decreasing"
        
        return trends
