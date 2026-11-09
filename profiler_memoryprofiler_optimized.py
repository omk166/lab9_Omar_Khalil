"""Line-level process RSS measurements after optimization."""
from memory_profiler import profile
import profiler_optimized as optimized


def main():
    return tuple(profile(function)() for function in (
        optimized.slow_function, optimized.optimized_fast_function,
        optimized.memory_intensive_function,
    ))


if __name__ == "__main__":
    main()
