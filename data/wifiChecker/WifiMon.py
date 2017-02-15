#!/usr/bin/python
import logging
import subprocess
import threading
import time

from data.ConfigurationReader import ConfigurationReader
from data.Constants import Constant

logger = logging.getLogger('sensorLogger')


class WifiMon(threading.Thread):
    threadExitFlag = 0

    def __init__(self):
        threading.Thread.__init__(self)
        self.cr = ConfigurationReader()
        self.wifi_ping_host = (self.cr.get_key_in_section(Constant.CONFIG_SECTION_WIFI, Constant.WIFI_PING_HOST))
        self.polling_interval = int(self.cr.get_key_in_section(Constant.CONFIG_SECTION_WIFI, Constant.POLLING_INTERVAL))
        self.use_mock_sensor = bool(self.cr.get_key_in_section(Constant.CONFIG_SECTION_APP, Constant.USE_MOCK_SENSOR))
        self.WLAN_check_flg = False

        logger.info('[wifi Alive check set as: %s', self.wifi_ping_host)

    def keep_wifi_alive(self):
        while not WifiMon.threadExitFlag:
            self.wlan_check()
            logger.info("Sleeping WIFI thread for [%s] seconds ", self.polling_interval)
            time.sleep(self.polling_interval)

    def wlan_check(self):
        """
        This function checks if the WLAN is still up by pinging the router.
        If there is no return, we'll reset the WLAN connection.
        If the resetting of the WLAN does not work, we need to reset the Pi.
        :return:
        """
        if self.use_mock_sensor:
            cmd = 'ping -c 1 -q ' + self.wifi_ping_host + ' | grep "1 packets received"'
        else:
            cmd = 'ping -c 1 -q ' + self.wifi_ping_host + ' | grep "1 received" '

        logger.debug(cmd)
        # ping_ret = subprocess.call(cmd, shell=True)

        ping_ret = ''
        try:
            ping_ret = subprocess.check_output(cmd, shell=True).rstrip('\n')
        except Exception as cpe:
            logger.critical("Wifi Check failed with [%s]", cpe.__str__())

        if len(ping_ret) < 1:
            # we lost the WLAN connection.
            # did we try a recovery already?
            if self.WLAN_check_flg:
                # we have a serious problem and need to reboot the Pi to recover the WLAN connection
                logger.critical(' *** Fatal ERROR in wifi checker *** ')
                logger.critical(' *** After 1 retry, the wifi is NOT available *** ')
                logger.critical(' *** Attempting SUDO REBOOT on Raspberry Pi *** ')
                self.WLAN_check_flg = False
                subprocess.call(['sudo reboot'], shell=True)
                return -1
            else:
                # try to recover the connection by resetting the LAN
                logger.critical("PING to [%s] is LOST! ", self.wifi_ping_host)
                logger.critical('Fatal error in wifiMon!')
                logger.critical('ATTEMPTING to turn wifi OFF and ON again!')
                self.WLAN_check_flg = True  # try to recover
                subprocess.call(['sudo /sbin/ifdown wlan0 && sleep 10 && sudo /sbin/ifup --force wlan0'], shell=True)
                return -2
        else:
            self.WLAN_check_flg = False
            logger.info("PING to [%s] is Alive", self.wifi_ping_host)
            return 1

