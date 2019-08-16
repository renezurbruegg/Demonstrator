""" Driver for the PCAL6416 Chip """
import logging
logger = logging.getLogger(__name__)

try:
    import smbus
except ImportError:
    logger.debug("could not import smbus")
    def _getBus(self, num):
        return self;
    def read_word_data(self, adress, cmd):
        logger.debug("Mock Object -- read word data: addrress" + str(adress) + " cmd: " + str(cmd))
        return 0;
    def write_word_data(self, device_address, mode, value):
        logger.debug("Sendind word data emulation: to: " + str(device_address) + " mode: " + str(mode)  + " value: " + str(value));

    obj = type('',(object,),{'read_word_data':read_word_data,'SMBus':_getBus,'write_word_data':write_word_data})()
    smbus = obj;

bus_num = 1
# Logger used to debug information
# use logger.info("my log message") for general infos and
# use logger.debug("my debug message") for information that are not necessary during production (won't be logged)


#connect Adress Pin to ground
SLAVE_ADDRESS=0b0100000

#connect Address Pin to VDD
#SLAVE_ADDRESS=0b0100001


class PinAssignment:
    """ Helper class for the PCAL6416, since the IoExpander does not also provide pins but also ports, this class is used to uniquely select a pin of the expander"""
    def __init__(self, port, pin, type):
        self.portNumber = port
        self.pinNumber = pin
        self.type = type


# See https://github.com/diaevd/android_kernel_samsung_sm-t325/blob/master/drivers/gpio/gpio-pcal6416a.c for a driver implementation in c.
# Datasheet with communication commands https://www.nxp.com/docs/en/data-sheet/PCAL6416A.pdf
class PCAL6416:
    """
    A class used to represent the PCAL6416 (IoExpander) Chip.
    ...

    Attributes
    ----------
    address int
    cmd int
    val int
    pinNumber int
    portNumber int
    """
    def __init__(self,bus_num=1,address=SLAVE_ADDRESS):
        logger.info("PCAL641 created address: " + str(address))
        self.bus = smbus.SMBus(1)
        self.device_address=address


    def setVoltageHighOnPinAssignment(self, pinAssignment):
        self.setVoltageHighOnPin(pinAssignment.portNumber, pinAssignment.pinNumber)

    def setVoltageLowOnPinAssignment(self, pinAssignment):
            self.setVoltageLowOnPin(pinAssignment.portNumber, pinAssignment.pinNumber)

    # sets voltage to high on given pin
    def setVoltageHighOnPin(self, portNumber, pinNumber):
        logger.debug("setVoltHighOnPin port:" +str(portNumber) + " pin: " + str(pinNumber))
        if portNumber==0:
            cmd=0x02
            register=self._readValue(self.device_address,cmd)

        elif portNumber==1:
            cmd=0x03
            register=self._readValue(self.device_address,cmd)

        else:
            raise ValueError('portNumber must be 0 or 1')

        value=1<<pinNumber
        value= value|register           #verodern mit alten value
        logger.debug("new value for port "+str(portNumber)+ " is "+bin(value))
        self._setValue(self.device_address,cmd,value)


    # sets voltage to low on given pin
    def setVoltageLowOnPin(self, portNumber, pinNumber):
        logger.debug("setVoltLowOnPin port:" +str(portNumber) + " pin: " + str(pinNumber))
        if portNumber==0:
            cmd=0x02
            register=self._readValue(self.device_address,cmd)

        elif portNumber==1:
            cmd=0x03
            register=self._readValue(self.device_address,cmd)
        else:
            raise ValueError('PortNumber must be 0 or 1')

        x= 1<< pinNumber                # je nach pin auf null setzen um als output zu machen
        x=~x
        value=register&x                #verunden mit bisherigem value
        logger.debug("new value for port "+str(portNumber)+ " is "+bin(value))
        self._setValue(self.device_address,cmd,value)

    # reads voltage from given OUTPUT pin
    def getVoltageOnOutputPin(self,portNumber, pinNumber):
        if portNumber==0:
            cmd=0x02

        elif portNumber==1:
            cmd=0x03

        else:
            raise ValueError('PortNumber must be 0 or 1')

        register=self._readValue(self.device_address, cmd)
        x=register>>pinNumber
        x=x%2
        logger.debug("voltage on port " + str(portNumber) +" Pin "+ str(pinNumber)+ " is " +str(x))
        return x

    #returns voltage from given INPUT pin
    def getVoltageOnInputPin(self,portNumber, pinNumber):
        if portNumber==0:
            cmd=0x00
        elif portNumber==1:
            cmd=0x01
        else:
            raise ValueError('PortNumber must be 0 or 1')

        register=self._readValue(self.device_address, cmd)
        x=register>>pinNumber
        x=x%2
        logger.debug("voltage on port " + str(portNumber) +" Pin "+ str(pinNumber)+ " is " +str(x))
        return x


    def setToOutputPinAssignment(self, assignment):
        self.setToOutputPin(assignment.portNumber, assignment.pinNumber)

    def setToOutputPin(self,portNumber, pinNumber):
        if portNumber==0:
            cmd=0X06                    #configuration port 0
            register=self._readValue(self.device_address, cmd)

        elif portNumber==1:
            cmd=0x07                    #configuration port 1
            register=self._readValue(self.device_address, cmd)
        else:
            raise ValueError('PortNumber must be 0 or 1')

        x= 1<< pinNumber                # je nach pin auf null setzen um als output zu machen
        x=~x
        value=register&x                                      #verunden mit bisherigem value
        logger.debug("new out/input configuration is " + bin(value))
        self._setValue(self.device_address,cmd,value)


    def setToInputPin(self, portNumber, pinNumber):
        if portNumber==0:
            cmd=0x06                    #configuration port 0
            register=self._readValue(self.device_address, cmd)

        elif portNumber==1:
            cmd=0x07                    #configuration port 1
            register=self._readValue(self.device_address, cmd)

        else:
            raise ValueError('PortNumber must be 0 or 1')

        value=1<<pinNumber
        value= value|register           #verodern mit alten value
        logger.debug("new out/input configuration is " + bin(value))
        self._setValue(self.device_address,cmd,value)

    # Sends a given value and comand to a given i2c address
    def _setValue(self, address, cmd, value):
        logger.debug("Setting value of PCAL6416 " + str(value) + "bin: " + bin(value)+"  Cmd : " + str(cmd) + " bin: " + bin(cmd) + "to  Address: " + str(address))

        self.bus.write_word_data(self.device_address, cmd, value)

    #Returns the value at a given i2c address
    def _readValue(self, address, cmd):
        logger.debug("Reading value of PCAL6416 at address: " + str(address) + "bin: " + bin(address) + "cmd: " + str(cmd)+ "bin: "+ bin(cmd))
        return self.bus.read_word_data(self.device_address, cmd)
