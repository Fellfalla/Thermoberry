#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Klassen import Communicator
from GlobalVariables import *
import RPi.GPIO as GPIO
import time
import socket
import sys

GPIO.setmode(GPIO.BCM)

class cSteuerung:
    def __init__(self):
        self.GPIOPins = {}
        self.IO = {}
        self.SetGPIO()


    def ControlGPIO(self):
        NewGPIOList = Communicator.GetGPIO()
        for Pin in NewGPIOList.keys():
            try:
                if self.GPIOPins[Pin] != NewGPIOList[Pin]:
                    self.SetGPIO()
            except KeyError:
                self.SetGPIO()

    def SetGPIO(self):
        self.GPIOPins = Communicator.GetGPIO()
        for Pin in self.GPIOPins.keys():
            GPIO.setup(self.GPIOPins[Pin], GPIO.OUT)
            GPIO.output(self.GPIOPins[Pin], GPIO.HIGH)

    def BefehleAusfuehren(self):
        GPIO_Befehle = Communicator.GetBefehle()
        if GPIO_Befehle is None:
            print ("Keine Befehle vorhanden oder Datenserver offline -> abwarten und eierschaukeln")
            return
        gpioGeraete =  Communicator.GetGPIO().keys()
        self.ControlGPIO()
        for GPIO_Name in [GPIO_Name for GPIO_Name in GPIO_Befehle.keys() if GPIO_Name in gpioGeraete]:
            if GPIO_Befehle[GPIO_Name]: # Falls True uebergeben wird
                print (GPIO_Name + " laeuft\n" )
                self.GPIO_An(self.GPIOPins[GPIO_Name])
            else:
                print (GPIO_Name + " aus\n" )
                self.GPIO_Aus(self.GPIOPins[GPIO_Name])

    @staticmethod
    def GPIO_An(Pin, invertiert=True): # invertiert bedeutet: Lampe leuchtet auf LOW
        if invertiert:
            if GPIO.input(Pin) == GPIO.HIGH:
                GPIO.output(Pin, GPIO.LOW)
        else:
            if GPIO.input(Pin) == GPIO.LOW:
                GPIO.output(Pin, GPIO.HIGH)

    @staticmethod
    def GPIO_Aus(Pin, invertiert=True): # invertiert bedeutet: Lampe leuchtet auf LOW
        if invertiert:
            if GPIO.input(Pin) == GPIO.LOW:
                GPIO.output(Pin, GPIO.HIGH)
        else:
            if GPIO.input(Pin) == GPIO.HIGH:
                GPIO.output(Pin, GPIO.LOW)


def main(argv):
    steuerung = cSteuerung()
    try:
        while True:  #MainSchleife
            try:
                steuerung.BefehleAusfuehren()
                time.sleep(PUFFERSTEUERUNG_INTERVALL_BEFEHLE_LESEN)
            except Exception as e:
               Communicator.SchreibeFehler(e, 'PufferSteuerungRaspi1 - Main')
            finally:
                time.sleep(PUFFERSTEUERUNG_INTERVALL_BEFEHLE_LESEN) # Abstand in dem die Befehle ausgefuehrt werden

    except KeyboardInterrupt:
        GPIO.cleanup()
        exit()


if __name__ == "__main__":
    main(sys.argv)