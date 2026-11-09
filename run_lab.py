"""Reproduce all measured evidence; run with .venv/Scripts/python run_lab.py."""
from pathlib import Path
import json
import os
import platform
import subprocess
import sys
import time
import timeit
import statistics

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / 'reports'
REPORTS.mkdir(exist_ok=True)
PYTHON = sys.executable


def run(label, args, env=None):
    command = [PYTHON, *args]
    heading = f'Project: lab9_Omar_Khalil\nPS {ROOT}> python {" ".join(args)}\n\n'
    print(heading, flush=True)
    started = time.perf_counter()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                            env={**os.environ, **(env or {})})
    output = heading + result.stdout + result.stderr
    (REPORTS / f'{label}.txt').write_text(output, encoding='utf-8')
    print(f'{label}: exit {result.returncode}; wall {time.perf_counter()-started:.2f}s', flush=True)
    if result.returncode:
        raise RuntimeError(output)


def main():
    for suffix, module in [('before', 'profiler'), ('after', 'profiler_optimized')]:
        run(f'cprofile_{suffix}', ['-m', 'cProfile', '-s', 'time', f'{module}.py'])
        line = 'profiler_lineprofiler' + ('_optimized' if suffix == 'after' else '')
        run(f'line_{suffix}', [f'{line}.py'])
        memory = 'profiler_memoryprofiler' + ('_optimized' if suffix == 'after' else '')
        run(f'memory_{suffix}', ['-m', 'memory_profiler', f'{memory}.py'])
        test = 'test_profiler' + ('_optimized' if suffix == 'after' else '')
        env = {'COVERAGE_FILE': str(ROOT / f'.coverage_{suffix}')}
        run(f'tests_{suffix}', ['-m', 'coverage', 'run', '--branch', f'--source={module}', '-m', 'unittest', '-v', test], env)
        run(f'coverage_{suffix}', ['-m', 'coverage', 'report', '-m'], env)
        run(f'coverage_html_{suffix}', ['-m', 'coverage', 'html', '-d', f'htmlcov_{suffix}'], env)
        run(f'coverage_json_{suffix}', ['-m', 'coverage', 'json', '-o', f'reports/coverage_{suffix}.json'], env)
    import profiler
    import profiler_optimized as optimized
    metrics = {'python': sys.version, 'platform': platform.platform(), 'functions': {}}
    for name, old, new, count in [
        ('slow_function', profiler.slow_function, optimized.slow_function, 1),
        ('fast_function', profiler.fast_function, optimized.optimized_fast_function, 100000),
        ('memory_intensive_function', profiler.memory_intensive_function, optimized.memory_intensive_function, 1),
    ]:
        assert old() == new()
        before = statistics.median(timeit.repeat(old, repeat=5, number=count)) / count
        after_count = max(count, 100000)
        after = statistics.median(timeit.repeat(new, repeat=5, number=after_count)) / after_count
        metrics['functions'][name] = {'before_seconds': before, 'after_seconds': after, 'speedup': before/after}
    (REPORTS / 'benchmark.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
    run('installed_packages', ['-c', "import importlib.metadata as m; print(*sorted(d.metadata['Name']+'=='+d.version for d in m.distributions()), sep=chr(10))"])


if __name__ == '__main__':
    main()
