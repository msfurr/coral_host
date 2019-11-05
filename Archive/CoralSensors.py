"""
Coral Sensor Library

"""

"""
VCNL4010 PROXIMITY SENSOR LIBRARY

WORKING VERSION

DESCRIPTION
    Current working version of proximity sensor code with custom read and write methods

ISSUES
    Output range is 2000 - 15000 instead of 0 - 65000
    Read method
        Original read method uses buffer to "write then read into" instead of just read from the register
    16 bit conversion
        Not sure if the method I'm using is actually reading into 16 bit high and low bytes

QUESTIONS
    Do I have to use a buffer?
    Why is the original method writing and then reading from the buffer immediately?
    How can I better replicate the original library with my code?
    Is the read and write from the SMBus library comparable to the read and write from the CircuitPython library?
    Also questions around conversion from high and low byte to 16 bit data?
        Seems like all the outputs I'm getting are in decimal values?
        Is it worth reading from one register (8 bit) then the other, combining into a string then reading then entire
        value as a 16 bit byte?

APPROACHES - what have I tried that hasn't worked
    Using CircuitPython based libraries
        Need to have a board that is custom built for their application

    Recreating the "write_read" method within the source code with my methods from SMBus
        Unclear how they write into the buffer, where the buffer is located, how they read from the buffer
        Note that my current version does not use a buffer


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
        self._device = SMBus(1)
        self.led_current = 20
        self.frequency = FREQUENCY_390K625
        self._write_u8(_VCNL4010_INTCONTROL, 0x08)

    def _read_u8(self, address):
        # Read an 8-bit unsigned value from the specified 8-bit address.
        with SMBus(1) as self._device:
            read = self._device.read_byte_data(_VCNL4010_I2CADDR_DEFAULT, address)
        return read

    def _write_u8(self, address, val):
        # Write an 8-bit unsigned value to the specified 8-bit address.
        with SMBus(1) as self._device:
            self._device.write_byte_data(_VCNL4010_I2CADDR_DEFAULT, address, val)

    def _read_u16BE(self, address):
        with SMBus(1) as self._device:
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

"""
ADS1015 LIBRARY

WORKING VERSION

DESCRIPTION
    Current working version of ADS1015 read library

ISSUES
    Output range is 15000 - 25000
    Read method
        Original read method uses buffer to "write then read into" instead of just read from the register
    16 bit conversion
        Not sure if the method I'm using is actually reading into 16 bit high and low bytes

CHANGE LOG
    10.21 - Update to read 16 bit


