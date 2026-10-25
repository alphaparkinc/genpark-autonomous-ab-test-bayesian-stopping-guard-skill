import sys, json
from client import AutonomousAbTestBayesianStoppingGuardClient
sys.stdout.reconfigure(encoding='utf-8')

def handle_mcp():
    guard = AutonomousAbTestBayesianStoppingGuardClient()
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print(json.dumps({"status": "ready", "skill": "genpark-autonomous-ab-test-bayesian-stopping-guard-skill"}))
        return
    req = json.loads(sys.stdin.read() or "{}")
    c_v = int(req.get("control_views", 1000))
    c_c = int(req.get("control_conversions", 50))
    v_v = int(req.get("variant_views", 1000))
    v_c = int(req.get("variant_conversions", 65))
    res = guard.evaluate_experiment(c_v, c_c, v_v, v_c)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    handle_mcp()
