"""This module contains a function to determine if a number is within a range."""

CONSTANT_VALUE = 10


def is_within_range(number_to_check: int) -> bool:
    """
    Check if a number is within the range of 0 to 100 (exclusive).

    Args:
        number_to_check: The number to check.

    Returns:
        True if the number is greater than 0 and less than 100, False otherwise.
    """
    if 0 < number_to_check < 100:
        return True
    return False
