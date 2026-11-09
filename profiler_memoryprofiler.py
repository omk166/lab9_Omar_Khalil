"""Line-level process RSS measurements of the unmodified workload."""
from memory_profiler import profile
import profiler


def main():
    # Wrap the actual definitions so line reports reference profiler.py.
    return tuple(profile(function)() for function in (
        profiler.slow_function, profiler.fast_function,
        profiler.memory_intensive_function,
    ))


if __name__ == "__main__":
    main()
