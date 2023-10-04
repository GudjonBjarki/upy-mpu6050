"""
A set of utility functions to help with bit manipulation.
These methods should simplify bit manipulation and make it more verbose.
"""


def enable_bit(value: int, bit_index: int) -> int:
    """
    Set a bit with a given index to 1.

    Parameters:
        value: The value to set the bit of.
        bit_index: The index of the bit to set.

    Returns:
        The updated value with the bit set to 1.
    """
    return value | (1 << bit_index)


def disable_bit(value: int, bit_index: int) -> int:
    """
    Set a bit with a given index to 0.

    Parameters:
        value: The value to set the bit of.
        bit_index: The index of the bit to set.

    Returns:
        The updated value with the bit set to 0.
    """
    return value & ~(1 << bit_index)


def set_bit(value: int, bit_index: int, bit_value: bool) -> int:
    """
    Set a bit with a given index to a given value.

    Parameters:
        value: The value to set the bit of.
        bit_index: The index of the bit to set.
        bit_value: The value to set the bit to. True for 1, False for 0.

    Returns:
        The updated value with the bit set.
    """
    if bit_value:
        return enable_bit(value, bit_index)

    else:
        return disable_bit(value, bit_index)


def get_bit(value: int, bit_index: int) -> int:
    """
    Get the value of a bit with a given index from a value.

    Parameters:
        value: The value to check the bit of.
        bit_index: The index of the bit to check.

    Returns:
        The value of the bit either 0 or 1.
    """
    return (value >> bit_index) & 1
