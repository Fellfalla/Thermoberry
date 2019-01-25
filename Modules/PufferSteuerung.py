#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Klassen import Communicator
from Klassen.Puffer import Puffer
from Klassen.Pumpe import Pumpe

import RPi.GPIO as GPIO
import time
import sys
from DatenbankModul import DatenbankManager
from GlobalVariables import *

"""SZENARIEN:
Spezialfaelle:
1. PufferVoll
2. Pumpe laeuft, Kein Wasser mehr da
3. Puffer leer

Hinzu kommen spezialfälle, falls z.b. gerade HeizungsPuffer geladen wird, sollte auch HygienePuffer geladen werden

"""

class Manager:
    def __init__(self):
        # todo: Befehlsliste erst KOMPLETT generieren, dann abspeichern
        ###INITIALISIERUNG###
        self.parameter = Communicator.GetParameter()
        self.logging = False
        self.dbManger = DatenbankManager()

        # Initialisiere Pumpen
        self.PumpeHeizraum = Pumpe(BEZEICHNUNG_PUMPE_HEIZRAUM)
        self.PumpeKeller = Pumpe(BEZEICHNUNG_PUMPE_KELLER)

        # Zustand Laden
        zustaende = Communicator.GetBefehle()
        if zustaende is not None:
            for pumpe in zustaende:
                if pumpe == self.PumpeHeizraum.Bezeichnung:
                    if zustaende[pumpe]:
                        self.PumpeHeizraum.Ein()
                    else:
                        self.PumpeHeizraum.Aus()

        #Initialisieren PufferReserve
        self.PufferReserve = Puffer(Volumen=VOLUMEN_RESERVE, Heizkreis=PUFFERNAME_HEIZRAUM)

        # Initialisieren PufferHeizung
        self.PufferHeizung = Puffer(Volumen=VOLUMEN_HEIZUNG, Heizkreis=PUFFERNAME_HEIZUNG)  # Puffer Nr 2 im Keller

        # Initialisiere PufferHygiene
        self.PufferHygiene = Puffer(Volumen=VOLUMEN_HYGIENE, Heizkreis=PUFFERNAME_HYGIENE)

        # Verknuepfen PufferReserve
        self.PufferReserve.setVersorgtePuffer(self.PufferHeizung)
        self.PufferReserve.setVersorgtePuffer(self.PufferHygiene)
        self.PufferReserve.setEntladePumpe(self.PumpeHeizraum)

        # Verknuepfen PufferHeizung
        self.PufferHeizung.setEntladePumpe(self.PumpeKeller)
        self.PufferHeizung.setBeladePumpe(self.PumpeHeizraum)
        self.PufferHeizung.setVersorgungsPuffer(self.PufferReserve)
        self.PufferHeizung.setVersorgtePuffer(self.PufferHygiene)
        self.PufferHeizung.setMischer(MischerName=BEZEICHNUNG_MISCHER+BEZEICHNUNG_KELLER)

        # Verknuepfen PufferHygiene
        self.PufferHygiene.setBeladePumpe(self.PumpeKeller)
        self.PufferHygiene.setVersorgungsPuffer(self.PufferReserve)
        self.PufferHygiene.setVersorgungsPuffer(self.PufferHeizung)

    def aktualisiereAlleLadeStati(self):
        self.PufferHygiene.aktualisiereLadeStatus()
        self.PufferReserve.aktualisiereLadeStatus()
        self.PufferHeizung.aktualisiereLadeStatus()

    def aktualisiereAlleLadungen(self):
        self.PufferHygiene.getLadung()
        self.PufferReserve.getLadung()
        self.PufferHeizung.getLadung()

    def aktualisiereAlleSensorwerte(self):
        self.PufferHygiene.PufferSensors.refreshAllSensorTemperatures()
        self.PufferReserve.PufferSensors.refreshAllSensorTemperatures()
        self.PufferHeizung.PufferSensors.refreshAllSensorTemperatures()

    def aktualisiereAlleParameter(self):
        self.parameter = Communicator.GetParameter()
        try:
            self.logging = eval(self.parameter[PARAMETER_LOGGING_PUFFER])
        except KeyError:
            Communicator.SchreibeFehler('%s Ersatzparameter uebernommen' %PARAMETER_LOGGING_PUFFER, 'aktualisiereAlleParameter in PufferSteuerung')
            self.logging = ERSATZPARAMETER_LOGGING_PUFFER
        self.PufferHygiene.Aktualisieren()
        self.PufferReserve.Aktualisieren()
        self.PufferHeizung.Aktualisieren()
        try:
            self.PufferHeizung.MinimaleTemperatur = Communicator.GetSensorTemperatur(BEZEICHNUNG_SENSOR+BEZEICHNUNG_MISCHER+BEZEICHNUNG_KELLER)
        except Exception as e:
            Communicator.SchreibeFehler(e,'aktualisiereAlleParameter@Manager')
            pass

    def controlReserve(self):
        """Steuert großen ReservePuffer"""
        heizungMinTemperatur = self.PufferHeizung.getMinTemperatur()
        if heizungMinTemperatur is None: # kein wert vorhanden
            return
        pumpverluste = Communicator.GetParameter(parameter=PARAMETER_TEMPERATUR_PUMPVERLUSTE, ersatzparameter=ERSATZPARAMETER_TEMPERATUR_PUMPVERLUSTE)
        temperaturAusgangMin = heizungMinTemperatur + pumpverluste
        # Fall 1: Puffer Voll
        if self.PufferReserve.Voll:  #ohne Gnade entleeren, falls Puffer Voll
            self.PufferReserve.EntladepumpeEin()

        # Fall 2: Puffer Leer
        elif self.PufferReserve.Leer:  #ohne Gnade nicht mehr entleeren, falls Puffer leer
            self.PufferReserve.EntladepumpeAus()

        # Fall 3: Ausgangstemperatur zu niedrig zum Laden
        if self.PufferReserve.getMaxTemperatur() <= temperaturAusgangMin: # Pumpe ausschalten, falls Temperaturniveau zu niedrig
            self.PufferReserve.EntladepumpeAus()

        # Fall 4: Laden, da Versorger gerade auch geladen wird: nicht vorhanden
        # kein Versorger vorhanden

    def controlHeizung(self):
        """Steuert den Heizungspuffer"""
        # Hinweis: beim Versorgungspuffer Pufferreserve kommen durch die lange Leitung noch Pumpverluste hinzu
        heizungMinTemperatur = self.PufferHeizung.getMinTemperatur()
        hygieneMinTemperatur = self.PufferHygiene.getMinTemperatur()
        if heizungMinTemperatur is None or hygieneMinTemperatur is None:
            return
        
        try:
            HeizkreisMischer = Communicator.loadObjectFromServer(name=BEZEICHNUNG_MISCHER + BEZEICHNUNG_KELLER)
            if HeizkreisMischer is not None:
                temperaturAusgangMin = HeizkreisMischer.TemperaturAusgangSoll # Der Heizungspuffer muss mindestens so warm sein wie die Solltemperatur vom Mischer
            else:
                temperaturAusgangMin = hygieneMinTemperatur + ERSATZPARAMETER_TEMPERATURDIFFERENZ_MIN_PUMPEN
        except Exception as e:
            Communicator.SchreibeFehler(e, 'controlHeizung@PufferSteuerung')
            temperaturAusgangMin = hygieneMinTemperatur + ERSATZPARAMETER_TEMPERATURDIFFERENZ_MIN_PUMPEN

        # Fall 1: HeizungsPuffer Voll
        if self.PufferHeizung.Voll:
            if self.PufferReserve.Voll: # weiterlaufen lassen, falls auch reserve voll
                #Beladepumpe:
                self.PufferHeizung.BeladepumpeEin()
                #Entladepumpe:
                self.PufferHeizung.EntladepumpeEin()
            else: # Anhalten falls selber voll und reserve nicht voll
                self.PufferHeizung.BeladepumpeAus()

        # Fall 2: HeizungsPuffer Leer
        elif self.PufferHeizung.Leer:
            #Beladepumpe
            try:
                temperaturEingangMin = heizungMinTemperatur + ERSATZPARAMETER_TEMPERATUR_PUMPVERLUSTE + ERSATZPARAMETER_TEMPERATURDIFFERENZ_MIN_PUMPEN
                mindestvolumen =  Communicator.GetParameter(parameter=PARAMETER_MINDESTVOLUMEN_PUMPEN)
                volumenEingang = self.PufferReserve.VolumenUeberTemperatur(temperaturEingangMin)
                if volumenEingang > mindestvolumen:
                    self.PufferHeizung.BeladepumpeEin()
                else:
                    
                    Communicator.SchreibeFehler('PufferHeizung laedt nicht',
                    '\nVorhandenes Volumen: ' + str(volumenEingang) + 
                    '\nErforderlichesVolumen: ' + str(mindestvolumen))
            except KeyError:
                if volumenEingang > ERSATZPARAMETER_MINDESTVOLUMEN_PUMPEN:
                    self.PufferHeizung.BeladepumpeEin()
            #Entladepumpe
            self.PufferHeizung.EntladepumpeAus()

        # Fall 3: Ausgangstemperatur zu niedrig zum Laden
        if self.PufferHeizung.getMaxTemperatur() <= temperaturAusgangMin: # Pumpe ausschalten, falls Temperaturniveau zu niedrig
            #Entladepumpe,
            self.PufferHeizung.EntladepumpeAus()

            
        # Fall 4: Laden, da Versorger gerade auch geladen wird: nicht vorhanden
        # Keine Ladepumpe für Reserve vorhanden

    def controlHygiene(self):
        """Steuert den Hygienespeicher"""
        heizungMinTemperatur = self.PufferHeizung.getMinTemperatur()
        hygieneMinTemperatur = self.PufferHygiene.getMinTemperatur()
        if heizungMinTemperatur is None or hygieneMinTemperatur is None:
            return
        temperaturEingangMin = self.PufferHygiene.getMinTemperatur() + ERSATZPARAMETER_TEMPERATURDIFFERENZ_MIN_PUMPEN
        volumenEingang = self.PufferHeizung.VolumenUeberTemperatur(temperaturEingangMin)

        # Fall 1: HygienePuffer Voll
        if self.PufferHygiene.Voll:
            if self.PufferHeizung.Voll and self.PufferReserve.Voll: # weiterlaufen lassen, falls auch reserve und heizung voll
                #Beladepumpe:
                self.PufferHygiene.BeladepumpeEin()
            else: # Anhalten falls selber voll und heizung nicht voll
                self.PufferHygiene.BeladepumpeAus()

        # Fall 2: HygienePuffer Leer
        elif self.PufferHygiene.Leer:
            if volumenEingang > 0:
                self.PufferHygiene.BeladepumpeEin()


        # Fall 3: Temperaturniveau zu niedrig zum Laden
        # Ist nicht zuständig für irgendeine Versorgung


        # Fall 4: Laden, da Versorger gerade auch geladen wird:
        if self.PufferHeizung.Pumpe_Fuellen.IstAktiv and self.PufferHeizung.getMaxTemperatur() > temperaturEingangMin:
            self.PufferHygiene.BeladepumpeEin()

    def Managemenent(self):
        ### Kontrollprozedur durchfuehren###
        ### evtl. Abhängigkeitsbaum hierzu aufzeichnen -> rel. kompliziert ###
        self.aktualisiereAlleParameter()
        self.aktualisiereAlleLadungen()
        self.aktualisiereAlleSensorwerte()

        self.aktualisiereAlleLadeStati()
        self.controlReserve()

        self.aktualisiereAlleLadeStati()
        self.controlHeizung()

        self.aktualisiereAlleLadeStati()
        self.controlHygiene()

        self.showStatus()

    def showStatus(self):
        print ( '%s' %'-'*55)
        print (self.PufferReserve)
        print (self.PufferHeizung)
        print (self.PufferHygiene)


    def datalogger (self):
        """
        Loggt die aktuellen Pufferdaten in die verschiedensten Ecken des Programms und der Raspberrys
        1. Auf die SQL Datenbank
        2. Auf den Datenserver
        """
        if self.logging:
            pufferManagerMembers = vars(self)
            for puffer in pufferManagerMembers.keys():
                if isinstance(pufferManagerMembers[puffer], Puffer):
                    self.dbManger.logObject(puffer,pufferManagerMembers[puffer])

        pufferManagerMembers = vars(self)
        for puffer in pufferManagerMembers.keys():
            if pufferManagerMembers[puffer].__class__.__name__ == Puffer.__name__:
                Communicator.storeObjectToServer(name=pufferManagerMembers[puffer].Bezeichnung, instanz=pufferManagerMembers[puffer])


