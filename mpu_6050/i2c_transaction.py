from machine import SoftI2C

from .utils import int_from_bytes


class I2CTransaction:
    """
    Context manager class used to simplify interacting with an I2C slave.

    Example:
        with I2CTransaction(i2c, address) as transaction:
            # Reading a single byte from the slave as an integer from the register 0x30.
            read_value = transaction.read_int(0x30, 1)

            # Writing two bytes (0xDE, 0xAD) to the slave at register 0x40.
            transaction = transaction.write(0x40, 0xDE, 0xAD)
    """

    i2c: SoftI2C
    address: int

    def __init__(self, i2c: SoftI2C, address: int):
        """
        Initialize a new I2CTransaction instance.

        Parameters:
            i2c: The I2C object the transaction is for.
            address: The address of the slave interact with.
        """
        self.i2c = i2c
        self.address = address

    def __enter__(self):
        self.i2c.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.i2c.stop()
        return False

    def read_bytes(self, register: int, length: int) -> bytes:
        """
        Read bytes from the I2C slave.

        Parameters:
            register: The address of the register to read from.
            length: The number of bytes to read starting from the register address.

        Returns:
            The bytes read from the register.
        """
        data = self.i2c.readfrom_mem(self.address, register, length)
        return data

    def read_int(
        self,
        register: int,
        byte_length: int,
        byteorder: str = "big",
        signed: bool = False,
    ) -> int:
        """
        Read an integer value from the I2C slave.

        Parameters:
            register: The address of the register to read from.
            length: The number of bytes to read starting from the register address.
            byteorder: The endianness of the bytes read. Either "big" or "little".
            signed: Whether the integer should be signed or not.

        Returns:
            The integer value of the read bytes.
        """
        byte_value = self.read_bytes(register, byte_length)
        integer_value = int_from_bytes(byte_value, byteorder, signed)
        return integer_value

    def write(self, register: int, *values) -> None:
        """
        Write to the i2c slave.

        Parameters:
            register: The starting address of the register to write to.
            values: The values to write. Each value should be an integer in the range 0 - 255.
        """
        array = [register]
        for value in values:
            array.append(value)

        self.i2c.writeto(self.address, bytearray(array))
