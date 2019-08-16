""" Driver for the LTC2631 Chip """
import logging
try:
    import smbus
except ImportError:
    def _getBus(self, num):
        return self;
    def write_word_data(self, device_address, mode, value):
        logger.debug("Sendind word data emulation: to: " + str(device_address) + " mode: " + str(mode)  + " value: " + str(value));

    obj = type('',(object,),{'SMBus':_getBus,'write_word_data':write_word_data})()
    smbus = obj;

logger = logging.getLogger(__name__)


FALLBACK_ADDRESS = 0x20     #7 bit address (will be left shifted to add the read write bit)

DEVICE_MODE_UPDATE_REG = 0x30

MODES = [DEVICE_MODE_UPDATE_REG]

LOGGING_ENABLED = True
INTERNAL_REFERENCE_VOLTAGE = 2.5
RESOLUTION = 10



class LTC2631:
    """
    A class used to represent the LTC2631 Chip.

    ...

    Attributes
    ----------
    refVoltage : float
        The Reference Voltage which is supplied to the LTC2631 Chip. Default Value is 5

    bus : SMBbus
        The SMBbus to connect to the LTC. Default ist SMBbus(1)

    Resolution : Int
        Accuracy of the LTC Chip. Information given as Number of Bits. Default: 10

    mode : int [2 Bytes]
        Defines the mode, the LTC is working in. See Datasheet, Table 3 Command codes. Only first Byte is relevant. Default is Update Register (0x30)

        Methods
        -------
        setToExtRefMode(refVoltage)
            Uses the extern supplied Voltage to generate the output.

            refVoltag: int
                Value of the supplied Voltage


        setToInternalRefMode(refVoltage = 2.5)
            Uses the intern supplied Voltage to generate the output. Default intern voltage is 2.5V

        setVolteage(voltage)
            Sets the voltage to a given voltage.

            voltage: float
                Must be between 0V and Reference Voltage.
        """


    def __init__(self, bus_num = 1, address=FALLBACK_ADDRESS, mode = DEVICE_MODE_UPDATE_REG, resolution = RESOLUTION) :
        if(mode not in MODES):
            raise ValueError('Unknown Mode: ' + str(mode))

        if(resolution == 0):
            raise ValueError('Resolution must not be 0!')

        self.device_address = address
        self.mode = mode
        self.bus = smbus.SMBus(1)
        self.refVoltage = INTERNAL_REFERENCE_VOLTAGE
        self.resolution = resolution

    def setToExtRefMode(self, refVoltage):
        """ if this function is called, the external supply voltage connected to the chip will be used """
        if(refVoltage < 0):
            raise ValueError('Reference Voltage must be > than 0. Given: '+ str(refVoltage))

        self.refVoltage = refVoltage
        self.bus.write_word_data(self.device_address, 0x70,0x0000)

    def setToInternalRefMode(self,  refVoltage = 2.5):
        if(refVoltage < 0):
            raise ValueError('Reference Voltage must be > than 0. Given: ' + str(refVoltage))

        self.bus.write_word_data(self.device_address,0x60,0x0000)
        self.refVoltage = refVoltage




    def setVoltage(self,voltage):
        """ Sets the output of this chip to a given voltage. The voltage must be smaller than the reference voltage"""
        #Vout= (k/2^n)*Vref
        if (voltage < 0 or voltage > self.refVoltage) :
            raise ValueError('Voltage mus be between 0 and reference Given: ' + str(voltage) + ' Reference Voltage: ' + str(self.refVoltage))

        logger.debug("Changing Voltage To " + str(voltage))
        value = int(voltage/(self.refVoltage) * (2**self.resolution - 1) )

        # Switch MSB and LSB.
        # LTC Only uses 10Bits from the 16Bits submitted by the RPI.
        # E.G: Set Output Value to 0b11 1111 1111 = 2^10 -1 = Max Value
        # -> Sends [1100 0000] [1111 1111]
        #          LSB            msb
        # Where the LSB gets padded with 6 Zeros to match 1 Byte

        msb = value >> 2
        lsb = value & 0b11

        defVal = (msb) + (lsb << 14)

        logger.debug("Val:" + str(defVal) + "bin: " + bin(defVal))


        self._setValue(defVal);

    def _setValue(self, value):
        """ private fucntion, transmits commands to set a given voltage usin I2C"""
        logger.debug("Setting value of LTC2631: Value: " + str(value) + "bin: " + bin(value)+"  Mode : " + str(self.mode) + "  Address: " + str(self.device_address))


        self.bus.write_word_data(self.device_address, self.mode, value)
