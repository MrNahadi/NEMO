import json
import os
from pathlib import Path

import pytest

from nemo.evaluation import make_run_id
from nemo.handshake import wait_for_response, write_request
from nemo.parts import get_part_definition
from nemo.sampling import latin_hypercube_samples
from nemo.schemas import EvaluationRequest


RUN_FUSION = os.environ.get("NEMO_FUSION_SMOKE") == "1"


@pytest.mark.fusion
@pytest.mark.skipif(not RUN_FUSION, reason="set NEMO_FUSION_SMOKE=1 with NEMOBridge running")
@pytest.mark.parametrize("part_id", ["bracket", "padeye", "stabilizer"])
def test_twenty_vector_fusion_geometry_sweep(part_id):
    definition = get_part_definition(part_id)
    vectors = [
        definition.baseline_parameters,
        *latin_hypercube_samples(20, seed=42, part_id=part_id),
    ]
    run_id = f"fusion_smoke_{part_id}_{make_run_id()}"
    handshake_dir = Path("data/runs/active")

    for iteration, parameters in enumerate(vectors):
        request = EvaluationRequest(
            run_id=run_id,
            iteration=iteration,
            mode="fusion_cad",
            part_id=part_id,
            parameters=parameters,
            artifact_formats=("step", "boundary_tags"),
        )
        write_request(handshake_dir, request)
        response = wait_for_response(
            handshake_dir,
            run_id=run_id,
            iteration=iteration,
            timeout_s=180.0,
        )
        assert response.status == "partial", response.error
        assert response.metrics.volume_m3 is not None
        assert response.metrics.volume_m3 > 0
        assert Path(response.artifacts["step"]).exists()
        boundary_path = Path(response.artifacts["boundary_tags"])
        assert boundary_path.exists()
        boundary_data = json.loads(boundary_path.read_text(encoding="utf-8"))
        for role in definition.boundary_tags:
            assert role in boundary_data["boundaries"]
            assert boundary_data["boundaries"][role]["faces"], (
                f"{part_id} boundary role {role!r} matched no faces"
            )
