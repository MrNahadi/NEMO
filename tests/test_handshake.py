import tempfile
import unittest
from pathlib import Path
from unittest import mock

from nemo.handshake import (
    read_request,
    read_response,
    serialized_fusion_channel,
    wait_for_response,
    write_request,
    write_response,
)
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

    def test_atomic_write_retries_windows_replace_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            response = EvaluationResponse(
                run_id="retry",
                iteration=0,
                status="ok",
                metrics=Metrics(1.0, 2.0, 3.0, 4.0, 5.0),
            )
            real_replace = __import__("os").replace
            attempts = 0

            def flaky_replace(source, target):
                nonlocal attempts
                attempts += 1
                if attempts == 1:
                    raise PermissionError("response.json is temporarily locked")
                return real_replace(source, target)

            with (
                mock.patch(
                    "nemo.handshake.os.replace",
                    side_effect=flaky_replace,
                ),
                mock.patch("nemo.handshake.time.sleep"),
            ):
                path = write_response(run_dir, response)

            self.assertEqual(attempts, 2)
            self.assertEqual(read_response(path), response)

    def test_timeout_reports_request_and_stale_response_state(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            request = EvaluationRequest(
                run_id="wanted",
                iteration=2,
                mode="analytical",
                parameters_mm={"baseplate_length": 150.0},
            )
            stale = EvaluationResponse(
                run_id="stale",
                iteration=1,
                status="ok",
                metrics=Metrics(1.0, 2.0, 3.0, 4.0, 5.0),
            )
            write_request(run_dir, request)
            write_response(run_dir, stale)

            with self.assertRaisesRegex(
                TimeoutError,
                "last observed response=run_id=stale iteration=1 status=ok",
            ) as raised:
                wait_for_response(
                    run_dir,
                    run_id="wanted",
                    iteration=2,
                    timeout_s=0.02,
                    poll_s=0.005,
                )

            self.assertIn("request.json exists", str(raised.exception))
            self.assertIn("response.json exists", str(raised.exception))

    def test_shared_fusion_channel_lock_is_exclusive(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with serialized_fusion_channel(temp_dir, timeout_s=0.1):
                with self.assertRaisesRegex(
                    TimeoutError, "serialized Fusion channel lock"
                ):
                    with serialized_fusion_channel(
                        temp_dir,
                        timeout_s=0.02,
                        poll_s=0.005,
                    ):
                        pass


if __name__ == "__main__":
    unittest.main()
