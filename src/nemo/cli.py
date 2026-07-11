"""Command-line entry point for the multi-part NEMO pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evaluation import evaluate_design, make_run_id
from .handshake import read_json, write_json_atomic
from .logger import append_evaluation, write_run_metadata
from .optimizers import optimize_analytical
from .parts import DEFAULT_PART_ID, get_part_definition, list_part_definitions
from .sampling import latin_hypercube_samples, random_samples
from .schemas import EvaluationRequest
from .validation import load_candidate_rows, select_validation_candidates, write_validation_package


PART_CHOICES = tuple(definition.part_id for definition in list_part_definitions())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NEMO multi-part marine optimizer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("parts", help="List registered part definitions")

    evaluate_parser = subparsers.add_parser("evaluate", help="Evaluate one design analytically")
    _add_part_argument(evaluate_parser)
    evaluate_parser.add_argument("--params-json", type=Path)
    evaluate_parser.add_argument("--output-json", type=Path)

    cad_parser = subparsers.add_parser("cad", help="Generate or update a native Fusion model")
    _add_part_argument(cad_parser)
    cad_parser.add_argument("--params-json", type=Path)
    cad_parser.add_argument(
        "--artifact",
        action="append",
        choices=("step", "stl", "boundary_tags"),
        default=[],
        help="Artifact to export; may be repeated",
    )
    cad_parser.add_argument("--output-json", type=Path)

    sample_parser = subparsers.add_parser("sample", help="Run analytical design-space sampling")
    _add_part_argument(sample_parser)
    sample_parser.add_argument("--count", type=int, default=60)
    sample_parser.add_argument("--method", choices=["latin", "random"], default="latin")
    sample_parser.add_argument("--seed", type=int, default=42)
    sample_parser.add_argument("--run-dir", type=Path)

    optimize_parser = subparsers.add_parser("optimize", help="Run bounded Nelder-Mead")
    _add_part_argument(optimize_parser)
    optimize_parser.add_argument("--max-iter", type=int, default=80)
    optimize_parser.add_argument("--run-dir", type=Path)
    optimize_parser.add_argument("--start-json", type=Path)
    optimize_parser.add_argument(
        "--mode",
        choices=["analytical", "fusion"],
        default="analytical",
        help="Fusion mode is CAD/mass-only until an FEA evaluator is configured",
    )

    package_parser = subparsers.add_parser(
        "validation-package",
        help="Create baseline plus analytical candidates for manual Fusion validation",
    )
    _add_part_argument(package_parser)
    package_parser.add_argument("csv_paths", nargs="+", type=Path)
    package_parser.add_argument("--count", type=int, default=5)
    package_parser.add_argument("--output-dir", type=Path, required=True)
    package_parser.add_argument("--min-fos", type=float)
    package_parser.add_argument("--max-deflection-mm", type=float)

    args = parser.parse_args(argv)
    commands = {
        "parts": _cmd_parts,
        "evaluate": _cmd_evaluate,
        "cad": _cmd_cad,
        "sample": _cmd_sample,
        "optimize": _cmd_optimize,
        "validation-package": _cmd_validation_package,
    }
    return commands[args.command](args)


def _add_part_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--part", choices=PART_CHOICES, default=DEFAULT_PART_ID)


def _cmd_parts(_args: argparse.Namespace) -> int:
    payload = []
    for definition in list_part_definitions():
        payload.append(
            {
                "part_id": definition.part_id,
                "name": definition.name,
                "material": definition.material.name,
                "parameter_count": len(definition.parameters),
                "parameters": [
                    {
                        "name": spec.name,
                        "unit": spec.unit,
                        "lower": spec.lower,
                        "upper": spec.upper,
                        "baseline": spec.baseline,
                    }
                    for spec in definition.parameters
                ],
            }
        )
    print(json.dumps(payload, indent=2))
    return 0


def _cmd_evaluate(args: argparse.Namespace) -> int:
    parameters = _load_parameters(args.params_json, args.part)
    response = evaluate_design(
        parameters,
        part_id=args.part,
        run_id=make_run_id(),
        iteration=0,
    )
    return _emit_response(response.to_dict(), args.output_json, response.status == "ok")


def _cmd_cad(args: argparse.Namespace) -> int:
    parameters = _load_parameters(args.params_json, args.part)
    artifacts = tuple(args.artifact or ("step", "boundary_tags"))
    response = evaluate_design(
        parameters,
        part_id=args.part,
        run_id=make_run_id(),
        iteration=0,
        mode="fusion_cad",
        artifact_formats=artifacts,
    )
    return _emit_response(response.to_dict(), args.output_json, response.status != "failed")


def _cmd_sample(args: argparse.Namespace) -> int:
    run_id = make_run_id()
    run_dir = args.run_dir or Path("data") / "runs" / f"{run_id}_{args.part}_sample"
    csv_path = run_dir / "results.csv"
    write_run_metadata(run_dir, part_id=args.part, run_id=run_id, run_type="sample")
    samples = (
        latin_hypercube_samples(args.count, seed=args.seed, part_id=args.part)
        if args.method == "latin"
        else random_samples(args.count, seed=args.seed, part_id=args.part)
    )
    for index, parameters in enumerate(samples):
        request = EvaluationRequest(
            run_id=run_id,
            iteration=index,
            mode="analytical",
            part_id=args.part,
            parameters=parameters,
        )
        response = evaluate_design(
            parameters,
            part_id=args.part,
            run_id=run_id,
            iteration=index,
        )
        append_evaluation(csv_path, request, response)
    print(f"Wrote {len(samples)} {args.part} evaluations to {csv_path}")
    return 0


def _cmd_optimize(args: argparse.Namespace) -> int:
    run_id = make_run_id()
    run_dir = args.run_dir or Path("data") / "runs" / f"{run_id}_{args.part}_optimize"
    csv_path = run_dir / "results.csv"
    write_run_metadata(run_dir, part_id=args.part, run_id=run_id, run_type="optimize")
    start_parameters = (
        _load_parameters(args.start_json, args.part) if args.start_json else None
    )
    result = optimize_analytical(
        part_id=args.part,
        run_id=run_id,
        start_parameters=start_parameters,
        max_iter=args.max_iter,
        output_csv=csv_path,
        mode=args.mode,
    )
    summary = {
        "schema_version": 2,
        "part_id": args.part,
        "run_id": run_id,
        "results_csv": str(csv_path),
        "best_objective": result.best_objective,
        "best_parameters": result.best_parameters,
        "evaluations": result.evaluations,
        "iterations": result.iterations,
    }
    write_json_atomic(run_dir / "optimization_summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


def _cmd_validation_package(args: argparse.Namespace) -> int:
    rows = load_candidate_rows(args.csv_paths)
    candidates = select_validation_candidates(
        rows,
        part_id=args.part,
        count=args.count,
        min_fos=args.min_fos,
        max_deflection_mm=args.max_deflection_mm,
    )
    write_validation_package(
        candidates,
        args.output_dir,
        part_id=args.part,
        min_fos=args.min_fos,
        max_deflection_mm=args.max_deflection_mm,
    )
    print(
        json.dumps(
            {
                "part_id": args.part,
                "output_dir": str(args.output_dir),
                "candidate_count": len(candidates),
                "candidates": [candidate["candidate_id"] for candidate in candidates],
            },
            indent=2,
        )
    )
    return 0


def _load_parameters(path: Path | None, part_id: str) -> dict[str, float]:
    definition = get_part_definition(part_id)
    if path is None:
        return dict(definition.baseline_parameters)
    payload = read_json(path)
    values = payload.get("parameters") or payload.get("parameters_mm") or payload
    return {str(key): float(value) for key, value in dict(values).items()}


def _emit_response(payload: dict, output: Path | None, success: bool) -> int:
    if output:
        write_json_atomic(output, payload)
    print(json.dumps(payload, indent=2))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
