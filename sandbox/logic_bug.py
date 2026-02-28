"""This module contains a function to count down from a given number."""


def count_down(start_number: int) -> None:
    """Counts down from a given number to 1, printing each number."""
    number: int = start_number
    while number > 0:
        print(number)
        number -= 1
