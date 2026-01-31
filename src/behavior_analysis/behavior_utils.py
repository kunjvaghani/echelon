import time
import threading
import logging
import sys
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from scipy.stats import entropy

# Configure logging
logging.basicConfig(level=logging.WARNING) # Reduced logging
logger = logging.getLogger(__name__)

# --- In-Memory Storage (Proof of concept) ---

# --- Incremental Session Accumulator (Step 2: Real-time Accumulation) ---
class SessionAccumulator:
    def __init__(self):
        self.lock = threading.Lock()
        
        # Incremental Stats
        self.keystroke_count = 0
        self.dwell_sum = 0.0
        self.dwell_sq_sum = 0.0
        
        self.flight_sum = 0.0
        self.flight_sq_sum = 0.0
        self.last_key_time = None
        
        self.mouse_moves_count = 0
        self.velocity_sum = 0.0
        self.velocities = [] # Keep velocities for Entropy (hard to do incrementally)
        
        self.raw_events_count = 0
        
    def add_events(self, events):
        with self.lock:
            for e in events:
                self.raw_events_count += 1
                t = e.get('t', 0)
                
                if e['type'] == 'k':
                    self.keystroke_count += 1
                    # Dwell
                    d = e.get('d', 0)
                    self.dwell_sum += d
                    self.dwell_sq_sum += (d * d)
                    
                    # Flight (Time since last key)
                    if self.last_key_time is not None:
                        flight = t - self.last_key_time
                        # Filter typing breaks (> 2s)
                        if flight < 2000:
                            self.flight_sum += flight
                            self.flight_sq_sum += (flight * flight)
                    self.last_key_time = t
                    
                elif e['type'] == 'm':
                    self.mouse_moves_count += 1
                    v = e.get('v', 0)
                    self.velocity_sum += v
                    self.velocities.append(v)
                    
            # Cap memory for raw lists
            if len(self.velocities) > 1000:
                self.velocities = self.velocities[-1000:]

    def get_snapshot(self):
        with self.lock:
            # Calculate means and stds on the fly from sums
            stats = {
                'keystroke_count': self.keystroke_count,
                'mouse_moves_count': self.mouse_moves_count,
                'avg_dwell_time': 0.0,
                'dwell_time_std': 0.0,
                'avg_flight_time': 0.0,
                'flight_time_std': 0.0,
                'avg_mouse_velocity': 0.0,
                'velocity_entropy': 0.0
            }
            
            # Dwell Stats
            if self.keystroke_count > 0:
                stats['avg_dwell_time'] = self.dwell_sum / self.keystroke_count
                variance = (self.dwell_sq_sum / self.keystroke_count) - (stats['avg_dwell_time'] ** 2)
                stats['dwell_time_std'] = np.sqrt(max(0, variance))
                
            # Flight Stats (Note: flight count is approx keystroke_count - 1 - breaks)
            # Simplified: using approx count derived from logic would be complex count tracking
            # reusing keystroke_count for demonstration, strictly we should track flight_count separate
            # Let's trust that flight_sum > 0 implies valid flights
            if self.flight_sum > 0:
                 flight_count = max(1, self.keystroke_count - 1) # Approximation
                 stats['avg_flight_time'] = self.flight_sum / flight_count
                 variance_f = (self.flight_sq_sum / flight_count) - (stats['avg_flight_time'] ** 2)
                 stats['flight_time_std'] = np.sqrt(max(0, variance_f))

            # Mouse Stats
            if self.mouse_moves_count > 0:
                stats['avg_mouse_velocity'] = self.velocity_sum / self.mouse_moves_count
                
                if len(self.velocities) > 5:
                    hist, _ = np.histogram(self.velocities, bins=10, density=True)
                    stats['velocity_entropy'] = entropy(hist + 1e-10)
            
            return stats

# Global Storage: Map[session_id, SessionAccumulator]
BEHAVIOR_SESSIONS = {}

