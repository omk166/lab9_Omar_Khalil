"""Equivalent sums with unnecessary waiting and iteration removed. Omar Khalil."""


def sum_of_squares(n):
    """Sum squares in range(n) in constant arithmetic operations."""
    return n * (n - 1) * (2 * n - 1) // 6


def slow_function():
    # The artificial delay does not affect the returned result.
    return sum_of_squares(10000)


def optimized_fast_function():
    return sum_of_squares(100)


def memory_intensive_function():
    return sum_of_squares(10000000)


def main():
    return slow_function(), optimized_fast_function(), memory_intensive_function()


if __name__ == "__main__":
    main()
