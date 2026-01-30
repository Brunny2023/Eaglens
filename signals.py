from config import *

class NewsSignalEngine:
    CATEGORIES = {
        "LINEUP_AVAILABILITY": 0.12,
        "TACTICAL_MANAGERIAL": 0.10,
        "MOTIVATION_INCENTIVE": 0.06,
        "PSYCHOLOGICAL": 0.05,
        "EXTERNAL_CONDITIONS": 0.04,
        "MARKET_NOISE": 0.02
    }

    def calculate_nss(self, sr, ss, pi, tr):
        """Calculate News Signal Score: SR × SS × PI × TR."""
        return sr * ss * pi * tr

    def apply_signal_shift(self, base_probs, news_items):
        """Apply capped probability shifts based on news items."""
        shifted_probs = base_probs.copy()
        total_shift = 0
        
        for item in news_items:
            category = item.get("category")
            impact = item.get("impact")  # -1 to 1
            nss = self.calculate_nss(
                item.get("sr", 1), 
                item.get("ss", 1), 
                item.get("pi", 1), 
                item.get("tr", 1)
            )
            
            if category in self.CATEGORIES:
                max_shift = self.CATEGORIES[category]
                shift = max_shift * impact * nss
                
                # Apply shift to home/away and redistribute
                if shift > 0: # Favoring home
                    shifted_probs["home"] += shift
                    shifted_probs["away"] -= shift * 0.8
                    shifted_probs["draw"] -= shift * 0.2
                else: # Favoring away
                    shifted_probs["away"] += abs(shift)
                    shifted_probs["home"] -= abs(shift) * 0.8
                    shifted_probs["draw"] -= abs(shift) * 0.2
                
                total_shift += abs(shift)

        # Ensure probabilities are valid
        for k in shifted_probs:
            shifted_probs[k] = max(0.01, shifted_probs[k])
        
        total = sum(shifted_probs.values())
        for k in shifted_probs:
            shifted_probs[k] /= total
            
        return shifted_probs, total_shift

class AssumptionRegistry:
    def __init__(self):
        self.assumptions = {
            "home_advantage": {"status": "active", "weight": 1.0},
            "recent_form": {"status": "active", "weight": 1.0},
            "elo_predictive": {"status": "active", "weight": 1.0}
        }

    def update_assumption(self, name, performance_metric):
        """Reduce weight or deactivate assumption if performance degrades."""
        if name in self.assumptions:
            if performance_metric < 0.5:
                self.assumptions[name]["status"] = "weakening"
                self.assumptions[name]["weight"] *= 0.8
            elif performance_metric < 0.3:
                self.assumptions[name]["status"] = "degraded"
                self.assumptions[name]["weight"] = 0.5
