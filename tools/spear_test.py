"""Spearfishing adapter for the sibling RimWorldDevTests launcher.

Batch groups for the test tiers (AGENTS.md, "Test tiers"), on top of the launcher's own commands:

  run fast [--seed N] ...    the fast batches, in one launch of the default mod set
  run compat [--seed N] ...  each compat batch once under its own --mods, then a coverage summary
  run seam [--seed N] ...    run-all, then the compat batches, then a coverage summary

A case skipped in one run counts as covered only if it passed in another run of the same group (hygiene's Dubs Bad Hygiene
cases skip in run-all and pass under --mods dbh). Any case left not run anywhere is listed; it fails the seam tier.
"""
from pathlib import Path
import json
import os
import re
import runpy
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
HARNESS = Path(os.environ.get("RIMWORLD_DEV_TESTS_ROOT", str(ROOT.parent / "RimWorldDevTests")))
LAUNCHER = HARNESS / "rimtest.py"
CONFIG = ROOT / "DevTests" / "devtests.json"

# The ticket tier's fast batches: about a minute of a run-all between them (ticket 39).
FAST = ["spearfishing-zone", "spearfishing-reef", "spearfishing-fins", "spearfishing-trip", "spearfishing-catch-rate",
        "spearfishing-exits", "spearfishing-wide-zone", "spearfishing-gear", "spearfishing-buoy", "spearfishing-wetsuit",
        "spearfishing-hygiene", "spearfishing-recreation", "spearfishing-freshwater", "spearfishing-save-removal",
        "spearfishing-shark"]
# Each compat batch and the mod set it needs. None is mapped in devtests.json's batchModSets: run-all loads the union of every
# mapped set, so Odyssey would change every batch's fish and the waves-no-* settings would clash (ticket 39's Comments).
COMPAT = [("spearfishing-odyssey", "odyssey"), ("spearfishing-hygiene", "dbh"), ("spearfishing-living-waters", "living-waters"),
          ("spearfishing-waves-no-sea", "waves-no-sea"), ("spearfishing-waves-no-swimming-setting", "waves-no-swimming-setting"),
          ("spearfishing-waves-no-hooks", "waves-no-hooks"), ("spearfishing-waves-no-api", "waves-no-api")]
SEAM_TIMEOUT = "3600"
RUN_LINE = re.compile(r"^Run (\S+): evidence (.+)$")


def launch(args):
    """One launcher command in a child process, echoed as it runs. Returns the exit code and the run folders it reported."""
    child = subprocess.Popen([sys.executable, str(LAUNCHER), "--config", str(CONFIG)] + args,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    runs = []
    for line in child.stdout:
        print(line, end="", flush=True)
        match = RUN_LINE.match(line.strip())
        if match:
            runs.append(Path(match.group(2)))
    return child.wait(), runs


def summarise(results, strict=True):
    """Print each run's result and every skipped case, as not run unless it passed in another run of the group. Strict (the seam
    tier) fails on a case not run anywhere; compat alone only lists them, since its default-set cases run in run-all."""
    cases = []
    for label, code, runs in results:
        for run in runs:
            report = run / "report.json"
            data = json.loads(report.read_text(encoding="utf-8")) if report.is_file() else {}
            cases += [(label, c) for c in data.get("cases", []) if not c.get("Diagnostic")]
    passed = {c["Id"]: label for label, c in cases if c.get("Result") == "pass"}
    uncovered = []
    print("\nCoverage summary:")
    for label, code, runs in results:
        mine = [c for l, c in cases if l == label]
        counts = {r: sum(1 for c in mine if c.get("Result") == r) for r in ("pass", "fail", "error", "skip")}
        state = "PASS" if code == 0 else "FAIL" if code == 1 else f"stopped (exit {code})"
        print(f"  {label}: {state}; {counts['pass']} pass, {counts['fail']} fail, {counts['error']} error, {counts['skip']} not run"
              + ("" if runs else "; no run folder reported"))
        for c in (c for c in mine if c.get("Result") == "skip"):
            where = passed.get(c["Id"])
            note = f"passed in {where}" if where else "NOT COVERED"
            print(f"    not run: {c['Id']} [{c.get('CoverageReason') or 'unclassified'}] {c.get('Reason', '')} ({note})")
            if not where:
                uncovered.append(c["Id"])
    if uncovered:
        print(f"Not run anywhere, so not covered: {', '.join(sorted(set(uncovered)))}")
    worst = max((code for _, code, _ in results), default=4)
    return worst if worst != 0 else (1 if uncovered and strict else 0)


def compat(rest):
    return [(f"{batch} --mods {mods}", *launch(["run", batch, "--mods", mods] + rest)) for batch, mods in COMPAT]


def main(argv):
    if argv[:1] == ["promo"]:
        # Ticket 31's promo video: films through the launcher below, then edits (tools/promo.py).
        sys.path.insert(0, str(ROOT / "tools"))
        import promo
        return promo.main(argv[1:])
    if not LAUNCHER.is_file():
        sys.exit(f"shared harness not found: {LAUNCHER}; set RIMWORLD_DEV_TESTS_ROOT to its checkout")
    group = argv[1] if argv[:1] == ["run"] and len(argv) > 1 and argv[1] in ("fast", "compat", "seam") else None
    if group in ("compat", "seam"):
        rest = argv[2:]
        if "--mods" in rest:
            sys.exit(f"run {group} sets each batch's --mods itself")
        started = time.monotonic()
        results = []
        if group == "seam":
            timeout = [] if "--timeout" in rest else ["--timeout", SEAM_TIMEOUT]
            results.append(("run-all", *launch(["run", "run-all"] + timeout + rest)))
        results += compat(rest)
        code = summarise(results, strict=group == "seam")
        print(f"{group} tier: {'PASS' if code == 0 else 'FAIL'} in {time.monotonic() - started:.0f} s wall clock")
        return code
    if group == "fast":
        argv = ["run"] + FAST + argv[2:]
    sys.argv = [str(LAUNCHER), "--config", str(CONFIG)] + argv
    started = time.monotonic()
    try:
        runpy.run_path(str(LAUNCHER), run_name="__main__")
    finally:
        if group == "fast":
            print(f"fast tier: {time.monotonic() - started:.0f} s wall clock")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
