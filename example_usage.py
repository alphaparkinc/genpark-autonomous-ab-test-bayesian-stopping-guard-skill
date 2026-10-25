from client import AutonomousAbTestBayesianStoppingGuardClient
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

def main():
    guard = AutonomousAbTestBayesianStoppingGuardClient()
    print("=== AUTONOMOUS AB TEST BAYESIAN STOPPING GUARD ===")
    
    # Control: 8,400 views, 336 conversions (4.0%)
    # Variant: 8,450 views, 422 conversions (5.0%) -> +25% uplift
    res = guard.evaluate_experiment(8400, 336, 8450, 422)
    print()
    print(f"Control: {res['control_conversion_rate']*100:.2f}% | Variant: {res['variant_conversion_rate']*100:.2f}% (Uplift: +{res['relative_uplift_pct']}%)")
    print(f"P(Variant > Control): {res['probability_variant_beats_control']*100:.2f}% | Expected Loss: {res['expected_loss']}")
    print(f"Decision: {res['recommended_decision']}")
    print(f"Rationale: {res['decision_rationale']}")

if __name__ == "__main__":
    main()
