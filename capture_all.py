"""Rerun lab tools and take genuine console-window screenshots on Windows."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def capture(label, args, env=None):
    print('Capturing ' + label, flush=True)
    process = subprocess.Popen([
        'conhost.exe', sys.executable, str(ROOT/'capture_terminal.py'),
        label, json.dumps(args),
    ], cwd=ROOT, env={**os.environ, **(env or {})},
       creationflags=subprocess.CREATE_NEW_CONSOLE)
    if process.wait() != 0:
        raise RuntimeError(label + ' failed')
    data = json.loads((ROOT/'reports'/f'{label}.capture.json').read_text())
    if data['returncode'] != 0:
        raise RuntimeError(label + ' failed')
    print('Saved ' + ', '.join(data['images']), flush=True)


def main():
    for suffix, module in [('before', 'profiler'), ('after', 'profiler_optimized')]:
        capture(f'cprofile_{suffix}', ['-m', 'cProfile', '-s', 'time', f'{module}.py'])
        extra = '_optimized' if suffix == 'after' else ''
        capture(f'line_{suffix}', [f'profiler_lineprofiler{extra}.py'])
        capture(f'memory_{suffix}', ['-m', 'memory_profiler', f'profiler_memoryprofiler{extra}.py'])
        env = {'COVERAGE_FILE': str(ROOT/f'.coverage_{suffix}')}
        capture(f'tests_{suffix}', ['-m', 'coverage', 'run', '--branch', f'--source={module}',
                                   '-m', 'unittest', '-v', f'test_profiler{extra}'], env)
        capture(f'coverage_{suffix}', ['-m', 'coverage', 'report', '-m'], env)
        for args in [['-m', 'coverage', 'html', '-d', f'htmlcov_{suffix}'],
                     ['-m', 'coverage', 'json', '-o', f'reports/coverage_{suffix}.json']]:
            subprocess.run([sys.executable, *args], cwd=ROOT, env={**os.environ, **env}, check=True)


if __name__ == '__main__':
    main()
