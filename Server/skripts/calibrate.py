from flask_app.Driver.PCAL6416 import PCAL6416, PinAssignment
from flask_app.Driver.ADS8885 import ADS8885
from io import StringIO
import sys, getopt
from datetime import datetime
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
SPI_MOSI = 10
SPI_MISO = 9
SPI_CLK = 11

GPIO.setup(SPI_MOSI, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(SPI_MISO, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(SPI_CLK, GPIO.OUT, initial = GPIO.LOW)

#
measurementIoExpander = PCAL6416(0, 0b0100001)
cs1 = 8
cs2 = 7
cs3 = 5
cs4 = 6


""" Contains all ADS8885 measurement Devices. """
measurementDevices = {
     "vm1": ADS8885('vm1',
                0,
                PinAssignment(0, 4, "resolution"),
                PinAssignment(0, 5, "resolution"),
                measurementIoExpander,
                cs1,
                {}
          ),
    "vm2": ADS8885('vm2',
              0,
              PinAssignment(0, 6, "resolution"),
              PinAssignment(0, 7, "resolution"),
              measurementIoExpander,
              cs2,
              {}
              )
              ,
    "cm3":  ADS8885('cm3',
              1,
              PinAssignment(0, 0, "resolution"),
              PinAssignment(0, 1, "resolution"),
              measurementIoExpander,
              cs3,
              {}
         ),
    "cm4": ADS8885('cm4',
              1,
              PinAssignment(0, 2, "resolution"),
              PinAssignment(0, 3, "resolution"),
              measurementIoExpander,
              cs4,
              {}
         )
     }

devices = {}
outputFile = "";
GPIO.setwarnings(False)

def init(argv):

     devices = {}
     count = -1
     interval = 0
     outputFile = "masurement.csv"
     buffLength = 100000

     try:
         opts, args = getopt.getopt(argv,"d:o:b:n:t:",["device==","ofile=","buffer="])
     except getopt.GetoptError:
         print ('test.py -d <DeviceIdList> -o <outputfile> ')
         print("err")
         sys.exit(2)

     print(opts)
     for opt, arg in opts:
         if opt == '-h':
             print ('test.py -d <DeviceIdList> -o <outputfile>')

             print ('test.py -d "vm1,vm2,cm3,cm4" -o output.csv')
             sys.exit()

         elif opt in ("-d", "--device"):
             if(arg == "ALL" or arg == "all"):
                  devices = measurementDevices;
             else:
                 for name in arg.split(","):
                      if(name not in measurementDevices.keys()):
                            print("Could not find device: " + name)
                            sys.exit(2)
                      devices[name] = measurementDevices[name]

             inputfile = arg
         elif opt in ("-o", "--ofile"):
             outputFile = arg
         elif opt in ("-b", "--buffer"):
             buffLength = int(arg)
         elif opt in ("-t", "--time"):
             interval = float(arg)
         elif opt in ("-n", "--number"):
             count = int(arg)


     print ('Output file is: ' +  outputFile)
     print("Devices are: " + str(devices.keys()))
     print("Buffer length: " + str(buffLength))

     return outputFile, devices

def main(argv):


    outputFile, devices = init(argv)
    print("opening files: ")
    fileList = {}

    with open(outputFile + ".info", mode='w') as file:
         file.write("Format: ")
         for dev in devices.values():
              file.write(" ")
              file.write(dev.getName())
              file.write(",")

         file.write("Real Value")
         file.write("\n Starting measurement: \n")
         file.write(str(datetime.now()) + "\n")

    start_time = time.time()
    print("Range: ([5]V, [500]mV, [50]mV, [500u]A, [50m]A)")
    myRange = ""
    while(True):
        inp = input()
        myRange = inp
        if(inp =="5"):
            for dev in devices.values():
                dev.setResolution(3)
            break;
        elif(inp == "500"):
            for dev in devices.values():
                dev.setResolution(2)
            break;
        elif (inp == "50"):
            for dev in devices.values():
                dev.setResolution(1)
            break;
        elif(inp == "500u"):
            for dev in devices.values():
                dev.setResolution(1)
            break;
        elif(inp == "50m"):
            for dev in devices.values():
                dev.setResolution(2)
            break;
    print("starting measurement")

    with open(outputFile, mode='w') as file:

         try:
            while (True):
                print("Value: (extern)")
                inp = input()
                value = 0;
                if(inp == "end"):
                    break;
                elif inp.replace('.','',1).isdigit():
                    value = float(inp)
                else:
                    print("unknown value")
                    continue;
                for dev in devices.values():
                    val = 0
                    for i in range(50):
                        val = val + dev.getVoltageFast()
                    val = val / 50
                    print("read value: " + str(val))
                    file.write(str(val))
                    file.write(",")

                file.write(str(value))

                file.write(";\n")

         except KeyboardInterrupt:
                print('interrupted!')

    endTime = time.time()

    with open(outputFile + ".info", mode='a') as file:
         file.write("\n Measurement Done: \n")
         file.write(str(datetime.now()) + "\n")

         num_lines = sum(1 for line in open(outputFile)) - 1

         file.write("Execution time: " + str(endTime - start_time) + " s \n")
         file.write("Items: " + str(num_lines) + " \n")
         file.write("Speed: " + str(num_lines/(endTime - start_time)) + " Lines/s \n");
         file.write("Speed: (Samples / s) " + str(num_lines/(endTime - start_time) * len(devices.keys())) + " Samples/s \n");

         file.write("\nRange:: " + str(myRange));

    print("done");


if __name__ == "__main__":
    main(sys.argv[1:])
