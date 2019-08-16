# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""Entry point for the server application."""
import threading
import json
import logging
from pylogging import HandlerType, setup_logger
import time
import os
import sys


from flask_cors import CORS
from .config import CONFIG
import traceback
from flask import request, jsonify, current_app, Flask
from flask_jwt_simple import (
    JWTManager, jwt_required, create_jwt, get_jwt_identity
)

from .http_codes import Status
from flask import make_response

from datetime import timedelta, datetime
from functools import update_wrapper


logger = logging.getLogger(__name__)
setup_logger(log_directory='./logs', file_handler_type=HandlerType.ROTATING_FILE_HANDLER, allow_console_logging = True, console_log_level  = logging.DEBUG, max_file_size_bytes = 1000000)


try:
    import RPi.GPIO as GPIO
    from pijuice import PiJuice # Import pijuice module
    import rpi_backlight as backlight
    simul = False
except ImportError:
    simul = True
    logger.error("could not import GPIO")

# import cv2
#
# cap = cv2.VideoCapture(0)

if(simul == False):
    GPIO.setmode(GPIO.BCM)


# Import used Devices, must be here because GPIO Mode has to be set first
from .Devices import varSupplies, LTCDevices, measurementDevices

SPI_MOSI = 10
SPI_MISO = 9
SPI_CLK = 11

if(simul == False):
    GPIO.setup(SPI_MOSI, GPIO.OUT, initial = GPIO.LOW)
    GPIO.setup(SPI_MISO, GPIO.OUT, initial = GPIO.LOW)
    GPIO.setup(SPI_CLK, GPIO.OUT, initial = GPIO.LOW)

mutex = threading.Lock()
# Create Flask App
app = Flask(__name__)
# Load Configuration for app. Secret key etc.
config_name = os.getenv('FLASK_CONFIGURATION', 'default')
app.config.from_object(CONFIG[config_name])

# Set Cors header. Used to accept connections from browser using XHTTP requests.
CORS(app, headers=['Content-Type'])
jwt = JWTManager(app)


 # Object to store the last measured voltage values
voltageValues = {}
voltageValuesSum = {}

#Pin Code
pinCode = app.config["PIN_CODE"]

#Polling time delay for Polling thread
pollingTimeDelay = app.config["POLLING_TIME_DELAY"]


if(not simul):
    pijuice = PiJuice(1, 0x14) # Instantiate PiJuice interface object
#init values
for dev in measurementDevices.keys():
    obj = {
        "value" : 0,
        "unit" : "",
        "max": ""
    }
    voltageValues[dev] = obj;

""" Path to config file (.json) for frontend """
CONF_FILE = os.path.join(os.path.dirname(__file__), 'conf.json')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'output.csv')
EXPORT_FOLDER = os.path.join(os.path.dirname(__file__), '../export/')

@jwt.jwt_data_loader
def add_claims_to_access_token(identity):
    now = datetime.utcnow()
    return {
        'exp': now + current_app.config['JWT_EXPIRES'],
        'iat': now,
        'nbf': now,
        'sub': identity,
        'roles': 'Admin'
    }


def crossdomain(origin=None, methods=None, headers=None, max_age=21600,
                attach_to_all=True, automatic_options=True):
    """Decorator function that allows crossdomain requests.
      Courtesy of
      https://blog.skyred.fi/articles/better-crossdomain-snippet-for-flask.html
    """
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    # use str instead of basestring if using Python 3.x
    if headers is not None and not isinstance(headers, list):
        headers = ', '.join(x.upper() for x in headers)
    # use str instead of basestring if using Python 3.x
    if not isinstance(origin, list):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        """ Determines which methods are allowed
        """
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        """The decorator function
        """
        def wrapped_function(*args, **kwargs):
            """Caries out the actual cross domain code
            """
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator



#-------------------------------------------------------------------------------
#                       BEGIN API Functions
#-------------------------------------------------------------------------------
@app.route('/api/storeconfig', methods=['POST', 'OPTIONS'])
@crossdomain(origin = '*')
@jwt_required
def storeConfig():
    """
        ### API Path   `/api/storeconfig`
        ### Request Type: `POST`
        Stores the given JSON Object in the Config file specifed by the  CONF_FILE variable.
        If the JWT Cookie is not set, this method will return Status Code 401 UNAUTHORIZED.
        Return Status Code 500 if the file could not be opened.
    """
    try:
        storeConfigObject(request.get_json())
    except IOError as e:
        error = "I/O Error " + str(e.errno) + " " + str(e.strerror)
        logger.error(error)
        return error , Status.HTTP_SERVER_ERROR;

    return "OK", Status.HTTP_OK_BASIC


@app.route('/api/loadconfig', methods=['GET', 'OPTIONS'])
@crossdomain(origin = '*')
def loadConfig():
    """
    ### API Path   `/api/loadconfig`
    ### Request Type: `GET`
    Loads the configuration specified in the CONF_FILE file.
    Returns a JSON Object with all Configurations that are defined."""
    try:
        with open(CONF_FILE,'r') as file:
            return file.read(), Status.HTTP_OK_BASIC
    except IOError as e:
        error = "I/O Error " + str(e.errno) + " " + str(e.strerror)
        logger.error(error)
        return error, Status.HTTP_SERVER_ERROR;

    return "Unknown Error", Status.HTTP_SERVER_ERROR;



@app.route('/api/update/chartConfig', methods=['POST', 'OPTIONS'])
@crossdomain(origin = '*')
@jwt_required
def updateChartconfig():
    """
    ### API Path   `/api/update/chartConfig`
    ### Request Type: `POST`
    Updates the device Config stored in the CONF_FILE.
    Make sure that the JSON Object supplied in the body matches the specification for a Chart config.
    ### POST Body
    ```
    [
  {
    "name": "Voltage chart",
    "col": {
      "sm": 12,
      "md": 12,
      "lg": 6,
      "xs": 12
    },
    "datasets": [
      {
        "name": "Voltage vm1",
        "autoLabel": true,
        "negRange": false,
        "chartDataset": {
          "currValue": 3.15,
          "borderColor": "#0618f9",
          "fill": false,
          "yAxisID": "yAxis1",
          "label": "Voltage vm1[V]"
        },
        "borderColor": "#2196f3",
        "customDataHandlerEnabled": false,
        "unit": "V",
        "handler": "",
        "datasetId": "ADS1dataset",
        "sourceId": "vm1",
        "autoRange": true
      },
      {
        "name": "Voltage vm2",
        "negRange": false,
        "chartDataset": {
          "currValue": 4.28,
          "borderColor": "#44a0bb",
          "fill": false,
          "yAxisID": "yAxis2",
          "label": "Voltage vm2[V]"
        },
        "lineColor": "#ff0000",
        "autoLabel": true,
        "customDataHandlerEnabled": false,
        "unit": "V",
        "handler": "",
        "datasetId": "ADS2dataset",
        "sourceId": "vm2",
        "autoRange": true
      }
    ],
    "axes": [
      {
        "position": "left",
        "id": "yAxis1"
      },
      {
        "position": "right",
        "id": "yAxis2"
      }
    ],
    "maxValues": 40,
    "chartId": "Chart#1"
  },
  {
    "name": "Current Chart",
    "col": {
      "sm": 12,
      "md": 12,
      "lg": 6,
      "xs": 12
    },
    "datasets": [
      {
        "name": "Current [cm3]",
        "autoLabel": true,
        "chartDataset": {
          "yAxisID": "leftAxis",
          "lineColor": "#2196f3",
          "label": "Current [cm3][uA]",
          "currValue": 193.87,
          "borderColor": "#e03105",
          "fill": false
        },
        "lineColor": "#2196f3",
        "customDataHandlerEnabled": false,
        "unit": "uA",
        "handler": "",
        "sourceId": "cm3",
        "autoRange": true
      },
      {
        "name": "Current [cm4]",
        "autoLabel": true,
        "chartDataset": {
          "currValue": 335.78,
          "borderColor": "#d89552",
          "fill": false,
          "yAxisID": "rightAxis",
          "label": "Current [cm4][uA]"
        },
        "customDataHandlerEnabled": false,
        "unit": "uA",
        "handler": "",
        "datasetId": "dataset-1558781553872",
        "sourceId": "cm4",
        "autoRange": true
      }
    ],
    "axes": [
      {
        "position": "left",
        "id": "leftAxis"
      },
      {
        "position": "right",
        "id": "rightAxis"
      }
    ],
    "maxValues": 40,
    "chartId": "Chart#2"
  }
]
    ```
    """
    params = request.get_json()
    print(json.dumps(params, indent=2, sort_keys=False))
    try:
        config_object = getConfigObject()
        config_object['charts'] = params
        storeConfigObject(config_object)
    except IOError as e:
        error = "I/O Error " + str(e.errno) + " " + str(e.strerror)
        logger.error(error);
        return error , Status.HTTP_SERVER_ERROR;

    return "OK", 200;

