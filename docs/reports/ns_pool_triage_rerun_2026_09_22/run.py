import os
import importlib.util, os
from pathlib import Path
os.chdir(os.path.expanduser("~/claude_projects/gaia-recovered-2026-05-27"))
spec = importlib.util.spec_from_file_location("tri", "scripts/ns_pool_triage_2026_05_28.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.RESULTS_JSON = Path("/tmp/ns_triage_rerun_2026_09_22/results.json")
m.REPORT_MD = Path("/tmp/ns_triage_rerun_2026_09_22/report.md")
m.main()
print("TRIAGE_RERUN_DONE", flush=True)
