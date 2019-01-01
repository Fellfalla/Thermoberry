#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Markus Weber'
import RPi.GPIO as GPIO
from Klassen import Communicator
from Klassen.Pumpe import Pumpe
from Klassen.Mischer import Mischer
from GlobalVariables import *
import time
import sys

def main(argv):
    # initialisierung damit meldung "variable might be unreferenced" nicht angezeigt wird in Hauptschleife
    Aufstellort = BEZEICHNUNG_KELLER
    while True:
        try:
            VorlaufMischer = Mischer(Aufstellort, versorgungsPuffer=BEZEICHNUNG_PUFFER+PUFFERNAME_HEIZUNG)
            HeizungsPumpe = Pumpe(BEZEICHNUNG_HEIZUNGSPUMPE)
            VorlaufMischer.Aktualisieren()
            Communicator.storeObjectToServer(name=VorlaufMischer.getName(), instanz=VorlaufMischer)
            print ("\nInitialsdaten:")
            print(VorlaufMischer)
            break
        except Exception as e:
            Communicator.SchreibeFehler(e.message, 'main@Mischer Initialisierung')
            time.sleep(20)



    # Hauptschleife
    try:
        while True:
            try:
                VorlaufMischer.Aktualisieren()
                HeizungsPumpe.PinsAktualisieren()

                VorlaufMischer.Kalkulieren()
                VorlaufMischer.PrintParameterWerte()  #Daten ausgeben
                Communicator.storeObjectToServer(name=VorlaufMischer.getName(), instanz=VorlaufMischer)
                
                VorlaufMischer.StarteRegelZyklus()
                if VorlaufMischer.Heizbetrieb:
                    HeizungsPumpe.Ein()
                else:
                    HeizungsPumpe.Aus()

            except Exception as e:
                Communicator.SchreibeFehler(e,"In Mischer" + Aufstellort + ".py ausgeloest")
                time.sleep(20)
    except KeyboardInterrupt:
        GPIO.cleanup()
        exit()





if __name__ == "__main__":
    main(sys.argv)