class BehaviorAnalyzer:
    def __init__(self):
        pass

    # --- Heuristic Baselines ---
    BASELINE_STATS = {
        'dwell_time': {'mean': 100.0, 'std': 30.0},
        'flight_time': {'mean': 150.0, 'std': 50.0},
        'mouse_velocity': {'mean': 0.5, 'std': 0.3},
        'velocity_entropy': {'mean': 2.0, 'std': 0.5}
    }

    def compute_z_score(self, value, baseline_key):
        base = self.BASELINE_STATS.get(baseline_key)
        if not base or base['std'] == 0:
            return 0.0
        return (value - base['mean']) / base['std']

    def calculate_risk_score(self, session_id):
        """
        Step 3 & 4: Submission-Time Final Aggregation & Evaluation
        """
        accumulator = BEHAVIOR_SESSIONS.get(session_id)
        if not accumulator or accumulator.raw_events_count == 0:
            return 0.5, "MANUAL_REVIEW", ["No behavioral data collected"]
            
        # Step 3: Final Aggregation (Snapshotted)
        features = accumulator.get_snapshot()
        
        # Step 4: Single Final Evaluation
        risk_score = 0.0
        reasons = []

        # 1. Typing Speed (Z-Score)
        if features['keystroke_count'] > 5:
            z_dwell = self.compute_z_score(features['avg_dwell_time'], 'dwell_time')
            if z_dwell < -2.5: 
                risk_score += 0.4
                reasons.append(f"Superhuman Typing Speed (Z={z_dwell:.1f})")

        # 2. Stability / Robotic (Variance)
        if features['keystroke_count'] > 5:
            if features['dwell_time_std'] < 5.0:
                risk_score += 0.5
                reasons.append("Robotic Key Press Consistency")
            
            if features['flight_time_std'] < 10.0 and features['avg_flight_time'] > 0:
                 risk_score += 0.3
                 reasons.append("Robotic Typing Rhythm")

        # 3. Mouse Entropy
        if features['mouse_moves_count'] > 10 and features['velocity_entropy'] < 0.5:
             risk_score += 0.4
             reasons.append("Unnatural Mouse Movement")

        # Step 5: Final Decision Logic
        risk_score = min(1.0, risk_score)
        
        if risk_score >= 0.75:
            decision = "REJECT"
        elif risk_score >= 0.35:
            decision = "MANUAL_REVIEW"
        else:
            decision = "ACCEPT"
            
        return risk_score, decision, reasons

class BehaviorServer:
    _instance = None
    _thread = None
    _app = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BehaviorServer, cls).__new__(cls)
            cls._instance._start_server()
        return cls._instance

    def _start_server(self):
        if self._thread and self._thread.is_alive():
            return

        self._app = Flask(__name__)
        CORS(self._app) 

        cli = sys.modules['flask.cli']
        cli.show_server_banner = lambda *x: None

        @self._app.route('/api/behavior', methods=['POST'])
        def receive_behavior():
            try:
                content = request.json
                session_id = content.get('session_id')
                events = content.get('events', [])
                
                if session_id:
                    if session_id not in BEHAVIOR_SESSIONS:
                        BEHAVIOR_SESSIONS[session_id] = SessionAccumulator()
                    
                    # Step 2: Real-Time Feature Accumulation
                    BEHAVIOR_SESSIONS[session_id].add_events(events)

                return jsonify({"status": "ok"}), 200
            except Exception as e:
                logger.error(f"Error in behavior API: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500

        def run_app():
            try:
                self._app.run(port=5001, debug=False, use_reloader=False)
            except Exception as e:
                logger.error(f"Failed to start Behavior Server: {e}")

        self._thread = threading.Thread(target=run_app, daemon=True)
        self._thread.start()
        logger.info("Behavior Analysis Background Server started on port 5001")


    def get_score(self, session_id):
        analyzer = BehaviorAnalyzer()
        return analyzer.calculate_risk_score(session_id)
