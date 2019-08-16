import sys
sys.path.insert(0, "../backend/")


from flask_app.Driver.PCAL6416 import PCAL6416, PinAssignment
from flask_app.Driver.ADS8885 import ADS8885, ResolutionScaler
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
    # # if(self.name == "vm1"):
    # #     return value * 2.3307 - 0.1192 #* 3.133 - 40.6;
    # # elif(self.name == "vm2"):
    # #     return value * 2.3487 + 0.0375 #* 3.133 - 40.6;
    # # return value;
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


""" Contains all ADS8885 measurement Devices. """
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
devices = {}
outputFile = "";

def init(argv):

     devices = {}
     count = -1
     interval = 0
     outputFile = "masurement.csv"

     try:
         opts, args = getopt.getopt(argv,"d:o:n:t:",["device==","ofile=","samples=","timedelta="])
     except getopt.GetoptError:
         print ('powerlog.py -d <DeviceIdList> -o <outputfile> -n <SamplesToTake> -t <TimeDelayBetweenSamples>')
         print("err")
         sys.exit(2)

     for opt, arg in opts:
         if opt == '-h':
             print ('powerlog.py -d <DeviceIdList> -o <outputfile> -n <SamplesToTake> -t <TimeDelayBetweenSamples>')
             print ('e.g. powerlog.py -d <vm1,vm2> -o measure.csv -n 10000 -t 0')
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
         elif opt in ("-t", "--time"):
             interval = float(arg)
         elif opt in ("-n", "--number"):
             count = int(arg)


     print ('Output file is: ' +  outputFile)
     print("Devices are: " + str(devices.keys()))

     return outputFile, devices, count, interval


def setRange(devs):
    for dev in devs:
        while(True):
            print("Select Range for Device: " + str(dev.getName()))
            print("Range: ([5]V, [500]mV, [50]mV, [500u]A, [50m]A)")
            inp = input()
            myRange = inp
            if(inp =="5"):
                dev.setResolution(3)
                return
            elif(inp == "500"):
                dev.setResolution(2)
                return
            elif (inp == "50"):
                dev.setResolution(1)
                return
            elif(inp == "500u"):
                dev.setResolution(1)
                return
            elif(inp == "50m"):
                dev.setResolution(2)
                return
            elif(inp == "end"):
                print("\n\n                                  \n   (                (             \n ( )\\ (      (    ( )\\ (      (   \n )((_))\\ )  ))\\   )((_))\\ )  ))\\  \n((_)_(()/( /((_) ((_)_(()/( /((_) \n | _ ))(_)|_))    | _ ))(_)|_))   \n | _ \\ || / -_)   | _ \\ || / -_)  \n |___/\\_, \\___|   |___/\\_, \\___|  \n      |__/             |__/       \n\n")
                sys.exit(2)

