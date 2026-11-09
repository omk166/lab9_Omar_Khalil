# Lab 9: Profiling in Python

**Omar Khalil** — GitHub: **omk166** — solo submission.

Original and optimized implementations, cProfile, line_profiler, memory_profiler,
unit tests, HTML coverage reports, and the combined Word report.

## Run

```powershell
python -m venv .venv
python -m pip --python .venv install -r requirements.txt
.\.venv\Scripts\python run_lab.py
.\.venv\Scripts\python build_report.py
```

The original workload retains all 10,000,000 iterations. Line-level memory
profiling can take substantially longer than normal execution.

## Deliverables

- `profiler.py`, `profiler_lineprofiler.py`, `profiler_memoryprofiler.py`, `test_profiler.py`: original version.
- Corresponding `_optimized.py` files: optimized version.
- `lab9_Omar_Khalil.docx`: combined analysis and before/after terminal-output snapshots.
- `reports/`: actual command logs, rendered transcript images, and benchmark measurements.
- `htmlcov_before/index.html`, `htmlcov_after/index.html`: coverage, with supporting assets.
- `github_repo_link.txt`: upload this text file to Moodle.

Snapshots are rendered from real command transcripts and labeled with the project
identifier, rather than desktop screen captures. The formula preserves returned
results; removing the artificial sleep intentionally changes timing behavior.
The original loop already uses low auxiliary memory, so no guaranteed RSS
reduction is claimed. The Word report explains the corrected memory assertion
and the unit-test coverage gaps.
