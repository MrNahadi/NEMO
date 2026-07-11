"""Diagnostic Fusion script for discovering text-command capabilities.

Run this from Fusion's Scripts and Add-Ins dialog. It writes command output to:

    data/runs/active/TextCommandProbe.log

The purpose is to see whether the installed Fusion build exposes any
Simulation/solve/result commands through Application.executeTextCommand().
"""

from __future__ import annotations

import os
import time
import traceback

import adsk.core


HANDSHAKE_DIR = "C:/Users/muigu/Documents/Projects/NEMO/data/runs/active"


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    log_path = os.path.join(HANDSHAKE_DIR, "TextCommandProbe.log")
    os.makedirs(HANDSHAKE_DIR, exist_ok=True)

    probes = [
        "Commands.List",
        "Command.List",
        "Commands",
        "TextCommands.List",
        "NuCommands.List",
        "Simulation.Solve",
        "Sim.Solve",
        "Solve",
        "Results",
    ]

    with open(log_path, "w", encoding="utf-8") as handle:
        handle.write(time.strftime("%Y-%m-%d %H:%M:%S"))
        handle.write(" Text command probe\n\n")
        for command in probes:
            handle.write(f"=== {command} ===\n")
            try:
                result = app.executeTextCommand(command)
                handle.write(str(result))
                handle.write("\n")
            except Exception:
                handle.write(traceback.format_exc())
            handle.write("\n")

    ui.messageBox(f"Text command probe complete.\n\nLog written to:\n{log_path}")
