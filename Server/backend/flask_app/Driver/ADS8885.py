""" Driver for the ADS8885 chip """
import logging

logger = logging.getLogger(__name__)

try:
    import smbus
except ImportError:
    def _getBus(self, num):
        return self
    def read_word_data(self, adress, cmd):
        logger.debug("Mock Object -- read word data: addrress" + str(adress) + " cmd: " + str(cmd))
        return 0
    def write_word_data(self, device_address, mode, value):
        logger.debug("Sendind word data emulation: to: " + str(device_address) + " mode: " + str(mode)  + " value: " + str(value));

    obj = type('',(object,),{'read_word_data':read_word_data,'SMBus':_getBus,'write_word_data':write_word_data})()
    smbus = obj
try:
    import spidev
    simul = False
except ImportError:
    simul = True
    logger.error("could not import spidev")
try:
    import RPi.GPIO as GPIO
except ImportError:
    simul = True
    logger.error("could not import GPIO")
# from .PCAL6416 import PCAL6416
# from .PCAL6416 import PinAssignment

import random

SPI_MOSI = 10
SPI_MISO = 9
SPI_CLK = 11


class ResolutionScaler:
    """ Class that offers a simple transform function. <br>
        Used to alibrate a ADS8885 chip. <br>
        The getScaledValue returns the real applied value before the voltage devider for a measured Value of the ADS chip.
    """
    def __init__(self, multiplier, offset):
        self.multiplier = multiplier
        self.offset = offset

    def getScaledValue(self, value):
        """Returns the real applied value before the voltage devider that corresponds to a measured value of the ADS chip."""
        return self.multiplier * value + self.offset


