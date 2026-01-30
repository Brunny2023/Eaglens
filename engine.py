import numpy as np
import pandas as pd
from scipy.stats import poisson
from config import *

class EaglensEngine:
    def __init__(self):
        self.calibration_metrics = {
            "brier_score": 0.18,  # Initial healthy state
            "performance_drift": 0.05,
            "data_drift_psi": 0.10,
            "league_volatility": 1.1,
            "sample_size": 50
        }

    def calculate_poisson_probabilities(self, home_exp_goals, away_exp_goals, max_goals=10):
        """Calculate match outcome probabilities using Poisson distribution."""
        home_probs = [poisson.pmf(i, home_exp_goals) for i in range(max_goals)]
        away_probs = [poisson.pmf(i, away_exp_goals) for i in range(max_goals)]
        
        # Outer product to get score matrix
        score_matrix = np.outer(home_probs, away_probs)
        
        home_win = np.sum(np.tril(score_matrix, -1))
        draw = np.sum(np.diag(score_matrix))
        away_win = np.sum(np.triu(score_matrix, 1))
        
        # Normalize to ensure sum is 1
        total = home_win + draw + away_win
        return {
            "home": home_win / total,
            "draw": draw / total,
            "away": away_win / total
        }

    def compute_confidence(self, metrics):
        """Compute confidence score (0-100) based on multiple factors."""
        confidence = 85  # Base confidence
        
        # Adjust based on Brier Score
        if metrics["brier_score"] > 0.20:
            confidence -= 15
            
        # Adjust based on Performance Drift
        if metrics["performance_drift"] > 0.15:
            confidence -= 30
            
        # Adjust based on Data Drift
        if metrics["data_drift_psi"] > 0.25:
            confidence -= 20
            
        # Adjust based on League Volatility
        if metrics["league_volatility"] > 1.25:
            confidence = min(confidence, 40)
            
        # Adjust based on Sample Size
        if metrics["sample_size"] < 10:
            confidence = min(confidence, 35)
            
        return max(0, confidence)

    def check_gates(self, metrics):
        """Check if any hard gating rules are triggered."""
        if metrics["brier_score"] > BRIER_THRESHOLD:
            return False, "Calibration failure: Rolling Brier score exceeds threshold (0.23)."
        
        if metrics["performance_drift"] > PERFORMANCE_DRIFT_SUPPRESS:
            return False, "Performance degradation: Model accuracy has drifted significantly."
            
        if metrics["data_drift_psi"] > DATA_DRIFT_PSI_SUPPRESS:
            return False, "Data drift detected: Input distribution has shifted beyond reliability."
            
        if metrics["league_volatility"] > LEAGUE_VOLATILITY_SUPPRESS:
            return False, "Extreme volatility: League conditions are currently too unpredictable."
            
        if metrics["sample_size"] < MIN_SAMPLE_SIZE:
            return False, "Insufficient data: Not enough historical matches for a reliable prediction."
            
        return True, None

    def predict(self, home_team, away_team, home_exp_goals, away_exp_goals):
        """Main prediction entry point with gating and confidence calculation."""
        # 1. Check Gates
        is_reliable, reason = self.check_gates(self.calibration_metrics)
        if not is_reliable:
            return {
                "status": "suppressed",
                "reason": reason
            }
            
        # 2. Calculate Probabilities
        probs = self.calculate_poisson_probabilities(home_exp_goals, away_exp_goals)
        
        # 3. Compute Confidence
        confidence = self.compute_confidence(self.calibration_metrics)
        
        # 4. Determine Confidence Label
        if confidence >= CONFIDENCE_HIGH[0]:
            label = "High"
        elif confidence >= CONFIDENCE_MEDIUM[0]:
            label = "Medium"
        else:
            label = "Low"
            
        return {
            "status": "success",
            "home_team": home_team,
            "away_team": away_team,
            "probabilities": probs,
            "confidence": confidence,
            "confidence_label": label
        }

# Example usage
if __name__ == "__main__":
    engine = EaglensEngine()
    prediction = engine.predict("Arsenal", "Chelsea", 1.8, 1.2)
    print(prediction)