@app.route('/api/update/measurementDevices', methods=['POST', 'OPTIONS'])
@crossdomain(origin = '*')
@jwt_required
def updateDevs():
    """
    ### API Path   `/api/update/measurementDevices`
    ### Request Type: `POST`
    Updates the configiruation of the measurements devices supplied in the requests body. <br>
    JSON Body must follow the following format:
    ### POST Body
    ```
    [
     {
      "deviceId":<String>,
      "currentResolution":<int>,
      "desiredResolution":<int>,
      "autoResolution":<true|false>
     }
    ]
    ```
    """
    #params are the new values
    params = request.get_json()

    try:
        #get the old/stored values
        config_object = getConfigObject()
    except IOError as e:
        error = "I/O Error " + str(e.errno) + " " + str(e.strerror)
        logger.error(error);
        return error , Status.HTTP_SERVER_ERROR;

    devices = config_object["devices"]
    logger.debug("Got Params:")
    logger.debug(json.dumps(params, indent=2, sort_keys=False))

    for dev in params:
        try:
            id = dev["deviceId"]
            if(id in measurementDevices.keys()): #check whether id is valid
                oldResolution=dev["currentResolution"]
                newResolution=dev["desiredResolution"]
                newautoResolution=dev["autoResolution"]
                measurementDevices[id].setResolution(int(newResolution))
                measurementDevices[id].setAutoResolution(bool(newautoResolution))

                for dev in devices:
                    if (dev["deviceId"] == id):
                        dev["currentResolution"] = int(newResolution) #müsste das nicht ein string sein???
                        dev["autoResolution"]=bool(newautoResolution)
            else:
                logger.error("Device " + str(id) + " not found")
                return "Device " + str(id) + " not found", Status.HTTP_BAD_REQUEST
        except ValueError as e:
            logger.error(str(e))
            return str(e), Status.HTTP_BAD_REQUEST



    try:
        storeConfigObject(config_object)
    except IOError as e:
        error = "I/O Error " + str(e.errno) + " " + str(e.strerror)
        logger.error(error)
        return error , Status.HTTP_SERVER_ERROR


    return "" , Status.HTTP_OK_BASIC


@app.route('/api/login', methods=['POST', 'OPTIONS'])
@crossdomain(origin = '*')
def login():
    """
        ### API Path   `/api/login`
        ### Request Type: `POST`
        Logs in an user. checks if the password supplied in the json body matches the pincode.
        If Login is successfully returns a jwt token used to authenticate the user.
        JSON Format:
        ### POST Body
        ```
        {
            password:<string>
        }
        ```
    """
    params = request.get_json()
    password = params.get('password', None)

    #Check if inputs are valid
    if not password:
        logger.info('Password not set!')
        return jsonify({"msg": "Missing Pincode parameter"}), Status.HTTP_BAD_REQUEST

    if password != pinCode:
        logger.info('Pincode was wrong')
        return jsonify({"msg": "Wrong Pincode"}), Status.HTTP_BAD_UNAUTHORIZED

    token = {'jwt': create_jwt(identity="admin"), 'exp': datetime.utcnow() + current_app.config['JWT_EXPIRES']}
        # id: number;
        # username: string;
        # password: string;
        # firstName: string;
        # lastName: string;
        # token?: string;
    ret = {"id": "NewUser", "token": token}

    logger.info('Login successfully ' + str(ret))
    return jsonify(ret), Status.HTTP_OK_BASIC



