"""Exact equivalence tests for the optimized implementation."""
import time
import unittest
from memory_profiler import memory_usage
import profiler_optimized as optimized


class TestOptimizedProfiler(unittest.TestCase):
    def test_functions(self):
        before = memory_usage(-1, interval=0.01, max_iterations=1)[0]
        start = time.perf_counter()
        self.assertEqual(optimized.slow_function(), 333283335000)
        self.assertEqual(optimized.optimized_fast_function(), 328350)
        self.assertEqual(optimized.memory_intensive_function(), 333333283333335000000)
        elapsed = time.perf_counter() - start
        after = memory_usage(-1, interval=0.01, max_iterations=1)[0]
        print(f"Optimized functions: {elapsed:.9f} seconds; RSS {before:.3f} -> {after:.3f} MiB")

    def test_formula_against_independent_loop(self):
        for n in (0, 1, 2, 10, 100, 10000):
            with self.subTest(n=n):
                self.assertEqual(optimized.sum_of_squares(n), sum(i*i for i in range(n)))


if __name__ == "__main__":
    unittest.main()
