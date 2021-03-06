#!/usr/bin/python
"""
Humidity Sensor class
"""
import logging
import data.sensors.AbstractSensor
from data.Constants import Constant

logger = logging.getLogger(Constant.LOGGER_NAME)


class HumiditySensor(data.sensors.AbstractSensor.AbstractSensor):
    """
    Humidity Sensor class
    """
    def __init__(self, _calibration_value, _use_mock_sensor, _json_key, _sensor_type):
        super(self.__class__, self).__init__(_json_key, _use_mock_sensor)
        self.calibrationValue = _calibration_value
        self.readSensor = None
        self.readSensor = data.sensors.AbstractSensor.AbstractSensor.setup_senor_hardware_type(
            _use_mock_sensor, _sensor_type, logger)


    def read_sensor(self):
        """
        Reads the HUMIDITY Sensor's % humidity value
        :return: the read humidity read from sensor
        """
        logger.debug("Reading Humidity Sensor")
        _sensor_reading = float("{0:.1f}".format(self.readSensor.read_humidity()))
        _calibrate_reading = float("{0:.1f}".format(float(self.calibrationValue)))
        _sensor_value = _sensor_reading + _calibrate_reading
        logger.info("Humidity Reading is: %f", _sensor_value)
        return _sensor_value