"""

import time
from smbus2 import SMBus

# Register and other configuration values:
ADS1x15_DEFAULT_ADDRESS        = 0x48
ADS1x15_POINTER_CONVERSION     = 0x00
ADS1x15_POINTER_CONFIG         = 0x01
ADS1x15_POINTER_LOW_THRESHOLD  = 0x02
ADS1x15_POINTER_HIGH_THRESHOLD = 0x03
ADS1x15_CONFIG_OS_SINGLE       = 0x8000
ADS1x15_CONFIG_MUX_OFFSET      = 12
# Maping of gain values to config register values.
ADS1x15_CONFIG_GAIN = {
    2/3: 0x0000,
    1:   0x0200,
    2:   0x0400,
    4:   0x0600,
    8:   0x0800,
    16:  0x0A00
}
ADS1x15_CONFIG_MODE_CONTINUOUS  = 0x0000
ADS1x15_CONFIG_MODE_SINGLE      = 0x0100
# Mapping of data/sample rate to config register values for ADS1015 (faster).
ADS1015_CONFIG_DR = {
    128:   0x0000,
    250:   0x0020,
    490:   0x0040,
    920:   0x0060,
    1600:  0x0080,
    2400:  0x00A0,
    3300:  0x00C0
}
# Mapping of data/sample rate to config register values for ADS1115 (slower).
ADS1115_CONFIG_DR = {
    8:    0x0000,
    16:   0x0020,
    32:   0x0040,
    64:   0x0060,
    128:  0x0080,
    250:  0x00A0,
    475:  0x00C0,
    860:  0x00E0
}
ADS1x15_CONFIG_COMP_WINDOW      = 0x0010
ADS1x15_CONFIG_COMP_ACTIVE_HIGH = 0x0008
ADS1x15_CONFIG_COMP_LATCHING    = 0x0004
ADS1x15_CONFIG_COMP_QUE = {
    1: 0x0000,
    2: 0x0001,
    4: 0x0002
}
ADS1x15_CONFIG_COMP_QUE_DISABLE = 0x0003


class ADS1x15(object):
    """Base functionality for ADS1x15 analog to digital converters."""

    def __init__(self, address = ADS1x15_DEFAULT_ADDRESS):
        from smbus2 import SMBus
        self._device = SMBus(1)

    def _data_rate_default(self):
        """Retrieve the default data rate for this ADC (in samples per second).
        Should be implemented by subclasses.
        """
        raise NotImplementedError('Subclasses must implement _data_rate_default!')

    def _data_rate_config(self, data_rate):
        """Subclasses should override this function and return a 16-bit value
        that can be OR'ed with the config register to set the specified
        data rate.  If a value of None is specified then a default data_rate
        setting should be returned.  If an invalid or unsupported data_rate is
        provided then an exception should be thrown.
        """
        raise NotImplementedError('Subclass must implement _data_rate_config function!')

    def _conversion_value(self, low, high):
        """Subclasses should override this function that takes the low and high
        byte of a conversion result and returns a signed integer value.
        """
        raise NotImplementedError('Subclass must implement _conversion_value function!')

    def _read(self, mux, gain, data_rate, mode):
        """Perform an ADC read with the provided mux, gain, data_rate, and mode
        values.  Returns the signed integer result of the read.
        """
        config = ADS1x15_CONFIG_OS_SINGLE  # Go out of power-down mode for conversion.
        # Specify mux value.
        config |= (mux & 0x07) << ADS1x15_CONFIG_MUX_OFFSET
        # Validate the passed in gain and then set it in the config.
        if gain not in ADS1x15_CONFIG_GAIN:
            raise ValueError('Gain must be one of: 2/3, 1, 2, 4, 8, 16')
        config |= ADS1x15_CONFIG_GAIN[gain]
        # Set the mode (continuous or single shot).
        config |= mode
        # Get the default data rate if none is specified (default differs between
        # ADS1015 and ADS1115).
        if data_rate is None:
            data_rate = self._data_rate_default()
        # Set the data rate (this is controlled by the subclass as it differs
        # between ADS1015 and ADS1115).
        config |= self._data_rate_config(data_rate)
        config |= ADS1x15_CONFIG_COMP_QUE_DISABLE  # Disble comparator mode.
        # Send the config value to start the ADC conversion.

        # Explicitly break the 16-bit value down to a big endian pair of bytes.
        self._device.write_i2c_block_data(ADS1x15_DEFAULT_ADDRESS, ADS1x15_POINTER_CONFIG, [(config >> 8) & 0xFF, config & 0xFF])

        # Wait for the ADC sample to finish based on the sample rate plus a
        # small offset to be sure (0.1 millisecond).
        time.sleep(1.0/data_rate+0.0001)

        # Retrieve the result.
        read_block = self._device.read_i2c_block_data(ADS1x15_DEFAULT_ADDRESS, ADS1x15_POINTER_CONVERSION, 2)
        return (read_block[0] << 8) | read_block[1]

    def _read_comparator(self, mux, gain, data_rate, mode, high_threshold,
                         low_threshold, active_low, traditional, latching,
                         num_readings):
        """Perform an ADC read with the provided mux, gain, data_rate, and mode
        values and with the comparator enabled as specified.  Returns the signed
        integer result of the read.
        """
        assert num_readings == 1 or num_readings == 2 or num_readings == 4, 'Num readings must be 1, 2, or 4!'
        # Set high and low threshold register values.
        self._device.write_i2c_block_data(ADS1x15_DEFAULT_ADDRESS, ADS1x15_POINTER_HIGH_THRESHOLD, [(high_threshold >> 8) & 0xFF, high_threshold & 0xFF])
        self._device.write_i2c_block_data(ADS1x15_DEFAULT_ADDRESS, ADS1x15_POINTER_LOW_THRESHOLD, [(low_threshold >> 8) & 0xFF, low_threshold & 0xFF])
        # Now build up the appropriate config register value.
        config = ADS1x15_CONFIG_OS_SINGLE  # Go out of power-down mode for conversion.
        # Specify mux value.
        config |= (mux & 0x07) << ADS1x15_CONFIG_MUX_OFFSET
        # Validate the passed in gain and then set it in the config.
        if gain not in ADS1x15_CONFIG_GAIN:
            raise ValueError('Gain must be one of: 2/3, 1, 2, 4, 8, 16')
        config |= ADS1x15_CONFIG_GAIN[gain]
        # Set the mode (continuous or single shot).
        config |= mode
        # Get the default data rate if none is specified (default differs between
        # ADS1015 and ADS1115).
        if data_rate is None:
            data_rate = self._data_rate_default()
        # Set the data rate (this is controlled by the subclass as it differs
        # between ADS1015 and ADS1115).
        config |= self._data_rate_config(data_rate)
        # Enable window mode if required.
        if not traditional:
            config |= ADS1x15_CONFIG_COMP_WINDOW
        # Enable active high mode if required.
        if not active_low:
            config |= ADS1x15_CONFIG_COMP_ACTIVE_HIGH
        # Enable latching mode if required.
        if latching:
            config |= ADS1x15_CONFIG_COMP_LATCHING
        # Set number of comparator hits before alerting.
        config |= ADS1x15_CONFIG_COMP_QUE[num_readings]
        # Send the config value to start the ADC conversion.
        # Explicitly break the 16-bit value down to a big endian pair of bytes.
        self._device.write_i2c_block_data(ADS1x15_DEFAULT_ADDRESS, ADS1x15_POINTER_CONFIG, [(config >> 8) & 0xFF, config & 0xFF])
        # Wait for the ADC sample to finish based on the sample rate plus a
        # small offset to be sure (0.1 millisecond).
        time.sleep(1.0/data_rate+0.0001)
        # Retrieve the result.
        result = self._device.read_byte_data(ADS1x15_DEFAULT_ADDRESS, ADS1x15_POINTER_CONVERSION, 2)
        return result

    def read_adc(self, channel, gain=1, data_rate=None):
        """Read a single ADC channel and return the ADC value as a signed integer
        result.  Channel must be a value within 0-3.
        """
        assert 0 <= channel <= 3, 'Channel must be a value within 0-3!'
        # Perform a single shot read and set the mux value to the channel plus
        # the highest bit (bit 3) set.
        return self._read(channel + 0x04, gain, data_rate, ADS1x15_CONFIG_MODE_SINGLE)

    def read_adc_difference(self, differential, gain=1, data_rate=None):
        """Read the difference between two ADC channels and return the ADC value
        as a signed integer result.  Differential must be one of:
          - 0 = Channel 0 minus channel 1
          - 1 = Channel 0 minus channel 3
          - 2 = Channel 1 minus channel 3
          - 3 = Channel 2 minus channel 3
        """
        assert 0 <= differential <= 3, 'Differential must be a value within 0-3!'
        # Perform a single shot read using the provided differential value
        # as the mux value (which will enable differential mode).
        return self._read(differential, gain, data_rate, ADS1x15_CONFIG_MODE_SINGLE)

    def start_adc(self, channel, gain=1, data_rate=None):
        """Start continuous ADC conversions on the specified channel (0-3). Will
        return an initial conversion result, then call the get_last_result()
        function to read the most recent conversion result. Call stop_adc() to
        stop conversions.
        """
        assert 0 <= channel <= 3, 'Channel must be a value within 0-3!'
        # Start continuous reads and set the mux value to the channel plus
        # the highest bit (bit 3) set.
        return self._read(channel + 0x04, gain, data_rate, ADS1x15_CONFIG_MODE_CONTINUOUS)

    def start_adc_difference(self, differential, gain=1, data_rate=None):
        """Start continuous ADC conversions between two ADC channels. Differential
        must be one of:
          - 0 = Channel 0 minus channel 1
          - 1 = Channel 0 minus channel 3
          - 2 = Channel 1 minus channel 3
          - 3 = Channel 2 minus channel 3
        Will return an initial conversion result, then call the get_last_result()
        function continuously to read the most recent conversion result.  Call
        stop_adc() to stop conversions.
        """
        assert 0 <= differential <= 3, 'Differential must be a value within 0-3!'
        # Perform a single shot read using the provided differential value
        # as the mux value (which will enable differential mode).
        return self._read(differential, gain, data_rate, ADS1x15_CONFIG_MODE_CONTINUOUS)

    def start_adc_comparator(self, channel, high_threshold, low_threshold,
                             gain=1, data_rate=None, active_low=True,
                             traditional=True, latching=False, num_readings=1):
        """Start continuous ADC conversions on the specified channel (0-3) with
        the comparator enabled.  When enabled the comparator to will check if
        the ADC value is within the high_threshold & low_threshold value (both
        should be signed 16-bit integers) and trigger the ALERT pin.  The
        behavior can be controlled by the following parameters:
          - active_low: Boolean that indicates if ALERT is pulled low or high
                        when active/triggered.  Default is true, active low.
          - traditional: Boolean that indicates if the comparator is in traditional
                         mode where it fires when the value is within the threshold,
                         or in window mode where it fires when the value is _outside_
                         the threshold range.  Default is true, traditional mode.
          - latching: Boolean that indicates if the alert should be held until
                      get_last_result() is called to read the value and clear
                      the alert.  Default is false, non-latching.
          - num_readings: The number of readings that match the comparator before
                          triggering the alert.  Can be 1, 2, or 4.  Default is 1.
        Will return an initial conversion result, then call the get_last_result()
        function continuously to read the most recent conversion result.  Call
        stop_adc() to stop conversions.
        """
        assert 0 <= channel <= 3, 'Channel must be a value within 0-3!'
        # Start continuous reads with comparator and set the mux value to the
        # channel plus the highest bit (bit 3) set.
        return self._read_comparator(channel + 0x04, gain, data_rate,
                                     ADS1x15_CONFIG_MODE_CONTINUOUS,
                                     high_threshold, low_threshold, active_low,
                                     traditional, latching, num_readings)

    def start_adc_difference_comparator(self, differential, high_threshold, low_threshold,
                                        gain=1, data_rate=None, active_low=True,
                                        traditional=True, latching=False, num_readings=1):
        """Start continuous ADC conversions between two channels with
        the comparator enabled.  See start_adc_difference for valid differential
        parameter values and their meaning.  When enabled the comparator to will
        check if the ADC value is within the high_threshold & low_threshold value
        (both should be signed 16-bit integers) and trigger the ALERT pin.  The
        behavior can be controlled by the following parameters:
          - active_low: Boolean that indicates if ALERT is pulled low or high
                        when active/triggered.  Default is true, active low.
          - traditional: Boolean that indicates if the comparator is in traditional
                         mode where it fires when the value is within the threshold,
                         or in window mode where it fires when the value is _outside_
                         the threshold range.  Default is true, traditional mode.
          - latching: Boolean that indicates if the alert should be held until
                      get_last_result() is called to read the value and clear
                      the alert.  Default is false, non-latching.
          - num_readings: The number of readings that match the comparator before
                          triggering the alert.  Can be 1, 2, or 4.  Default is 1.
        Will return an initial conversion result, then call the get_last_result()
        function continuously to read the most recent conversion result.  Call
        stop_adc() to stop conversions.
        """
        assert 0 <= differential <= 3, 'Differential must be a value within 0-3!'
        # Start continuous reads with comparator and set the mux value to the
        # channel plus the highest bit (bit 3) set.
        return self._read_comparator(differential, gain, data_rate,
                                     ADS1x15_CONFIG_MODE_CONTINUOUS,
                                     high_threshold, low_threshold, active_low,
                                     traditional, latching, num_readings)

    def stop_adc(self):
        """Stop all continuous ADC conversions (either normal or difference mode).
        """
        # Set the config register to its default value of 0x8583 to stop
        # continuous conversions.
        config = 0x8583
        self._device.write_i2c_block_data(ADS1x15_DEFAULT_ADDRESS, ADS1x15_POINTER_CONFIG, [(config >> 8) & 0xFF, config & 0xFF])

    def get_last_result(self):
        """Read the last conversion result when in continuous conversion mode.
        Will return a signed integer value.
        """
        # Retrieve the conversion register value, convert to a signed int, and
        # return it.
        result = self._device.read_byte_data(ADS1x15_DEFAULT_ADDRESS, ADS1x15_POINTER_CONVERSION, 2)
        return result


class ADS1115(ADS1x15):
    """ADS1115 16-bit analog to digital converter instance."""

    def __init__(self, *args, **kwargs):
        super(ADS1115, self).__init__(*args, **kwargs)

    def _data_rate_default(self):
        # Default from datasheet page 16, config register DR bit default.
        return 128

    def _data_rate_config(self, data_rate):
        if data_rate not in ADS1115_CONFIG_DR:
            raise ValueError('Data rate must be one of: 8, 16, 32, 64, 128, 250, 475, 860')
        return ADS1115_CONFIG_DR[data_rate]

    def _conversion_value(self, low, high):
        # Convert to 16-bit signed value.
        value = ((high & 0xFF) << 8) | (low & 0xFF)
        # Check for sign bit and turn into a negative value if set.
        if value & 0x8000 != 0:
            value -= 1 << 16
        return value


class ADS1015(ADS1x15):
    """ADS1015 12-bit analog to digital converter instance."""

    def __init__(self, *args, **kwargs):
        super(ADS1015, self).__init__(*args, **kwargs)

    def _data_rate_default(self):
        # Default from datasheet page 19, config register DR bit default.
        return 1600

    def _data_rate_config(self, data_rate):
        if data_rate not in ADS1015_CONFIG_DR:
            raise ValueError('Data rate must be one of: 128, 250, 490, 920, 1600, 2400, 3300')
        return ADS1015_CONFIG_DR[data_rate]

    def _conversion_value(self, low, high):
        # Convert to 12-bit signed value.
        value = ((high & 0xFF) << 4) | ((low & 0xFF) >> 4)
        # Check for sign bit and turn into a negative value if set.
        if value & 0x800 != 0:
            value -= 1 << 12
        return value