class ADS8885:
    """
    A class used to represent the ADS8885 Chip.
    ...

    Attributes
    ----------
    pin1,pin2:  integer which represents the pinnumber of the PCAL chip to control the <br>
                -VSel1/2 pin of the corresponding TS5A3359DCUR chip for the voltage measurement <br>
                -IRngSel1/2 pin used for the current measurement <br>
    measurement ==0 voltage measurement <br>
                ==1 current measurement <br>
    """
    voltageMap = {
        1 : {
            "unit":"mV",
            "max":50
        },
        2 : {
            "unit":"mV",
            "max":500
        },
        3 : {
            "unit":"V",
            "max":5
        }
    }
    currentMap = {
        1 : {
            "unit":"uA",
            "max":500
        },
        2 : {
            "unit":"mA",
            "max":50
        }
    }


    def __init__(self, name, measurement, pinAss1, pinAss2, ioExpander, cspin, resolutionScalers, vref = 2.5):
        self.name = name
        self.vref = vref
        self.pinAss1 = pinAss1
        self.pinAss2 = pinAss2
        self.ioExpander = ioExpander
        self.resolution = 1
        self.cspin = cspin
        self.measurement = measurement
        self.autoResolution=False

        self.resolutionScalers = resolutionScalers

        if(simul == False):
            GPIO.setup(self.cspin, GPIO.OUT, initial = GPIO.LOW)
            self.ioExpander.setToOutputPinAssignment(pinAss1)
            self.ioExpander.setToOutputPinAssignment(pinAss2)
        #Voltage measurement
        if(measurement == 0):
            self.resolutionMap = self.voltageMap
        else:
            self.resolutionMap = self.currentMap





        # if (simul==False):
        #     self.spi = spidev.SpiDev()
        #     # self.spi.bits_per_word = 8
        #     self.spi.open(0,1)
        #     self.spi.max_speed_hz = 7629 #Todo tweek
        #     self.spi.mode = 0b10
        #     self.spi.cshigh = True
        #     #self.spi.no_cs = True
        #     #self.spi.lsbfirst = True
        #     GPIO.setup(self.cspin, GPIO.OUT)

    def getVoltage(self):
        """ return the voltage that is measured by the ADS chip.
        This voltage needs to be scaled up using the scaleToResolution function, to get the real applied voltage."""
        # print("getVoltage in: " + self.name)

        if(simul):
            return random.randint(0,  int(self.vref))
            # return random.randint(0,self.getMaxRange()) / 100

        data = self.getAdcValue()

        # print("Got data " + bin(data))
        #
        # st = bin(data) + (18-(len(bin(data))-2))*"0";
        #
        # print("n data : " + st,2)
        # # 0000 - 01ffff -> POS
        # # 1000 - 11fffff -> neg
        # print(st)
        # # data = 0x20000
        MSB = (int)((data & (0b1 << 17)) != 0)
        valToXor = (0x3FFFF * MSB)
        xored = (data ^ valToXor)
        val = xored + MSB

        # print(val)
        # print("xored: " + bin(xored))


        maxVal = 0x1FFFF
        # print("maxVal: " + str(maxVal))

        ratio = (val / maxVal)

        value = self.vref * ratio
        if(MSB):
            value *= -1

        # logger.debug("value: " + str(value) + "ratio: " + str(ratio))
        # print("first bit: " + str(data & (0b1 << 17)) == 0)

        return (-1) * value;

    def getVoltageFast(self):
        """ Fast implementation of the getVoltage() function """
        data = self.getAdcValue()

        MSB = (bool)((data & (0b1 << 17)) != 0)
        val = (data ^  (0x3FFFF * MSB)) + MSB

        value = self.vref * (val / 0x1FFFF)

        if(MSB == False):
                return -value
        return value

    def scaleToResolution(self, value):
        """ scales a measured value from the ADS chip to the real applied value using internal ResolutionScaler objects that are set when creating this class"""
        # print(self.name + " get scale to resolution for value : " + str(value))
        # print(self.resolution)
        # print(self.resolutionScalers[self.resolution].multiplier)
        # print(self.resolutionScalers[self.resolution].offset)
        # print("ret: " + str(self.resolutionScalers[self.resolution].getScaledValue(value)))
        return self.resolutionScalers[self.resolution].getScaledValue(value)
        # # self.calibrationMap[self.resolution]
        # return self.muliplier * value + self.offset;
        # # return value
        # # tmp = 0.0114*value**2 + 1.2688 * value + 2.0662
        # # if(self.name == "vm1"):
        # #     return value * 2.3307 - 0.1192 #* 3.133 - 40.6;
        # # elif(self.name == "vm2"):
        # #     return value * 2.3487 + 0.0375 #* 3.133 - 40.6;
        # # return value;

    def getMaxRange(self):
        """ Return the max value that can be measured in this range"""
        return self.resolutionMap[self.resolution]["max"]

    def getUnit(self):
        """ Return the unit of this measurement"""
        return self.resolutionMap[self.resolution]["unit"]

    def getName(self):
        """ Returns the name of this measurement device"""
        return self.name

    def getAdcValue(self):
        """ gets the value of the ADS Chip. currently using an ugly SPI emulation using GPIO pins.
        TODO: Fix errata of PCB and then use SPI library
        """
        if(simul):
            return random.randint(0,self.getMaxRange()) / 100

        LOW = GPIO.LOW
        HIGH = GPIO.HIGH

        GPIO.output(SPI_MOSI, HIGH)
        GPIO.output(SPI_CLK, LOW) # Start with clock low
        GPIO.output(self.cspin, HIGH)  # Enable chip

        for i in range(8):  # Send bit pattern starting from bit b4
            GPIO.output(SPI_CLK, HIGH) # Clock pulse
            GPIO.output(SPI_CLK, LOW)

        GPIO.output(SPI_MOSI, LOW)
        GPIO.output(SPI_CLK, LOW)
        GPIO.output(SPI_CLK, LOW)

        # Get reply
        data = 0
        for i in range(18):  # Read 11 bits and insert at right
            GPIO.output(SPI_CLK, HIGH)  # Clock pulse
            data <<= 1  # Shift left, LSB = 0
            if GPIO.input(SPI_MISO): # If high, LSB = 1,
                data |= 0x1
            GPIO.output(SPI_CLK, LOW)

        GPIO.output(self.cspin, LOW) # Disable chip

        return data;

    def setAutoResolution(self, autoResolution):
        """ Enables the auto resolution function for this chip"""
        self.autoResolution=autoResolution

    def maxResolution(self):
        """ return true if max resolution of the device is reached """
        reached= False
        if self.measurement==0:
            if self.resolution==3:
                reached=True
        if self.measurement==1:
            if self.resolution==2:
                reached=True
        return reached

    def minResolution(self):
        """ return true if min resolution of the device is reached """
        reached= (self.resolution==1)
        return reached


    def setResolution(self,resolution):
        """ Sets the resolution of this device. <br>
            [V]: 1 -> 50mV, 2 -> 500mV, 3 -> 5V <br>
            [A]: 1 -> 500uA, 2 -> 50mA
        """
        logger.debug("set resolution: name: " +str(self.name) + " resolution: " + str(resolution))
        self.resolution = resolution
        if self.measurement==0:
            #resolution = 50mV
            if resolution== 1:
                self.ioExpander.setVoltageLowOnPinAssignment(self.pinAss1)
                self.ioExpander.setVoltageLowOnPinAssignment(self.pinAss2)

            #resolution =500mV
            elif resolution== 2:
                self.ioExpander.setVoltageHighOnPinAssignment(self.pinAss1)
                self.ioExpander.setVoltageLowOnPinAssignment(self.pinAss2)

            #resolution = 5V
            elif resolution== 3:
                self.ioExpander.setVoltageLowOnPinAssignment(self.pinAss1)
                self.ioExpander.setVoltageHighOnPinAssignment(self.pinAss2)

            else:
                raise ValueError('resolution for voltage measurement must be 1 (for the 50mV range), 2 (for the 500mV range) or 3 (for the 5V range)')


        elif (self.measurement == 1):
            #resolution=500uA
            if resolution ==1:
                self.ioExpander.setVoltageHighOnPinAssignment(self.pinAss1)
                self.ioExpander.setVoltageHighOnPinAssignment(self.pinAss2)
            #resolution=50mA
            elif resolution==2:
                self.ioExpander.setVoltageLowOnPinAssignment(self.pinAss1)
                self.ioExpander.setVoltageLowOnPinAssignment(self.pinAss2)
            else:
                raise ValueError('resolution for current measurement must be 1 (for the 500uA range) or 2 (for the 50mA range)')


    def reachedResolutionMax(self, value):
        """
        returns true if voltage is close to upper resolution limit
        """
        tolerance=0
        reached=False
        resolution= self.resolution
        absVal = abs(value)
        if self.measurement==0:
            #resolution = 50mV
            if resolution== 1:
                reached= (absVal>=(50-tolerance))

            #resolution =500mV
            elif resolution== 2:
                reached= (absVal>=(500-tolerance))

            #resolution = 5V
            elif resolution== 3:
                reached= (absVal>=(5-tolerance))

            else:
                raise ValueError('resolution for voltage measurement must be 1 (for the 50mV range), 2 (for the 500mV range) or 3 (for the 5V range)')

        elif self.measurement == 1:
            #resolution=500uA
            if resolution ==1:
                reached= (absVal>=(500-tolerance))

            #resolution=50mA
            elif resolution==2:
                reached= (absVal>=(50-tolerance))

            else:
                raise ValueError('resolution for current measurement must be 1 (for the 500uA range) or 2 (for the 50mA range)')

        else:
                raise ValueError('measurement for voltage measurement must be 0, measurement for current measurement must be 1')
        return reached

    def getDebugInfos(self):
        """ Returns debug information about the chip (name, current resolution, maxRange etc.) """
        ans = self.getName() + " : " + str(self.getMaxRange()) + " : " + str(self.resolution) + "\n";
        ans += "ADC values: " +  str(self.getVoltage()) + " adc val fast " + str(self.getVoltageFast())
        return ans;

    def reachedResolutionMin(self, value):
        """
        Returns true if voltage is close to lower resolution limit
        """
        tolerance=0
        reached=False
        absVal = abs(value)
        resolution= self.resolution
        if self.measurement==0:
            #resolution = 50mV
            if resolution== 1:
                reached=False

            #resolution =500mV
            elif resolution== 2:
                reached= (absVal<=(50+tolerance))

            #resolution = 5V
            elif resolution== 3:
                reached= (absVal<=(0.5+tolerance))

            else:
                raise ValueError('resolution for voltage measurement must be 1 (for the 50mV range), 2 (for the 500mV range) or 3 (for the 5V range)')

        elif self.measurement == 1:
            #resolution=500uA
            if resolution ==1:
                reached= False

            #resolution=50mA
            elif resolution==2:
                reached= (absVal<=(0.5+tolerance))

            else:
                raise ValueError('resolution for current measurement must be 1 (for the 500uA range) or 2 (for the 50mA range)')

        else:
                raise ValueError('measurement for voltage measurement must be 0, measurement for current measurement must be 1')
        return reached
