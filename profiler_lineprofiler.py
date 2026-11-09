"""Line profiling of the original functions without copying their code."""
from line_profiler import LineProfiler
from profiler import slow_function, fast_function, memory_intensive_function, main


def profile_main():
    profiler = LineProfiler(slow_function, fast_function, memory_intensive_function)
    profiler.runcall(main)
    profiler.print_stats()


if __name__ == "__main__":
    profile_main()
