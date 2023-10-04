from micropython import const
from machine import SoftI2C

from .i2c_transaction import I2CTransaction
from .bit_utils import enable_bit, disable_bit, set_bit, get_bit

# Gravitational constant used to scale accelerometer output.
gravitational_g = const(9.81)


class Registers:
    """
    A collection of registers used by the MPU6050 i2c protocol.
    """

    SELF_TEST_X = const(0x0D)
    SELF_TEXT_Y = const(0x0E)
    SELF_TEST_Z = const(0x0F)
    SMPLRT_DIV = const(0x10)

    CONFIG = const(0x19)
    ACCEL_CONFIG = const(0x1C)
    GYRO_CONFIG = const(0x1B)

    FIFO_EN = const(0x23)

    ACCEL_X_OUT = const(0x3B)
    ACCEL_Y_OUT = const(0x3D)
    ACCEL_Z_OUT = const(0x3F)

    TEMP_OUT = const(0x41)

    GYRO_X_OUT = const(0x43)
    GYRO_Y_OUT = const(0x45)
    GYRO_Z_OUT = const(0x47)

    PWR_MGMT_1 = const(0x6B)


class GyroscopeRange:
    """
    The different scale ranges of the MPU-6050 gyroscope.
    """

    # Gyrscope range of ±250°/s
    range_250 = (0b00, 250.0)

    # Gyrscope range of ±500°/s
    range_500 = (0b01, 500.0)

    # Gyrscope range of ±1000°/s
    range_1000 = (0b10, 1000.0)

    # Gyrscope range of ±2000°/s
    range_2000 = (0b11, 2000.0)


class AccelerometerRange:
    """
    The different scale ranges the MPU-6050 accelerometer.
    """

    # Accelerometer range of ±2.0g
    range_2g = (0b00, 2.0)

    # Accelerometer range of ±4.0g
    range_4g = (0b01, 4.0)

    # Accelerometer range of ±8.0g
    range_8g = (0b10, 8.0)

    # Accelerometer range of ±16.0g
    range_16g = (0b11, 16.0)


class ClockSource:
    """
    The different clock sources available for the MPU-6050.
    """

    internal_oscillator = 0
    gyroscope_x = 1
    gyroscope_y = 2
    gyroscope_z = 3
    external_32_khz = 4
    external_19_mhz = 5
    stop_clock = 7


