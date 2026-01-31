import time
import numpy as np

class BehaviorAnalyzer:
    def __init__(self):
        pass

    def capture_baseline(self, typing_data):
        """
        Analyzes registration behavior patterns.
        typing_data: list of timestamps or keystroke intervals
        """
        # TODO: Calculate Baseline Metrics
        # 1. Calculate 'Flight Time' (avg time between keypresses).
        # 2. Calculate 'Dwell Time' (avg time key is held down).
        # 3. Store the Mean and Standard Deviation.
        # Returns: A dictionary or serialized string of this baseline.
        return {"mean_flight_time": 0.15, "std_dev": 0.02}

    def detect_anomaly(self, current_data, baseline_data):
        """
        Compares current behavior against baseline.
        """
        # TODO: Implement Anomaly Detection
        # 1. Calculate stats for the current session (mean, std).
        # 2. Compare with baseline using Z-Score or simple threshold.
        #    z_score = (current_mean - baseline_mean) / baseline_std
        # 3. If z_score > 3 (3 sigma), flag as anomaly (bot behavior or different user).
        return {"deviation_score": 0.05, "is_anomaly": False}
