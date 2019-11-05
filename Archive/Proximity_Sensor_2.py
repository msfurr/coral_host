"""
VCNL4010 PROXIMITY SENSOR LIBRARY (2nd I2C Bus)

WORKING VERSION

DESCRIPTION
    Current working version of proximity sensor code with custom read and write methods

"""

from micropython import const
import adafruit_bus_device.i2c_device as i2c_device
from smbus2 import SMBus

__version__ = "0.0.0-auto.0"

# pylint: disable=bad-whitespace
# Internal constants:
_VCNL4010_I2CADDR_DEFAULT   = const(0x13)
_VCNL4010_COMMAND           = const(0x80)
_VCNL4010_PRODUCTID         = const(0x81)
_VCNL4010_PROXRATE          = const(0x82)
_VCNL4010_IRLED             = const(0x83)
_VCNL4010_AMBIENTPARAMETER  = const(0x84)
_VCNL4010_AMBIENTDATA       = const(0x85)
_VCNL4010_PROXIMITYDATA     = const(0x87)
_VCNL4010_INTCONTROL        = const(0x89)
_VCNL4010_PROXINITYADJUST   = const(0x8A)
_VCNL4010_INTSTAT           = const(0x8E)
_VCNL4010_MODTIMING         = const(0x8F)
_VCNL4010_MEASUREAMBIENT    = const(0x10)
_VCNL4010_MEASUREPROXIMITY  = const(0x08)
_VCNL4010_AMBIENTREADY      = const(0x40)
_VCNL4010_PROXIMITYREADY    = const(0x20)
_VCNL4010_AMBIENT_LUX_SCALE = 0.25  # Lux value per 16-bit result value.

# User-facing constants:
FREQUENCY_3M125    = 3
FREQUENCY_1M5625   = 2
FREQUENCY_781K25   = 1
FREQUENCY_390K625  = 0

# Disable pylint's name warning as it causes too much noise.  Suffixes like
# BE (big-endian) or mA (milli-amps) don't confirm to its conventions--by
# design (clarity of code and explicit units).  Disable this globally to prevent
# littering the code with pylint disable and enable and making it less readable.
# pylint: disable=invalid-name

class VCNL4010:
    """Vishay VCNL4010 proximity and ambient light sensor."""

    def __init__(self):
        self._device = SMBus(2)
        self.led_current = 20
        self.frequency = FREQUENCY_390K625
        self._write_u8(_VCNL4010_INTCONTROL, 0x08)

    def _read_u8(self, address):
        # Read an 8-bit unsigned value from the specified 8-bit address.
        with SMBus(2) as self._device:
            read = self._device.read_byte_data(_VCNL4010_I2CADDR_DEFAULT, address)
        return read

    def _write_u8(self, address, val):
        # Write an 8-bit unsigned value to the specified 8-bit address.
        with SMBus(2) as self._device:
            self._device.write_byte_data(_VCNL4010_I2CADDR_DEFAULT, address, val)

    def _read_u16BE(self, address):
        with SMBus(2) as self._device:
            read_block = self._device.read_i2c_block_data(_VCNL4010_I2CADDR_DEFAULT, address, 2)
        return (read_block[0] << 8) | read_block[1]

    @property
    def proximity(self):
        """The detected proximity of an object in front of the sensor.  This
        is a unit-less unsigned 16-bit value (0-65535) INVERSELY proportional
        to the distance of an object in front of the sensor (up to a max of
        ~200mm).  For example a value of 10 is an object farther away than a
        value of 1000.  Note there is no conversion from this value to absolute
        distance possible, you can only make relative comparisons.
        """
        # Clear interrupt.
        status = self._read_u8(_VCNL4010_INTSTAT)
        status &= ~0x80
        self._write_u8(_VCNL4010_INTSTAT, status)
        # Grab a proximity measurement.
        self._write_u8(_VCNL4010_COMMAND, _VCNL4010_MEASUREPROXIMITY)
        # Wait for result, then read and return the 16-bit value.
        while True:
            result = self._read_u8(_VCNL4010_COMMAND)
            if result & _VCNL4010_PROXIMITYREADY:
                return self._read_u16BE(_VCNL4010_PROXIMITYDATA)