def main(argv):
#    print("\n\n ____  __.                                                   __           .__        __     \n|    |/ _|___________    ______ ______ ____   ______   _____|  | _________|__|______/  |_   \n|      < \\_  __ \\__  \\  /  ___//  ___// __ \\ /  ___/  /  ___/  |/ /\\_  __ \\  \\____ \\   __\\  \n|    |  \\ |  | \\// __ \\_\\___ \\ \\___ \\\\  ___/ \\___ \\   \\___ \\|    <  |  | \\/  |  |_> >  |    \n|____|__ \\|__|  (____  /____  >____  >\\___  >____  > /____  >__|_ \\ |__|  |__|   __/|__|    \n        \\/           \\/     \\/     \\/     \\/     \\/       \\/     \\/          |__|           \n                      .__                                                                   \n  _____  __ __   ____ |  |__   __  _  ________  _  __                                       \n /     \\|  |  \\_/ ___\\|  |  \\  \\ \\/ \\/ /  _ \\ \\/ \\/ /                                       \n|  Y Y  \\  |  /\\  \\___|   Y  \\  \\     (  <_> )     /                                        \n|__|_|  /____/  \\___  >___|  /   \\/\\_/ \\____/ \\/\\_/                                         \n      \\/            \\/     \\/                                                               \n                      .__                          .__                                      \n  _____  __ __   ____ |  |__     ____  ____   ____ |  |                                     \n /     \\|  |  \\_/ ___\\|  |  \\  _/ ___\\/  _ \\ /  _ \\|  |                                     \n|  Y Y  \\  |  /\\  \\___|   Y  \\ \\  \\__(  <_> |  <_> )  |__                                   \n|__|_|  /____/  \\___  >___|  /  \\___  >____/ \\____/|____/                                   \n      \\/            \\/     \\/       \\/                                                      \n                      .__                __          _____  _____                           \n  _____  __ __   ____ |  |__     _______/  |_ __ ___/ ____\\/ ____\\                          \n /     \\|  |  \\_/ ___\\|  |  \\   /  ___/\\   __\\  |  \\   __\\\\   __\\                           \n|  Y Y  \\  |  /\\  \\___|   Y  \\  \\___ \\  |  | |  |  /|  |   |  |                             \n|__|_|  /____/  \\___  >___|  / /____  > |__| |____/ |__|   |__|                             \n      \\/            \\/     \\/       \\/                                                      \n                      .__        _____                 __                                   \n  _____  __ __   ____ |  |__   _/ ____\\____    _______/  |_                                 \n /     \\|  |  \\_/ ___\\|  |  \\  \\   __\\\\__  \\  /  ___/\\   __\\                                \n|  Y Y  \\  |  /\\  \\___|   Y  \\  |  |   / __ \\_\\___ \\  |  |                                  \n|__|_|  /____/  \\___  >___|  /  |__|  (____  /____  > |__|                                  \n      \\/            \\/     \\/              \\/     \\/                                        \n                      .__      .__                                                      .___\n  _____  __ __   ____ |  |__   |__| _____ _____________   ____   ______ ______ ____   __| _/\n /     \\|  |  \\_/ ___\\|  |  \\  |  |/     \\\\____ \\_  __ \\_/ __ \\ /  ___//  ___// __ \\ / __ | \n|  Y Y  \\  |  /\\  \\___|   Y  \\ |  |  Y Y  \\  |_> >  | \\/\\  ___/ \\___ \\ \\___ \\\\  ___// /_/ | \n|__|_|  /____/  \\___  >___|  / |__|__|_|  /   __/|__|    \\___  >____  >____  >\\___  >____ | \n      \\/            \\/     \\/           \\/|__|               \\/     \\/     \\/     \\/     \\/ \n\n")

    outputFile, devices, count, interval = init(argv);

    folder, devices, count, interval = init(argv)
    devs = list(devices.values());

    setRange(devs);
    start_time = time.time()
    print("Writing to file: " + outputFile)
    lastDev = devs[-1]


    with open(outputFile, mode='w') as file:

        for dev in devs:
            file.write(dev.getName())
            if (dev != lastDev):
                file.write(",")

        file.write("; \n")

        while(count != 0):
            for dev in devs:
                value = dev.scaleToResolution(dev.getVoltage())
                file.write(str(value))
                if(dev != lastDev):
                    file.write(",")
            file.write(";\n")
        #    print("got value: " + str(value) + " unit: " +  dev.getUnit());

            if(interval != 0):
                time.sleep(interval)
            if(count != -1):
                count = count - 1;

    endTime = time.time()
    #print("         ,---.    .--.     .---. .-. .-.,---.    ,---.           ,---.  .-. .-. _______   ,'|\"\\    .---.  .-. .-.,---.   \n|\\    /| | .-'   / /\\ \\   ( .-._)| | | || .-.\\   | .-'  |\\    /| | .-'  |  \\| ||__   __|  | |\\ \\  / .-. ) |  \\| || .-'   \n|(\\  / | | `-.  / /__\\ \\ (_) \\   | | | || `-'/   | `-.  |(\\  / | | `-.  |   | |  )| |     | | \\ \\ | | |(_)|   | || `-.   \n(_)\\/  | | .-'  |  __  | _  \\ \\  | | | ||   (    | .-'  (_)\\/  | | .-'  | |\\  | (_) |     | |  \\ \\| | | | | |\\  || .-'   \n| \\  / | |  `--.| |  |)|( `-'  ) | `-')|| |\\ \\   |  `--.| \\  / | |  `--.| | |)|   | |     /(|`-' /\\ `-' / | | |)||  `--. \n| |\\/| | /( __.'|_|  (_) `----'  `---(_)|_| \\)\\  /( __.'| |\\/| | /( __.'/(  (_)   `-'    (__)`--'  )---'  /(  (_)/( __.' \n'-'  '-'(__)                                (__)(__)    '-'  '-'(__)   (__)                       (_)    (__)   (__)     ")
    print("done");

    print.write("\n Measurement Done: \n")
    print.write(str(datetime.now()) + "\n")

    num_lines = sum(1 for line in open(outputFile)) - 1

    print("Execution time: " + str(endTime - start_time) + " s \n")
    print("Items: " + str(num_lines) + " \n")
    print("Speed: " + str(num_lines/(endTime - start_time)) + " Lines/s \n");
    print("Speed: (Samples / s) " + str(num_lines/(endTime - start_time) * len(devices.keys())) + " Samples/s \n");

if __name__ == "__main__":
    main(sys.argv[1:])
