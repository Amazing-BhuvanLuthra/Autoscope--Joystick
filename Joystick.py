#########################################################################
# Copyright Valetude Primus Healthcare Pvt. Ltd. - All Rights Reserved
# Unauthorized copying of this file via any medium is strictly prohibited
# Proprietary and confidential
#########################################################################

"""
@brief Interface for the Joystick object

This file contains functions for threaded interface with the
Joystick.
"""

from evdev import InputDevice, categorize, ecodes
import serial
import time
import threading
import logging
import datetime
import main
import backend.autofocus
import backend.static.classes as C
import backend.static.constants as c



class Joystick:
    """
    @ breif class for interfacing with backend joystick

    This class inplements additional functions to interface 
    with Joystick
    """
    __instance__ = None
    def __init__(self):


        if Joystick.__instance__:
            logging.error("[Joystick] Multiple instances requested")
            raise RuntimeError("Another instance of joystick interface already exists")
        
        logging.info("[Joystick] Creating new instance")

        self.joystick = (None)

        self.stop = True

        #Setting the input device
        #self.gamepad = InputDevice('/dev/input/event5')

        logging.info("[Joystick] Creating new Joystick")


        #button code variables (change to suit your device)
        self.aBtn = 308
        self.bBtn = 304
        self.cBtn = 307
        self.dBtn = 305
        self.TRBtn = 311
        self.TLBtn = 310

        #Serial board Initialising
        # self.board = serial.Serial(c.MOTOR_TTY,9600)

        #self.lock = threading.Lock()
        #self.lock.acquire()

        Joystick.__instance__ = self

    def _thread(self) -> None:
        """
        @breif Private method to store OS thread for Joystick

        This function interfaces with the operating system thread for
        controlling the motars with Joystick
        """
        logging.info("[Joystick] Initialising Thread handler befor gamepad")
        board = serial.Serial("/dev/ttyUSB1",9600)
        gamepad = InputDevice('/dev/input/event5')
        logging.info("[Joystick] Initialising Thread handler")
        #loop and filter by event code and print the mapped label
        for event in gamepad.read_loop():
            if event.type == ecodes.EV_KEY:
                if event.value == 1:
                    logging.info("[Joystick] {}".format(event.code))
                    if event.code == self.aBtn:
                        logging.info("[Joystick] Autofocus")
                        backend.autofocus.auto()
                    elif event.code == self.bBtn:
                        continue        
                    elif event.code == self.cBtn: 
                        logging.info("[Joystick] Capture")
                        main.cam.capture(datetime.datetime.now().strftime("%d%m%Y_%H%M%S"))
                    elif event.code == self.dBtn:
                        continue          
                    elif event.code == self.TLBtn:
                        _ = board.write("zcclk,{}".format(main.mover.z_axis_f.step_size).encode())
                        main.mover.z_axis_f.position += main.mover.z_axis_f.step_size
                        while True:
                            data = self.board.readline()
                            if data == b'Done\r\n':
                                break
                    elif event.code == self.TRBtn:
                        _ = board.write("zclk,{}".format(main.mover.z_axis_f.step_size).encode())
                        main.mover.z_axis_f.position -= main.mover.z_axis_f.step_size
                        while True:
                            data = self.board.readline()
                            if data == b'Done\r\n':
                                break 
            elif event.type == ecodes.EV_ABS:
                if event.code == 0:
                    if event.value == 0:
                        logging.info("[Joystick] x Axis moving")
                        _ = board.write("xclk,{}".format(main.mover.x_axis.step_size).encode())
                        main.mover.x_axis.position -= main.mover.x_axis.step_size
                        while True:
                            data = board.readline()
                            if data == b'Done\r\n':
                                break            
                    elif event.value == 2:
                        logging.info("[Joystick] x Axis moving")
                        _ = board.write("xcclk,{}".format(main.mover.x_axis.step_size).encode())
                        main.mover.x_axis.position += main.mover.x_axis.step_size
                        while True:
                            data = board.readline()
                            if data == b'Done\r\n':
                                break           
                elif event.code == 1:
                    if event.value == 0:
                        logging.info("[Joystick] y Axis moving")
                        _ = board.write("ycclk,{}".format(main.mover.y_axis.step_size).encode())
                        main.mover.y_axis.position += main.mover.y_axis.step_size
                        while True:
                            data = board.readline()
                            if data == b'Done\r\n':
                                break            
                    elif event.value == 2:
                        logging.info("[Joystick] y Axis moving")
                        _ = board.write("yclk,{}".format(main.mover.y_axis.step_size).encode())
                        main.mover.y_axis.position -= main.mover.y_axis.step_size
                        while True:
                            data = board.readline()
                            if data == b'Done\r\n':
                                break
            if self.stop:
                break

        self.stop = False
        
    def start_thread(self) -> None:
        """
        @brief Start background thread to control motar using Joystick

        This function initializes and binds a background thread to the
        class instance to get signals from Joystick
        """
        logging.info("[Joystick] Starting new thread")

        # if existing thread is already dead, remove it from list
        if self.joystick and not self.joystick.is_alive():
            self.joystick = None

        if not self.joystick:
            logging.info("[Joystick] Creating new thread")
            self.stop = False
            self.joystick = threading.Thread(target=self._thread)
            self.joystick.start()
            logging.info("[Joystick] Created new thread")

            # wait until we start receiving data
            # while not self.frame:
            #     time.sleep(0)


    def stop_thread(self) -> None:
        """
        @brief Stop background thread from controlling motars using Joystick

        This function stops the background thread from sending the
        signal from the Joystick.
        """
        logging.info("[Joystick] Stopping existing thread")

        # nothing to kill
        if not self.joystick:
            pass
        else:
            self.stop = True
            if self.joystick.is_alive():
                self.joystick.join()
            time.sleep(.1)
            self.joystick = None
