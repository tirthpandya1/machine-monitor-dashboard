from kafka import KafkaProducer as BaseKafkaProducer
import json
from typing import Dict, Any

class KafkaProducer:
    def __init__(self, bootstrap_servers=['localhost:9092']):
        """
        Initialize Kafka Producer
        
        :param bootstrap_servers: List of Kafka bootstrap servers
        """
        try:
            self.producer = BaseKafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except Exception as e:
            print(f"Error initializing Kafka Producer: {e}")
            self.producer = None
    
    def send_machine_metrics(self, topic: str, machine_data: Dict[str, Any]):
        """
        Send machine metrics to a Kafka topic
        
        :param topic: Kafka topic name
        :param machine_data: Dictionary of machine metrics
        """
        if self.producer:
            try:
                self.producer.send(topic, machine_data)
                self.producer.flush()
            except Exception as e:
                print(f"Error sending message to Kafka: {e}")
    
    def close(self):
        """
        Close the Kafka producer connection
        """
        if self.producer:
            self.producer.close()
