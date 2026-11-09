"""Correctness, timing and memory observations for the original lab."""
import time
import unittest
from memory_profiler import memory_usage
import profiler


class TestProfiler(unittest.TestCase):
    def measure(self, function):
        start = time.perf_counter()
        value = function()
        duration = time.perf_counter() - start
        print(f"{function.__name__}: {duration:.6f} seconds")
        return value, duration

    def test_slow_function(self):
        value, duration = self.measure(profiler.slow_function)
        self.assertEqual(value, 333283335000)
        self.assertGreaterEqual(duration, 2)

    def test_fast_function(self):
        value, duration = self.measure(profiler.fast_function)
        self.assertEqual(value, 328350)
        self.assertLess(duration, 1)

    def test_memory_intensive_function(self):
        before = memory_usage(-1, interval=0.01, max_iterations=1)[0]
        value, duration = self.measure(profiler.memory_intensive_function)
        after = memory_usage(-1, interval=0.01, max_iterations=1)[0]
        print(f"RSS before: {before:.3f} MiB; after: {after:.3f} MiB")
        self.assertEqual(value, 333333283333335000000)
        # RSS need not rise: this loop retains no large collection.
        self.assertGreater(before, 0)
        self.assertGreater(after, 0)
        self.assertLess(duration, 5)


if __name__ == "__main__":
    unittest.main()
