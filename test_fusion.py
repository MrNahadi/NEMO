import time
from pathlib import Path
from nemo.config import BASELINE_PARAMETERS_MM
from nemo.handshake import write_request, wait_for_response
from nemo.schemas import EvaluationRequest
from nemo.evaluation import make_run_id

def test_fusion_handshake():
    run_dir = Path("data/runs/active")
    run_dir.mkdir(parents=True, exist_ok=True)
    
    run_id = make_run_id()
    iteration = 1
    
    # Use baseline parameters, but let's change one to see Fusion update
    params = dict(BASELINE_PARAMETERS_MM)
    params["baseplate_length"] = 160.0  # Changed from 150.0 to verify update
    
    request = EvaluationRequest(
        run_id=run_id,
        iteration=iteration,
        mode="fusion",  # Fusion Add-in doesn't strictly check mode, but good practice
        parameters_mm=params
    )
    
    print(f"Writing request to {run_dir}/request.json...")
    write_request(run_dir, request)
    
    print("Waiting for Fusion 360 to process and write response.json (timeout=120s)...")
    try:
        response = wait_for_response(run_dir, run_id=run_id, iteration=iteration, timeout_s=120.0)
        print("\nSuccess! Received response from Fusion 360:")
        print(f"Status: {response.status}")
        print(f"Mass: {response.metrics.mass_kg} kg")
        if response.error:
            print(f"Message/Error: {response.error}")
    except TimeoutError as e:
        print(f"\nTimeout Error: {e}")
        print("Did you start the NEMOBridge Add-in in Fusion 360?")

if __name__ == "__main__":
    test_fusion_handshake()