class MPU6050:
    """
    A class to interact with a MPU-6050 sensor over I2C.
    """

    i2c: SoftI2C
    address: int
    gyroscope_scale: float
    accelerometer_scale: float

    def __init__(self, i2c: SoftI2C, address: int = 0x68):
        """
        Initialize a new Mpu6050 instance.
        This will also automatically wake up the component and configure the sensor ranges to default values.
        This also sets the clock source to the Y gyroscope output.

        Parameters:
            i2c: The I2C class to interact with.
            address: The address of the MPU6050 component.
                     This should typically always be b110100X (0x68 / 0x69).
        """
        self.i2c = i2c
        self.address = address

        self.wake_up()
        self.set_clock_source(ClockSource.gyroscope_y)
        self.set_gyroscope_range(GyroscopeRange.range_250)
        self.set_accelerometer_range(AccelerometerRange.range_2g)

    def start_transaction(self) -> I2CTransaction:
        """
        Start a new I2C transaction.
        All reads / writes should use transactions instead of accessing the i2c class.

        Returns:
            The transaction created.
        """
        transaction = I2CTransaction(self.i2c, self.address)
        return transaction

    def wake_up(self) -> None:
        """
        Wake up the MPU-6050 by disabling the SLEEP bit of the PWR_MGMT_1 register.
        """
        with self.start_transaction() as transaction:
            read_value = transaction.read_int(Registers.PWR_MGMT_1, 1)
            write_value = disable_bit(read_value, 6)
            transaction.write(Registers.PWR_MGMT_1, write_value)

    def sleep(self) -> None:
        """
        Put the MPU-6050 into sleep mode by enabling the SLEEP bit of the PWR_MGMT_1 register.
        """
        with self.start_transaction() as transaction:
            read_value = transaction.read_int(Registers.PWR_MGMT_1, 1)
            write_value = enable_bit(read_value, 6)
            transaction.write(Registers.PWR_MGMT_1, write_value)

    def set_gyroscope_range(self, option: tuple) -> None:
        """
        Set the scale range of the gyroscope by setting the FS_SEL value of the GYRO_CONFIG register.

        Parameters:
            option: A range value from GyroscopeRange.
        """
        # the 2 bit value of the selection.
        fs_sel = option[0]

        # the range of the gyroscope in degrees/s
        scale = option[1]

        with self.start_transaction() as transaction:
            read_value = transaction.read_int(Registers.GYRO_CONFIG, 1)
            write_value = set_bit(read_value, 3, get_bit(fs_sel, 0))
            write_value = set_bit(write_value, 4, get_bit(fs_sel, 1))
            transaction.write(Registers.GYRO_CONFIG, write_value)

        self.gyroscope_scale = scale

    def set_accelerometer_range(self, option: tuple) -> None:
        """
        Set the scale range of the accelerometer by setting the FS_SEL value of the ACCEL_CONFIG register.

        Parameters:
            option: A range value from AccelerometerRange.
        """
        # The 2 bit value of the selection.
        fs_sel = option[0]

        # The range of the accelerometers in gravitational gs.
        scale = option[1]

        with self.start_transaction() as transaction:
            read_value = transaction.read_int(Registers.ACCEL_CONFIG, 1)
            write_value = set_bit(read_value, 3, get_bit(fs_sel, 0))
            write_value = set_bit(write_value, 4, get_bit(fs_sel, 1))
            transaction.write(Registers.ACCEL_CONFIG, write_value)

        self.accelerometer_scale = scale

    def set_clock_source(self, option: int):
        """
        Set the clock source of the compnent.

        Parameters:
            option: A value from ClockSource.
        """
        with self.start_transaction() as transaction:
            read_value = transaction.read_int(Registers.PWR_MGMT_1, 1)

            write_value = set_bit(read_value, 0, get_bit(option, 0))
            write_value = set_bit(write_value, 1, get_bit(option, 2))
            write_value = set_bit(write_value, 1, get_bit(option, 3))

            transaction.write(Registers.PWR_MGMT_1, write_value)

    def read_gyroscope_raw(self) -> tuple:
        """
        Read the raw integer values from the gyroscope sensor.
        The integer values will be in the range of -32768 to 32767.
        These values must be scaled by the set gyroscope scale to get the rotation in degrees.

        Returns:
            A tuple containing the x, y, z values of the gyroscope reading.
        """
        with self.start_transaction() as transaction:
            reading = (
                transaction.read_int(Registers.GYRO_X_OUT, 2, signed=True),
                transaction.read_int(Registers.GYRO_Y_OUT, 2, signed=True),
                transaction.read_int(Registers.GYRO_Z_OUT, 2, signed=True),
            )

        return reading

    def read_gyroscope_degrees(self) -> tuple:
        """
        Read the rotation values from the gyroscope sensor.
        The value will be returned in degrees/second.

        Returns:
            A tuple containgn the x, y, z values of the gyroscope readings.
        """
        reading = self.read_gyroscope_raw()
        scaled_reading = (
            reading[0] / 32767 * self.gyroscope_scale,
            reading[1] / 32767 * self.gyroscope_scale,
            reading[2] / 32767 * self.gyroscope_scale,
        )
        return scaled_reading

    def read_accelerometer_raw(self) -> tuple:
        """
        Read the raw integer values from the accelerometer sensor.
        The integer values will be in the range of -32768 to 32767.
        These values must be sclaed by the set accelerometer scale to get the acceleration in gs.

        Returns:
            A tuple containing the x, y, z values of the accelerometer readings.
        """
        with self.start_transaction() as transaction:
            reading = (
                transaction.read_int(Registers.ACCEL_X_OUT, 2, signed=True),
                transaction.read_int(Registers.ACCEL_Y_OUT, 2, signed=True),
                transaction.read_int(Registers.ACCEL_Z_OUT, 2, signed=True),
            )

        return reading

    def read_accelerometer_gs(self) -> tuple:
        """
        Read the acceleration values from the accelerometer sensor.
        The values will be returned in gravitational gs.

        Returns:
            A tuple containing the x, y, z values of the accelerometer readings.
        """
        reading = self.read_accelerometer_raw()
        scaled_reading = (
            reading[0] / 32767 * self.accelerometer_scale,
            reading[1] / 32767 * self.accelerometer_scale,
            reading[2] / 32767 * self.accelerometer_scale,
        )
        return scaled_reading

    def read_accelerometer_meters(self) -> tuple:
        """
        Read the acceleration values from the accelerometer sensor.
        The values will be returned in m²/s.

        Returns:
            A tuple containing the x, y, z, values of the accelerometer readings.
        """
        reading = self.read_accelerometer_gs()
        scaled_reading = (
            reading[0] * gravitational_g,
            reading[1] * gravitational_g,
            reading[2] * gravitational_g,
        )
        return scaled_reading

    def read_temperature_raw(self) -> int:
        """
        Read the raw integer value from the temperature sensor.
        The integer value will be in the range of -32768 to 32767.

        Returns:
            The integer value of the temperature reading.
        """
        with self.start_transaction() as transaction:
            reading = transaction.read_int(Registers.TEMP_OUT, 2, signed=True)

        return reading

    def read_temperature_degrees(self) -> float:
        """
        Read the celcius value from the temperature sensor.

        Returns:
            The reading of the temperature sensor in celcius degrees.
        """
        reading = self.read_temperature_raw()

        # Datasheet tells us the temperature in degrees celcius should be (TEMP_OUT / 340 + 36.53)
        return reading / 340 + 36.53
