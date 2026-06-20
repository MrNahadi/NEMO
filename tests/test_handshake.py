import tempfile
import unittest
from pathlib import Path

from nemo.handshake import read_request, write_request, write_response, read_response
from nemo.schemas import EvaluationRequest, EvaluationResponse, Metrics


class HandshakeTests(unittest.TestCase):
    def test_request_and_response_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            request = EvaluationRequest(
                run_id="test",
                iteration=1,
                mode="analytical",
                parameters_mm={"baseplate_length": 150.0},
            )
            response = EvaluationResponse(
                run_id="test",
                iteration=1,
                status="ok",
                metrics=Metrics(1.0, 2.0, 3.0, 4.0, 5.0),
                error=None,
            )

            request_path = write_request(run_dir, request)
            response_path = write_response(run_dir, response)

            self.assertEqual(read_request(request_path), request)
            self.assertEqual(read_response(response_path), response)


if __name__ == "__main__":
    unittest.main()