def main(argv):
    # initialisierung
    try:
        pufferManager = Manager()
        pufferManager.datalogger() # Wichtig, da sonst keine pufferobjekte auf dem server existieren
    except Exception as e:
        Communicator.SchreibeFehler(e.message, 'PufferSteuerung@Main')

    # Hauptschlefie
    try:
        lastLoggingTime = time.time() - PUFFERSTEUERUNG_INTERVALL_DATALOGGING
        while True:  #MainSchleife
            try:
                pufferManager.Managemenent()
                if time.time() - lastLoggingTime > PUFFERSTEUERUNG_INTERVALL_DATALOGGING:
                    pufferManager.datalogger()
                    lastLoggingTime = time.time()
            except Exception as e:
                Communicator.SchreibeFehler(e, 'PufferSteuerung@Main')
                # todo: Falls Datenserver beim Scriptstart nicht laeuft, geht es auch ncith sobald der Server startet
                del pufferManager
                pufferManager = Manager() # Manager neu Instanzieren
            finally:
                time.sleep(PUFFERSTEUERUNG_INTERVALL_BEFEHLE_SCHREIBEN) # Intervall in dem die Lage analysiert und Befehle geschrieben werden


    except KeyboardInterrupt:
        GPIO.cleanup()
    finally:
        if pufferManager.dbManger.db.open:
            pufferManager.dbManger.disconnect()

if __name__ == "__main__":
    main(sys.argv)