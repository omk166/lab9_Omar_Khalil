"""Build a Word report from real logs; images faithfully render those logs."""
from pathlib import Path
import json
import re
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / 'reports'


def snapshots(path):
    # These are transcript renders, not photographs of a terminal window.
    lines = ['Project: lab9_Omar_Khalil | Omar Khalil', *path.read_text(encoding='utf-8').rstrip().splitlines()]
    font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 15)
    images = []
    for page, start in enumerate(range(0, len(lines), 48), 1):
        chunk = lines[start:start+48]
        width = max(1000, int(max(font.getlength(line) for line in chunk)) + 40)
        canvas = Image.new('RGB', (width, 26 + len(chunk)*21), '#102030')
        draw = ImageDraw.Draw(canvas)
        for i, line in enumerate(chunk):
            draw.text((18, 12+i*21), line, font=font, fill='#ecf2f7')
        dest = REPORTS / f'{path.stem}_{page}.png'
        canvas.save(dest)
        images.append(dest)
    return images


def main():
    metrics = json.loads((REPORTS/'benchmark.json').read_text())
    doc = Document()
    doc.add_heading('Lab 9: Profiling in Python', 0)
    doc.add_paragraph('Omar Khalil | GitHub: omk166 | Solo submission')
    doc.add_paragraph('Repository: https://github.com/omk166/lab9_Omar_Khalil')
    doc.add_heading('Environment and method', 1)
    doc.add_paragraph(metrics['python'] + '\n' + metrics['platform'])
    doc.add_paragraph('The original workload uses 10,000, 100, and 10,000,000 iterations, respectively. '
                      'All profiling runs use the full workload. Raw command outputs are in reports/. '
                      'The snapshots below are faithful rendered terminal transcripts from those outputs, '
                      'with the required project identifier; they are not desktop screen captures. '
                      'Package versions are recorded in requirements.txt. Timing comparisons use perf_counter/timeit '
                      'without instrumentation: medians of five repeats, with repeated calls for very short functions.')
    doc.add_heading('Changes and correctness', 1)
    doc.add_paragraph('The handout contains duplicated fragments and damaged indentation, which were repaired. '
                      'The original implementation is preserved in profiler.py. Optimized code uses '
                      'n(n-1)(2n-1)/6 for the sum of squares over range(n), replacing each loop. '
                      'fast_function is replaced by optimized_fast_function in every optimized runner and test. '
                      'The two-second sleep is removed because it does not change the returned sum. '
                      'If a real application requires a delay, removing it would not preserve that timing contract. '
                      'All three exact results are tested, and the formula is independently checked against a loop for six sizes.')
    doc.add_heading('Uninstrumented performance comparison', 1)
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Light Shading Accent 1'
    for c, text in zip(table.rows[0].cells, ['Function', 'Before (s/call)', 'After (s/call)', 'Speedup']):
        c.text = text
    for name, result in metrics['functions'].items():
        cells = table.add_row().cells
        for cell, text in zip(cells, [name, f"{result['before_seconds']:.9g}", f"{result['after_seconds']:.9g}", f"{result['speedup']:.2f}x"]):
            cell.text = text
    doc.add_paragraph('Speedups are specific to this machine. Each original sum takes O(n) arithmetic operations; '
                      'the formulas use O(1) arithmetic operations for these fixed inputs. Both approaches retain '
                      'only a few integers. Python integer size grows with n, so constant operation counts do not '
                      'imply constant bit complexity for arbitrarily large integers.')
    doc.add_heading('cProfile analysis', 1)
    doc.add_paragraph('The original report identifies time.sleep as the largest time consumer, followed by '
                      'memory_intensive_function. The fast function is too brief for the printed millisecond '
                      'precision to resolve well. The optimized profile removes the sleep and long loops. '
                      'Very short optimized calls may print as 0.000 seconds; this is rounding, not zero execution time. '
                      'Use the uninstrumented table above for their comparison.')
    doc.add_heading('Line profiler analysis', 1)
    doc.add_paragraph('Before optimization, the sleep line dominates slow_function, while repeated loop control '
                      'and total += i ** 2 dominate the ten-million-iteration function. After optimization '
                      'there are no per-element loop lines: each wrapper calls the formula once. '
                      'Line tracing overhead is substantial, especially for millions of hits, so its total '
                      'duration should not be interpreted as normal application runtime.')
    doc.add_heading('Memory analysis', 1)
    for suffix in ('before', 'after'):
        text = (REPORTS / f'memory_{suffix}.txt').read_text(encoding='utf-8')
        samples = [float(value) for value in re.findall(r'^\s*\d+\s+([\d.]+) MiB', text, re.MULTILINE)]
        doc.add_paragraph(f'{suffix.title()}: largest reported line RSS = {max(samples):.1f} MiB.')
    doc.add_paragraph('Despite its name, memory_intensive_function does not build a large list: range is lazy '
                      'and the function keeps a running integer total. Both versions therefore have low auxiliary '
                      'storage, and RSS can remain flat or fluctuate because of allocator and process activity. '
                      'Removing the loop reduces temporary integer allocations, but a lower RSS is not guaranteed. '
                      'Before/after process baselines also include profiler and interpreter overhead. '
                      'The handout assertion requiring final RSS to increase was replaced with exact result '
                      'checks and positive RSS measurements; otherwise a correct implementation could fail unpredictably.')
    doc.add_paragraph('The original memory report contains very large negative values in the Increment column '
                      'on the repeatedly executed loop lines. These are an aggregation artifact: memory_profiler '
                      'accumulates differences against the previous line\'s recorded maximum across millions of '
                      'hits. A small RSS drop can therefore be counted repeatedly. They do not mean the program '
                      'freed hundreds of gigabytes. The Mem usage column stays around 24.6 MiB in this run.')
    doc.add_heading('Coverage analysis', 1)
    for suffix, module in [('before', 'profiler.py'), ('after', 'profiler_optimized.py')]:
        data = json.loads((REPORTS/f'coverage_{suffix}.json').read_text())
        info = next(v for k,v in data['files'].items() if k.endswith(module))
        doc.add_paragraph(f"{suffix.title()}: {info['summary']['covered_lines']}/{info['summary']['num_statements']} "
                          f"statements covered. Unexecuted lines: {info['missing_lines']}. "
                          f"Missing branches: {info.get('missing_branches', [])}.")
    doc.add_paragraph('The unit tests call computational functions directly. The main orchestration and '
                      'script-entry paths are exercised by the profiler commands but are outside these unit-test '
                      'coverage runs; their uncovered lines are therefore expected. Branch coverage is enabled. '
                      'The complete standalone HTML report directories are included, not just index.html, '
                      'because the index depends on accompanying assets and per-file pages.')
    doc.add_paragraph('The optimized percentage can be lower despite equivalent tested results: '
                      'the formula removes many covered loop statements while the same two orchestration '
                      'and entry-point statements remain uncovered. Percentages alone do not establish test quality.')
    for suffix in ('before', 'after'):
        doc.add_heading(suffix.title() + ' optimization: evidence', 1)
        for tool, title in [('cprofile','cProfile'),('line','line_profiler'),('memory','memory_profiler'),('tests','Unit tests'),('coverage','Coverage')]:
            doc.add_heading(title, 2)
            for path in snapshots(REPORTS/f'{tool}_{suffix}.txt'):
                doc.add_picture(str(path), width=Inches(6.5))
    for section in doc.sections:
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)
    doc.styles['Normal'].font.size = Pt(10)
    doc.save(ROOT/'lab9_Omar_Khalil.docx')
    print('Created lab9_Omar_Khalil.docx')


if __name__ == '__main__':
    main()
