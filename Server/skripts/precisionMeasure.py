import sys
sys.path.insert(0, "../flask_app")

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
                cs1
          ),
    "vm2": ADS8885('vm2',
              0,
              PinAssignment(0, 6, "resolution"),
              PinAssignment(0, 7, "resolution"),
              measurementIoExpander,
              cs2
              )
              ,
    "cm3":  ADS8885('cm3',
              1,
              PinAssignment(0, 0, "resolution"),
              PinAssignment(0, 1, "resolution"),
              measurementIoExpander,
              cs3
         ),
    "cm4": ADS8885('cm4',
              1,
              PinAssignment(0, 2, "resolution"),
              PinAssignment(0, 3, "resolution"),
              measurementIoExpander,
              cs4
         )
     }

devices = {}
outputFile = "";

def init(argv):

     devices = {}
     count = -1
     interval = 0
     outputFile = "masurement.csv"
     buffLength = 100000

     try:
         opts, args = getopt.getopt(argv,"d:o:b:n:t:",["device==","ofile=","buffer="])
     except getopt.GetoptError:
         print ('test.py -d <DeviceIdList> -o <outputfile> -n <SamplesToTake> -t <TimeDelayBetweenSamples>')
         print("err")
         sys.exit(2)

     print(opts)
     for opt, arg in opts:
         if opt == '-h':
             print ('test.py -d <DeviceIdList> -o <outputfile> -n <SamplesToTake> -t <TimeDelayBetweenSamples>')
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

     return outputFile, devices, buffLength,count, interval

def main(argv):

    outputFile, devices, buffLength, count, interval = init(argv)
    print("opening files: ")
    fileList = {}
    buffer = StringIO();

    for dev in devices.values():
          buffer.write(dev.getName())
          buffer.write(",")

    buffer.write("; \n")

    #
    # for dev in devices.keys():
    #      fileList[dev] = open(outputFile + dev + ".csv", mode='w')
    #      buffer[dev] =  StringIO();

    with open(outputFile + ".info", mode='w') as file:
         file.write("Format: ")
         for dev in devices.values():
              file.write("    ")
              file.write(dev.getName())
         file.write("\n Starting measurement: \n")
         file.write(str(datetime.now()) + "\n")

    start_time = time.time()
    print("starting measurement")

    with open(outputFile, mode='w') as file:
         try:
            while (count > 0 or count == -1):
                for dev in devices.values():
                    file.write(str(dev.getVoltageFast()))
                    file.write(",")

                if(count > 0):
                    count -=1;

                if(interval > 0):
                    print("Got measurement")
                    time.sleep(interval)

                file.write(";\n")

         except KeyboardInterrupt:
                print('interrupted!')
                if(buffLength > 0):
                    file.write(buffer.getvalue())

    endTime = time.time()

    with open(outputFile + ".info", mode='a') as file:
         file.write("\n Measurement Done: \n")
         file.write(str(datetime.now()) + "\n")

         num_lines = sum(1 for line in open(outputFile)) - 1

         file.write("Execution time: " + str(endTime - start_time) + " s \n")
         file.write("Items: " + str(num_lines) + " \n")
         file.write("Speed: " + str(num_lines/(endTime - start_time)) + " Lines/s \n");
         file.write("Speed: (Samples / s) " + str(num_lines/(endTime - start_time) * len(devices.keys())) + " Samples/s \n");
         file.write("Buffer length: " + str(buffLength));


    print("done");


if __name__ == "__main__":
    main(sys.argv[1:])
