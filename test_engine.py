from engine import EaglensEngine

def test_engine():
    engine = EaglensEngine()
    
    print("--- Test 1: Normal Prediction ---")
    res1 = engine.predict("Team A", "Team B", 1.5, 1.0)
    print(f"Status: {res1['status']}")
    if res1['status'] == 'success':
        print(f"Probs: {res1['probabilities']}")
        print(f"Confidence: {res1['confidence']} ({res1['confidence_label']})")
    
    print("\n--- Test 2: Gating (High Brier Score) ---")
    engine.calibration_metrics['brier_score'] = 0.25
    res2 = engine.predict("Team A", "Team B", 1.5, 1.0)
    print(f"Status: {res2['status']}")
    print(f"Reason: {res2.get('reason')}")
    
    print("\n--- Test 3: Low Confidence (Small Sample Size) ---")
    engine.calibration_metrics['brier_score'] = 0.18 # Reset
    engine.calibration_metrics['sample_size'] = 8
    res3 = engine.predict("Team A", "Team B", 1.5, 1.0)
    print(f"Status: {res3['status']}")
    print(f"Confidence: {res3['confidence']} ({res3['confidence_label']})")

if __name__ == "__main__":
    test_engine()
