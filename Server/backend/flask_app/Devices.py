""" Module that contain all devices used on the PCB """
from .Driver.LTC2631 import LTC2631
from .Driver.PCAL6416 import PCAL6416, PinAssignment
from .Driver.ADS8885 import ADS8885, ResolutionScaler
from .VarSupply import VarSupply


"""
    This file contains all the Device configuration used to measure voltage/current or supply voltages.
"""

measurementIoExpander = PCAL6416(0, 0b0100001)
cs1 = 8
cs2 = 7
cs3 = 5
cs4 = 6

resolutionScalersVm1 = {
    # 5V
    3: ResolutionScaler(2.3361, -0.11733),
    # 50mV
    1: ResolutionScaler(25.4362, -3.44427),
    # 500mV
    2: ResolutionScaler(255.016, -13.7671)
}

resolutionScalersVm2 = {
    # 5V
    3: ResolutionScaler(2.3535, 0.04193),
    1: ResolutionScaler(25.4852, -2.2547),
    2: ResolutionScaler(255.394, 4.3131)
}

resolutionScalersCm3 = {
    # 500uA
    1: ResolutionScaler(242.9322, -0.47838),
    # 50mA
    2: ResolutionScaler(44.9391, -0.0085668)
}

resolutionScalersCm4 = {

    2: ResolutionScaler(45.60521, -0.33778),
    1: ResolutionScaler(241.4526, -2.2501)
}


measurementDevices = {
    "vm1": ADS8885('vm1',
            0,
            PinAssignment(0, 4, "resolution"),
            PinAssignment(0, 5, "resolution"),
            measurementIoExpander,
            cs1,
            resolutionScalersVm1
        ),
   "vm2": ADS8885('vm2',
           0,
           PinAssignment(0, 6, "resolution"),
           PinAssignment(0, 7, "resolution"),
           measurementIoExpander,
           cs2,
           resolutionScalersVm2
           )
           ,
   "cm3":  ADS8885('cm3',
           1,
           PinAssignment(0, 0, "resolution"),
           PinAssignment(0, 1, "resolution"),
           measurementIoExpander,
           cs3,
           resolutionScalersCm3
       ),
   "cm4": ADS8885('cm4',
           1,
           PinAssignment(0, 2, "resolution"),
           PinAssignment(0, 3, "resolution"),
           measurementIoExpander,
           cs4,
           resolutionScalersCm4
       )
    }
""" Contains all ADS8885 measurement Devices, that are built onto the board. This Object is used in the server.py file"""

bodyBiasingControl = LTC2631(address = 0b0010000)
bodyBiasingNegControl = LTC2631(address = 0b0010001)
precisionSupply1Control = LTC2631(address = 0b0010010)
precisionSupply2Control = LTC2631(address= 0b0010011)


LTCDevices = {
    "BBP": bodyBiasingControl,
    "BBN": bodyBiasingNegControl,
    "PS1": precisionSupply1Control,
    "PS2": precisionSupply2Control
}
""" Voltage supplies that use an LTC chip. This Object is used in the server.py file """



pinAssignements1 = [
    PinAssignment(0, 0, "enable"),
    PinAssignment(0, 1, "voltageOut"),
    PinAssignment(0, 2, "voltageOut"),
    PinAssignment(0, 3, "voltageOut"),
    PinAssignment(0, 4, "voltageOut")
]
pinAssignements2 = [
    PinAssignment(0, 5, "enable"),
    PinAssignment(0, 6, "voltageOut"),
    PinAssignment(0, 7, "voltageOut"),
    PinAssignment(1, 0, "voltageOut"),
    PinAssignment(1, 1, "voltageOut")

]
pinAssignements3 = [
    PinAssignment(1, 2, "enable"),
    PinAssignment(1, 3, "voltageOut"),
    PinAssignment(1, 4, "voltageOut"),
    PinAssignment(1, 5, "voltageOut"),
    PinAssignment(1, 6, "voltageOut")
]


varSupplies = {
    "1": VarSupply(0b0100000, pinAssignements1, "VarSupply1"),
    "2": VarSupply(0b0100000, pinAssignements2, "VarSupply2"),
    "3": VarSupply(0b0100000, pinAssignements3, "VarSupply3")
}
""" Voltage supplies that do not use an LTC chip but are controlled using IO Pins from the IO Expander """
