"""Line profiling after optimization."""
from line_profiler import LineProfiler
from profiler_optimized import (
    slow_function, optimized_fast_function, memory_intensive_function,
    sum_of_squares, main,
)


def profile_main():
    profiler = LineProfiler(slow_function, optimized_fast_function,
                            memory_intensive_function, sum_of_squares)
    profiler.runcall(main)
    profiler.print_stats()


if __name__ == "__main__":
    profile_main()
