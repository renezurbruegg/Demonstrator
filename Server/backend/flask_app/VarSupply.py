""" Class that emulates the VarSupply object and offers a setVoltage() function"""
from flask_app.Driver.PCAL6416 import PCAL6416
import logging

class VarSupply:
    """
    This class emulates a VarSupply object. <br>
    It provides a set voltage function, that sets the output of a VarSupply to the given voltage.
    """
    def __init__(self, address, pinAssignments, name):
        self.logger = logging.getLogger(__name__)
        self.ioExpander = PCAL6416(1, address)
        self.pinAssignments = pinAssignments
        self.name = name
        for pinAss in pinAssignments:
            self.ioExpander.setToOutputPinAssignment(pinAss)

    def setVoltage(self, voltage):
        # Convert voltage diff to int between 0 and 15
        self.logger.debug("Setting voltage in device " + self.name + " desired voltage: " + str(voltage) + " V")
        if(voltage != 3.5):
            voltage  = int((float(voltage) - 1.8) * 10 + 0.5)
        else:
            voltage = 0b1111

        if (voltage > 0b1111 or voltage < 0b0000):
            raise ValueError("Voltage not in range")

        for assignment in self.pinAssignments:
            if (assignment.type == "enable"):
                self.ioExpander.setVoltageHighOnPinAssignment(assignment)
            else:
                if ((voltage % 2) == 0):
                    self.ioExpander.setVoltageLowOnPinAssignment(assignment)
                else:
                    self.ioExpander.setVoltageHighOnPinAssignment(assignment)
                voltage = voltage >> 1
