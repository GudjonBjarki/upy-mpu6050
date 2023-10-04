"""
A collection of general utility functions.
"""


def int_from_bytes(data, byteorder: str = "big", signed: bool = False):
    """
    Converts bytes to an integer.

    This is our own implementation of the normally built in int.from_bytes.
    We make our own since the micropython implementation for the ESP32 doesn't suport the signed parameter.

    Params:
        data: The bytes to convert.
        byteorder: The endianess of the bytes. Either "big" or "little"
        signed: Whether the integer is signed or not.

    Returns:
        The bytes converted into an integer.
    """

    if byteorder not in ("big", "little"):
        raise ValueError("Byteorder must be either 'big' or 'little'")

    if byteorder == "little":
        # list slicing with steps other than 1 isn't implemented.
        # data = data[::-1]
        reversed_data = bytearray(len(data))
        for i in range(len(data)):
            reversed_data[i] = data[len(data) - 1 - i]
        data = reversed_data

    value = 0
    for byte in data:
        value = (value << 8) | byte

    if signed and (data[0] & 0x80):
        value -= 1 << (8 * len(data))

    return value
