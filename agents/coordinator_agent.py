"""
Coordinator Agent

This agent orchestrates all other agents in the pipeline.
It's the CENTRAL CONTROLLER of our Multi-Agent System.

Job: Initialize agents → Run pipeline → Handle errors → Return final results
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from datetime import datetime
from agents.base_agent import BaseAgent
from agents.collector_agent import DataCollectorAgent
from agents.processor_agent import DataProcessorAgent
from agents.classifier_agent import QualityClassifierAgent
from agents.advisor_agent import HealthAdvisorAgent


class CoordinatorAgent(BaseAgent):
    """
    Agent responsible for coordinating all other agents.
    """
    
    def __init__(self, target_cities=None):
        """
        Initialize the coordinator and all sub-agents.
        
        Args:
            target_cities: Optional list of cities to monitor
        """
        self.target_cities = target_cities
        
        # Initialize all agents
        self.collector = DataCollectorAgent(target_cities=target_cities)
        self.processor = DataProcessorAgent()
        self.classifier = QualityClassifierAgent()
        self.advisor = HealthAdvisorAgent()
        
        # Track pipeline status
        self.pipeline_status = {}
        
        super().__init__()
    
    def get_name(self):
        return "CoordinatorAgent"
    
    def run_pipeline(self):
        """
        Execute the full agent pipeline.
        
        Pipeline: Collector → Processor → Classifier → Advisor
        
        Returns:
            Dictionary with final results and metadata
        """
        self.log("Starting pipeline execution...")
        pipeline_start = datetime.now()
        
        # Reset status tracking
        self.pipeline_status = {
            "collector": "pending",
            "processor": "pending",
            "classifier": "pending",
            "advisor": "pending",
        }
        
        # Step 1: Collect data
        self.log("Step 1/4: Running Data Collector...")
        collector_result = self.collector.run()
        self.pipeline_status["collector"] = collector_result.status
        
        if collector_result.status != "success":
            self.log("ERROR: Pipeline failed at Collector stage")
            return {"status": "error", "failed_at": "collector", "data": None}
        
        # Step 2: Process data
        self.log("Step 2/4: Running Data Processor...")
        processor_result = self.processor.run(collector_result)
        self.pipeline_status["processor"] = processor_result.status
        
        if processor_result.status != "success":
            self.log("ERROR: Pipeline failed at Processor stage")
            return {"status": "error", "failed_at": "processor", "data": None}
        
        # Step 3: Classify data
        self.log("Step 3/4: Running Quality Classifier...")
        classifier_result = self.classifier.run(processor_result)
        self.pipeline_status["classifier"] = classifier_result.status
        
        if classifier_result.status != "success":
            self.log("ERROR: Pipeline failed at Classifier stage")
            return {"status": "error", "failed_at": "classifier", "data": None}
        
        # Step 4: Add health recommendations
        self.log("Step 4/4: Running Health Advisor...")
        advisor_result = self.advisor.run(classifier_result)
        self.pipeline_status["advisor"] = advisor_result.status
        
        if advisor_result.status != "success":
            self.log("ERROR: Pipeline failed at Advisor stage")
            return {"status": "error", "failed_at": "advisor", "data": None}
        
        # Calculate duration
        pipeline_duration = (datetime.now() - pipeline_start).total_seconds()
        self.log(f"Pipeline completed successfully in {pipeline_duration:.2f} seconds")
        
        # Return final results
        return {
            "status": "success",
            "data": advisor_result.data,
            "pipeline_status": self.pipeline_status,
            "duration_seconds": pipeline_duration,
            "timestamp": datetime.now().isoformat(),
        }
    
    def process(self, input_message=None):
        """
        Main processing method - runs the full pipeline.
        
        Returns:
            Message containing final results
        """
        result = self.run_pipeline()
        
        return self.create_message(
            data=result,
            status=result["status"]
        )


# Test the coordinator
if __name__ == "__main__":
    print("Testing Coordinator Agent...")
    print("=" * 50)
    print()
    
    # Create and run the coordinator
    coordinator = CoordinatorAgent()
    result = coordinator.run()
    
    print()
    print("=" * 50)
    print("FINAL RESULTS")
    print("=" * 50)
    
    if result.status == "success":
        data = result.data
        
        print(f"\nPipeline Status: {data['status']}")
        print(f"Duration: {data['duration_seconds']:.2f} seconds")
        print(f"Timestamp: {data['timestamp']}")
        
        print("\nAgent Status:")
        for agent, status in data['pipeline_status'].items():
            emoji = "✅" if status == "success" else "❌"
            print(f"  {emoji} {agent}: {status}")
        
        # Print the report
        print("\n" + data['data']['report'])
    else:
        print(f"\nPipeline failed!")
        print(f"Error: {result.data}")