@app.route("/api/logout", methods=['POST', 'OPTIONS'])
@jwt_required
@crossdomain(origin='*')
def logout():
    """
    ### API Path   `/api/logout`
    ### Request Type: `POST`
    Logs out an user, JWT Token must be set, otherwise Token invalid is returned
    """
    identity = get_jwt_identity()
    if not identity:
        return jsonify({"msg": "Token invalid"}), Status.HTTP_BAD_UNAUTHORIZED
    logger.info('Logged out user !!')
    return 'logged out successfully', Status.HTTP_OK_BASIC


@app.route('/api/voltageUpdate/<deviceId>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def voltageUpdate(deviceId):
    """
    ### API Path   `/api/voltageUpdate/<deviceId>`
    ### Request Type: `GET`
    Requests the curremt voltage/Current for a device.
    <deviceId> must match the deviceId whose value we want to know (e.g VM1, CM3).
    If ALL is used as Device Id, all Values will be returned"""
    logger.info('Volt update requested for device id: ' + deviceId)

    if(deviceId == "ALL"):
        mutex.acquire()
        ret = jsonify(voltageValues)
        mutex.release()
        return ret, Status.HTTP_OK_BASIC

    try:
        mutex.acquire()
        ret = voltageValues[deviceId]
        mutex.release()
        return ret, Status.HTTP_OK_BASIC

    except KeyError:
        return "Device Id not Found", Status.HTTP_BAD_REQUEST



@app.route('/api/getSystemInfos', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def getSystemInfos():
    """
    ### API Path   `/api/getSystemInfos`
    ### Request Type: `GET`
    Return information about the system.
    ###Returns:
    ```
    {
        battery: {
            value: <value>,
            charging: <bool>
        },
        temp: <string>
    }
    ```
    """

    data = {}

    data["battery"] = {}
    # return (temp.replace("temp=",""))
    if(simul):
        data["battery"]["value"] = "33"
        data["battery"]["charging"] = "false"
        data["temp"] = "12C"
        return jsonify(data), Status.HTTP_OK_BASIC


    temp = os.popen("vcgencmd measure_temp").readline()
    data["temp"] = temp
    status = pijuice.status.GetStatus()
    if(status["error"] != "NO_ERROR"):
        print("Error while getting pijuice status" + str(status["error"]))
        return status["error"], Status.HTTP_SERVER_ERROR;

    charge = pijuice.status.GetChargeLevel()
    if(charge["error"] != "NO_ERROR"):
        print("Error while getting pijuice status" + str(charge["error"]))
        return charge["error"], Status.HTTP_SERVER_ERROR;
    charging = "true" if (status["data"]["powerInput"] == "PRESENT") else "false"
    data["battery"]["value"] = str(charge["data"]);
    data["battery"]["charging"] = charging

    return jsonify(data), Status.HTTP_OK_BASIC



@app.route('/api/updateDeviceVoltages', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
@jwt_required
def updateAllDevices():
    """
        ### API Path   `/api/updateDeviceVoltages`
        ### Request Type: `POST`
        Updates the voltage of a List of supply devices.
        The deviceids, type of the device and desired voltage must be sent in the post body.
        e.g. Sets voltage of Varsupply-1 and 2
        ### POST Body
        ```
        [
            { "type" = "varsupply",
              "id" = 1,
              "desiredVoltage" = 2.5
            },
            { "type" = "varsupply",
              "id" = 2,
              "desiredVoltage" = 1.8
            }
        ]
        ```
    """
    logger.debug(json.dumps(request.get_json(), indent=2, sort_keys=False))
    logger.info(json.dumps(request.get_json(), indent=2, sort_keys=False))
    params = request.get_json()
    for dev in params:
        try:
            if(not _setVoltageOnDevice(dev["enabled"], dev["type"], dev["id"], dev["desiredVoltage"])):
                return "Device not found or voltage not valid", Status.HTTP_BAD_REQUEST
        except KeyError as e:
            logger.error(str(e))
            return "An internal error ocurred " + str(e), Status.HTTP_BAD_REQUEST
        except ValueError as e:
            logger.error(str(e))
            return "Invalid Value: " + str(e), Status.HTTP_BAD_REQUEST

    return 'Voltages Set', Status.HTTP_OK_BASIC



@app.route('/api/setVoltageOnDevice/<deviceType>/<deviceNumber>/<voltage>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def setVoltageOnDevice(deviceType, deviceNumber, voltage):
    """
    ### API Path   `/api/setVoltageOnDevice/<deviceType>/<deviceNumber>/<voltage>`
    ### Request Type: `GET`
    Sets the value of one Voltage supply. Mostly used internally. recommended to use /api/updateDeviceVoltages """
    try:
        if(not _setVoltageOnDevice(True, deviceType, deviceNumber, voltage, False)):
            return "Device not found or voltage not valid", Status.HTTP_BAD_REQUEST

    except KeyError as e:
        logger.error(str(e))
        return "An internal error ocurred " + str(e), Status.HTTP_BAD_REQUEST
    except ValueError as e:
        logger.error(str(e))
        return "Invalid Value: " + str(e), Status.HTTP_BAD_REQUEST

    return "Voltage Set successfully", Status.HTTP_OK_BASIC


@app.route('/api/shutdown', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
@jwt_required
def shutdown():
    """
    ### API Path   `/api/shutdown`
    ### Request Type: `GET`
    Shuts the device down """
    # Shutting down$
    if(simul):
        return "Shuting down...", Status.HTTP_OK_BASIC
    command = "/usr/bin/sudo /sbin/shutdown now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    return output, Status.HTTP_OK_BASIC


@app.route('/api/updateGeneralSettings', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
@jwt_required
def updateGeneralSettings():
    """
    ### API Path   `/api/updateGeneralSettings`
    ### Request Type: `POST`
    Changes general settings. Currently only brightness is possible """
    logger.debug(json.dumps(request.get_json(), indent=2, sort_keys=False))
    params = request.get_json()
    if(simul):
        return 'Simulation', Status.HTTP_OK_BASIC;

    brightness = int(params["brightness"])

    if(brightness > 255 or brightness < 0):
        return "Invalid Range for brightness", Status.HTTP_BAD_REQUEST

    backlight.set_brightness(brightness)

    return 'Changes Applied', Status.HTTP_OK_BASIC

@app.route('/api/storeImage', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def storeImage():
    """
    ### API Path   `/api/storeImage`
    ### Request Type: `POST`
    Stores a base64 string as image locally on the Demonstrator
    ###Post Body:
    ```
    image: <base64DecodedImage>
    ```
    """
    # Todo security
    params = request.get_json()
    import base64
    print(params["image"][22:])
    imgdata = base64.b64decode(params["image"][22:])
    filename = "export_" + str(datetime.now().strftime('%Y%m-%d%H-%M%S')) + ".png"
    file = os.path.join(EXPORT_FOLDER, filename)
    with open(file, 'wb') as f:
        f.write(imgdata)
    return "OK", Status.HTTP_OK_BASIC


@app.route('/api/storeCsv', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def storeCsv():
    """
    ### API Path   `/api/storeCsv`
    ### Request Type: `POST`
    Stores the content of the request as .csv file
    ###Post Body:
    ```
    <csvContent>
    ```
    """
    # Todo security
    params = request.get_json()
    filename = "export_" + str(datetime.now().strftime('%Y%m-%d%H-%M%S')) + ".csv"
    file = os.path.join(EXPORT_FOLDER, filename)
    maxcount = len(params.keys())
    count = 0
    keys = params.keys();

    with open(file, 'w') as f:
        for dataId in keys:
            f.write(dataId)
            count += 1
            if(count != maxcount):
                f.write(",")
        f.write(";\n")
        for i in range(len(list(params.values())[0])):
            count = 0
            for key in keys:
                f.write(str(params[key][i]))
                count += 1
                if(count != maxcount):
                    f.write(",")
            f.write(";\n")

    # for i in range(0, len(params.s())):
    return "OK", Status.HTTP_OK_BASIC



#-------------------------------------------------------------------------------
#                      END API FUNCTIONS
#-------------------------------------------------------------------------------

class PollingThread(threading.Thread):
    """
    Thread that continually updates voltage values.
    Stores them in VoltageValues object.
    """

    def __init__ (self, devices, interval, threadId):
        threading.Thread.__init__(self)
        self.devices = devices
        self.interval = interval
        self.threadId = threadId
        self.daemon = True # Please kill our thread, when server is not running anymore

    # def run2(self):
    #
    #    while True:
    #      for dev in self.devices:
    #          voltageValues[dev.getName()] = str(dev.getVoltage()) # store voltage values in object.
    #          time.sleep(0.1)
    #
    #      time.sleep(self.interval)


    def run(self):
        """ Collects a predifined amount of sample values from all devices specifed in the devices variable, supplied by the constructor.
            Than averages it and stores the average in the global Conf Object.
            After that, the thread waits for a given time specified in the interval variable.
        """
        loops = 5

        while True:
            try:
                # reset sum values
                for dev in self.devices:
                    voltageValuesSum[dev.getName()] = 0

                for i in range(loops):
                    for dev in self.devices:
                        # voltage = dev.getVoltage()
                        # lastVal = voltage
                        voltageValuesSum[dev.getName()] += dev.getVoltage()

                for dev in self.devices:
                    if(voltageValuesSum[dev.getName()] is None):
                        continue

                    sum = voltageValuesSum[dev.getName()]
                    average = dev.scaleToResolution(sum/loops)
                    #   file.write(str(average) + dev.getUnit())
                    #   file.write(",")
                    # if (dev.getUnit() == "V" and average > 5.5 ):
                    #      logger.debug("got weird voltage!")
                    #      logger.error("Got weird voltage!!")
                    #      logger.debug(dev.getDebugInfos())
                    # logger.debug("got average values for: " + str(dev.getName()) + " av: " + str(average))
                    voltageValues[dev.getName()]["value"] = str(average) # store voltage values in object.
                    voltageValues[dev.getName()]["unit"] = dev.getUnit()
                    voltageValues[dev.getName()]["max"] = dev.getMaxRange()

                    if (dev.autoResolution):
                        # check if we reached upper resolution
                        if(dev.reachedResolutionMax(average) and not dev.maxResolution()):
                            logger.debug("Reached upper resolution limit")
                            currentresolution = dev.resolution
                            logger.debug("current  res: " + str(currentresolution))
                            dev.setResolution(currentresolution + 1)
                            logger.debug("changed to next higher resolution range")
                        # check for lower resolution
                        elif(dev.reachedResolutionMin(average) and not dev.minResolution()):
                            logger.debug("Reached lower resolution limit")
                            currentresolution = dev.resolution
                            logger.debug("current  res: " + str(currentresolution))
                            dev.setResolution(currentresolution-1)
                            logger.debug("changed to next lower resolution range")

            except IOError as e:
                logger.error("IO Error in thread")
                logger.error(e)
                # logger.debug(e)
                # file.write("got exception")
            except ValueError as e:
                # file.write("got exception")
                logger.error("Value Error in thread")
                logger.error(e)
                # logger.debug(e)
            except TypeError as e:
                # file.write("got exception")
                logger.error("Type Error in thread")
                logger.error(e)
                # logger.debug(e)
            except:
                # file.write("got exception")
                logger.error("Unexpected error:")
                logger.error(str(sys.exc_info()))
                raise
            finally:
                # file.write("\n")
                # file.flush();
                time.sleep(self.interval)

       # logger.debug("------------running----------")
       # while(True):
       #     mutex.acquire()
       #     for dev in self.devices:
       #           val = dev.getVoltage();
       #           average= dev.scaleToResolution(val)
       #           logger.debug("updatinmg values:" + str(average))
       #           voltageValues[dev.getName()]["value"] = str(average) # store voltage values in object.
       #           voltageValues[dev.getName()]["unit"] = dev.getUnit()
       #           voltageValues[dev.getName()]["max"] = dev.getMaxRange()
       #           # time.sleep(0.01)
       #     mutex.release()
       #     time.sleep(self.interval)

       # loops= 5
       # waitingTime= 0.01
       # maxStepAllowed = 0.1
       # with open(OUTPUT_FILE,'w') as file:
       #     for dev in self.devices:
       #         file.write(dev.getName())
       #         file.write(",")
       #     file.write(";\n")
       #     file.flush()
       #     while True:
       #         try:
       #             # i=0
       #             # while i<loops:
       #             for dev in self.devices:
       #                 maxStep = 0
       #                 lastVal = dev.getVoltage()
       #                 sum = dev.getVoltage()
       #                 for i in range(loops - 1):
       #                     # name= dev.getName()
       #                     voltage=dev.getVoltage()
       #                     print(str(voltage))
       #                     maxStep = max(abs(voltage-lastVal), maxStep)
       #                     lastVal = voltage
       #                     # if(i==0):
       #                     #     sum=0
       #                     # else:
       #                     #     sum=float(voltageValuesSum[name])
       #                     sum=sum+voltage
       #                     # voltageValuesSum[name] = str(sum) # store voltage values in object.
       #                 if(abs(maxStep) > maxStepAllowed):
       #                     print("step to big!")
       #                     voltageValuesSum[dev.getName()] = None
       #                 else:
       #                      voltageValuesSum[dev.getName()] = str(sum)
       #                 print("step:" + str(maxStep))
       #                 time.sleep(0.0001)
       #                 # i=i+1
       #             for dev in self.devices:
       #                 if(voltageValuesSum[dev.getName()] is None):
       #                     continue;
       #                 sum=float(voltageValuesSum[dev.getName()])
       #                 average= dev.scaleToResolution(sum/loops)
       #                 file.write(str(average) + dev.getUnit())
       #                 file.write(",")
       #                 if (dev.getUnit() == "V" and average > 5.5 ):
       #                     logger.debug("got weird voltage!")
       #                     logger.error("Got weird voltage!!")
       #                     logger.debug(dev.getDebugInfos())
       #                 logger.debug("got average values for: " + str(dev.getName()) + " av: " + str(average))
       #                 voltageValues[dev.getName()]["value"] = str(average) # store voltage values in object.
       #                 voltageValues[dev.getName()]["unit"] = dev.getUnit()
       #                 voltageValues[dev.getName()]["max"] = dev.getMaxRange()
       #
       #                 if(dev.autoResolution):
       #                     if(dev.reachedResolutionMax(average) and not dev.maxResolution()):
       #                         logger.debug("Reached upper resolution limit")
       #                         currentresolution=dev.resolution
       #                         logger.debug("current  res: " + str(currentresolution))
       #                         dev.setResolution(currentresolution+1)
       #                         logger.debug("changed to next higher resolution range")
       #
       #                     elif(dev.reachedResolutionMin(average) and not dev.minResolution()):
       #                         logger.debug("Reached lower resolution limit")
       #                         currentresolution=dev.resolution
       #                         logger.debug("current  res: " + str(currentresolution))
       #                         dev.setResolution(currentresolution-1)
       #                         logger.debug("changed to next lower resolution range")
       #
       #         except IOError as e:
       #              logger.error("IO Error in thread")
       #              logger.error(e)
       #              logger.debug(e)
       #              file.write("got exception")
       #         except ValueError as e:
       #              file.write("got exception")
       #              logger.error("Value Error in thread")
       #              logger.error(e)
       #              logger.debug(e)
       #         except TypeError as e:
       #              file.write("got exception")
       #              logger.error("Type Error in thread")
       #              logger.error(e)
       #              logger.debug(e)
       #         except:
       #              file.write("got exception")
       #              logger.error("Unexpected error:")
       #              logger.error(str(sys.exc_info()))
       #              raise
       #         finally:
       #              file.write("\n")
       #              file.flush();
       #              time.sleep(self.interval)
       #





def _setVoltageOnDevice(enabled, deviceType, deviceNumber, voltage, updateConfig = True):
    """ private function. Used to change voltage of a device.  <br>
    Set updateConfig to false, if you do not want to store the changes.
    """
    logger.info('setVoltageOnDevice ' + deviceType + " : " + deviceNumber + ":" + str(voltage) + "v")
    voltage = float(voltage)
    voltageSet = False

    if (deviceType == "VarSupply"):
        if deviceNumber in varSupplies.keys():
            if (not enabled):
                varSupplies[deviceNumber].disable()
            else:
                varSupplies[deviceNumber].setVoltage(voltage)
            voltageSet = True

    elif (deviceType == "PrecisionSupply"):
        devId = "PS" + deviceNumber
        if devId in LTCDevices.keys():
            if (not enabled):
                LTCDevices[devId].disable()
            else:
                LTCDevices[devId].setVoltage(voltage)
            voltageSet = True

    elif (deviceType == "BodyBias"):
        if deviceNumber in LTCDevices.keys():
            if (not enabled):
                LTCDevices[deviceNumber].disable()
            else:
                LTCDevices[deviceNumber].setVoltage(abs(voltage))
            voltageSet = True

    try:
        #get the old/stored values
        config_object = getConfigObject()
    except IOError as e:
        error = "I/O Error " + str(e.errno) + " " + str(e.strerror)
        logger.error(error);
        return False

    devices = config_object["supplies"]

    for dev in devices:
        if(dev["type"] == deviceType and dev["id"] == deviceNumber):
            dev["currentVoltage"] = voltage
            dev["enabled"] = enabled
            if ("maxFix" in dev.keys()):
                dev["maxValueChecked"] = (voltage == dev["maxFix"])
            #if(deviceType == "VarSupply" )

    try:
        storeConfigObject(config_object)
    except IOError as e:
        error = "I/O Error " + str(e.errno) + " " + str(e.strerror)
        logger.error(error)
        return False

    return voltageSet


def init():
    """
    Sets up initial values. <br>
    Reads current settings stored in config file. <br>
    Sets all supplies to the values specified in config file and sets resolution of measurement devices.    <br>
    ### Raises IoError if config is not found
    """

    #get the stored values
    config_object = getConfigObject()

    # Set resolutions of measurements
    for dev in  config_object["devices"]:
        id = dev["deviceId"]
        if(id in measurementDevices.keys()):
            measurementDevices[id].setResolution(int(dev["currentResolution"]))
            measurementDevices[id].setAutoResolution(int(dev["autoResolution"]))

    # Set supply voltages
    for dev in config_object["supplies"]:
        try:
            if not _setVoltageOnDevice(dev["enabled"], dev["type"], dev["id"], dev["currentVoltage"]):
                logger.error("Device not found or voltage not valid" + str(dev))
        except KeyError as e:
            logger.error(str(e))
        except ValueError as e:
            logger.error(str(e))



def main():
    """Main entry point of the app. <br>
    Starts local server and sets values stored in the conf.json file.
    """
    # logger.info("Beginning main")

    init()
    logger.info("starting server")

    voltagePoller = PollingThread(measurementDevices.values(), pollingTimeDelay, "Thread 1")
    logger.debug("starting polling thread")
    voltagePoller.start()
    logger.debug("Thread started")
    logger.debug("count: " + str(threading.active_count() ))
    try:
        app.run(debug=False, host = app.config["IP"], port = app.config["PORT"])
        logger.info("Server started. IP: " + str(app.config["IP"]) + " Port: " + str(app.config["PORT"]))

        logger.debug("count: " + str(threading.active_count() ))

    except Exception as exc:
        logger.error(exc)
        logger.exception(traceback.format_exc())
    finally:
        pass


def storeConfigObject(confObj):
    """ Takes a Object and dumps it as JSON in the CONF_FILE"""
    with open(CONF_FILE,'w') as file:
        file.write(json.dumps(confObj, indent=2, sort_keys=False))



def getConfigObject():
    """ Reads the content of the CONF_FILE and converts it to a json Objects. Returns the object."""
    with open(CONF_FILE,'r') as file:
        string = file.read()
        return json.loads(string)

    return '{msg: "could not load file"}'


# def createContinuesVideoStream():
#     while True:
#         ret, frame = cap.read()
#
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', frame)[1].tobytes() + b'\r\n')
#
# @app.route('/api/video_feed')
# @crossdomain(origin='*')
# def video_feed():
#     return Response(createContinuesVideoStream(),mimetype='multipart/x-mixed-replace; boundary=frame')
