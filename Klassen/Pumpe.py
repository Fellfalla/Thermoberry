#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Markus Weber'
import RPi.GPIO as GPIO
import Communicator
from GlobalVariables import *
import socket
GPIO.setmode(GPIO.BCM)  #Set Numbering mode

class Pumpe:
    def __init__(self, Bezeichnung, master = None):
        self.Blockiert = False
        self.IstAktiv = False
        self.Bezeichnung = Bezeichnung
        self.PinEinAus = None
        self.prioritaet = 0
        self.master = master

        self.PinsAktualisieren()

    def resetPrioritaet(self,prioritaet=0):
        ### setzt Prioritaet auf 0 zurueck falls kein Parameter uebergeben wird ###
        if self.prioritaet <= prioritaet:
            self.prioritaet = 0

    def PinsAktualisieren(self):
        # todo seltsamkeit entfernen Manche Pinbelegungen angeblich nicht vorhanden
        for gpioTuple in Communicator.GetGPIO(machine_name=None):
            if self.Bezeichnung in gpioTuple[1].keys():
                neuerPin = gpioTuple[1][self.Bezeichnung]
                if self.PinEinAus != neuerPin: # neue Pinzuweisung gefunden
                    self.CleanGPIOPin(self.PinEinAus)
                    self.PinEinAus = neuerPin
                    GPIO.setup(self.PinEinAus, GPIO.OUT)
                    GPIO.output(self.PinEinAus, GPIO.HIGH)
                    self.master = gpioTuple[0]

        if self.master is None: # Falls kein raspberry zugewiesen wurde
            Communicator.SchreibeFehler('Pinbelegung fuer ' + str(self.Bezeichnung) + ' nicht vorhanden', 'SetGPIOPins')
                #time.sleep(10)  # Solange durchfuehren bis Passender Wert drin ist
                #self.SetGPIOPins()

    def ControlPins(self):
        #todo: debugging - dieser Programmteil wird viel zu oft aufgerufen
        if self.master is None:
            self.PinsAktualisieren()
        else:
            GPIOPins = Communicator.GetGPIO(machine_name=self.master)
            try:
                if GPIOPins[self.Bezeichnung] != self.PinEinAus:
                    print ('pumpe aktualisiert pins')
                    self.PinsAktualisieren()
            except KeyError as e:
                Communicator.SchreibeFehler(e,"Control Pins")

    def CleanGPIOPin(self, pin):
        try:
            if pin is not None:
                GPIO.cleanup(pin)
        except TypeError:
            print("TypeError in CleanGPIOPins")

    def Ein(self,prioritaet=0):  # GPIO Pin einschalten
        if self.Blockiert:
            return
        elif prioritaet < self.prioritaet:
            return
        self.PinsAktualisieren()
        self.IstAktiv = True
        if self.master == socket.gethostname():
            print (self.Bezeichnung + " ein - Pin ", self.PinEinAus, " auf Low")
            self.GPIOLOW(self.PinEinAus)
            self.IstAktiv = True
        else: #falls anderer raspi zuständig ist
            Communicator.SchreibeBefehl(self.Bezeichnung,True)

    def Aus(self,prioritaet=0):  # GPIO Pin ausschalten
        if self.Blockiert:
            return
        elif prioritaet < self.prioritaet:
            return
        self.PinsAktualisieren()
        self.IstAktiv = False
        if self.master == socket.gethostname():
            print (self.Bezeichnung + " aus - Pin ", self.PinEinAus, " auf High")
            self.GPIOHIGH(self.PinEinAus)

        else: #falls anderer raspi zuständig ist
            Communicator.SchreibeBefehl(self.Bezeichnung,False)

    def GPIOHIGH(self, Pin):
        if GPIO.input(Pin) == GPIO.LOW:
            GPIO.output(Pin, GPIO.HIGH)

    def GPIOLOW(self, Pin):
        if GPIO.input(Pin) == GPIO.HIGH:
            GPIO.output(Pin, GPIO.LOW)

def main():
    pass


if __name__ == "__main__":
    main()