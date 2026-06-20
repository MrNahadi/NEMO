"""Command-line entry point for the external NEMO pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import BASELINE_PARAMETERS_MM
from .evaluation import evaluate_design, make_run_id
from .handshake import read_json, write_json_atomic
from .logger import append_evaluation
from .optimizers import optimize_analytical
from .sampling import latin_hypercube_samples, random_samples
from .schemas import EvaluationRequest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NEMO marine bracket optimizer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    evaluate_parser = subparsers.add_parser("evaluate", help="Evaluate one design analytically")
    evaluate_parser.add_argument("--params-json", type=Path)
    evaluate_parser.add_argument("--output-json", type=Path)

    sample_parser = subparsers.add_parser("sample", help="Run analytical design-space sampling")
    sample_parser.add_argument("--count", type=int, default=30)
    sample_parser.add_argument("--method", choices=["latin", "random"], default="latin")
    sample_parser.add_argument("--seed", type=int, default=42)
    sample_parser.add_argument("--run-dir", type=Path)

    optimize_parser = subparsers.add_parser("optimize", help="Run analytical Nelder-Mead")
    optimize_parser.add_argument("--max-iter", type=int, default=80)
    optimize_parser.add_argument("--run-dir", type=Path)

    args = parser.parse_args(argv)
    if args.command == "evaluate":
        return _cmd_evaluate(args)
    if args.command == "sample":
        return _cmd_sample(args)
    if args.command == "optimize":
        return _cmd_optimize(args)
    parser.error(f"Unknown command: {args.command}")
    return 2


def _cmd_evaluate(args: argparse.Namespace) -> int:
    parameters = dict(BASELINE_PARAMETERS_MM)
    if args.params_json:
        payload = read_json(args.params_json)
        parameters = {
            key: float(value)
            for key, value in payload.get("parameters_mm", payload).items()
        }

    response = evaluate_design(parameters, run_id=make_run_id(), iteration=0)
    payload = response.to_dict()
    if args.output_json:
        write_json_atomic(args.output_json, payload)
    print(json.dumps(payload, indent=2))
    return 0 if response.status == "ok" else 1


def _cmd_sample(args: argparse.Namespace) -> int:
    run_id = make_run_id()
    run_dir = args.run_dir or Path("data") / "runs" / f"{run_id}_sample"
    csv_path = run_dir / "results.csv"
    samples = (
        latin_hypercube_samples(args.count, seed=args.seed)
        if args.method == "latin"
        else random_samples(args.count, seed=args.seed)
    )

    for index, parameters in enumerate(samples):
        request = EvaluationRequest(
            run_id=run_id,
            iteration=index,
            mode="analytical",
            parameters_mm=parameters,
        )
        response = evaluate_design(parameters, run_id=run_id, iteration=index)
        append_evaluation(csv_path, request, response)

    print(f"Wrote {len(samples)} evaluations to {csv_path}")
    return 0


def _cmd_optimize(args: argparse.Namespace) -> int:
    run_id = make_run_id()
    run_dir = args.run_dir or Path("data") / "runs" / f"{run_id}_optimize"
    csv_path = run_dir / "results.csv"
    result = optimize_analytical(
        run_id=run_id,
        max_iter=args.max_iter,
        output_csv=csv_path,
    )
    summary = {
        "run_id": run_id,
        "results_csv": str(csv_path),
        "best_objective": result.best_objective,
        "best_parameters_mm": result.best_parameters_mm,
        "evaluations": result.evaluations,
        "iterations": result.iterations,
    }
    write_json_atomic(run_dir / "optimization_summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
