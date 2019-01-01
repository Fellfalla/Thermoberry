#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Markus Weber'

from Klassen import Communicator
from Klassen.Sensor import Sensor
from Klassen.SensorListe import SensorListe

from GlobalVariables import *

import time
import os
import sys

class SensorAuswertung(object):

    def checkSensorIDs(self):
        """Testet ob alle angeschlossenen Sensoren in der SensorListe angelegt sind """
        try:
            for identifier in Communicator.getSlaveList():
                if identifier not in Communicator.getSensorList().getAllIDs():
                    print ('Neue Sensor ID %s gefunden' %identifier)
                    self._assignID(identifier=identifier)
                    self.checkSensorIDs()
        except IOError:
            pass
            #print ('Keine Sensoren angeschlossen - Kann %s%s nicht finden' %(PATH_SLAVE_LIST, SLAVE_LIST_DATEINAME))

    @staticmethod
    def checkSensorNames():
        """Testet ob alle Sensoren in SensorListe einen Namen zugeordnet haben"""
        sensorList = Communicator.getSensorList()
        for sensorName in Communicator.getSensorNameList():
            if sensorName not in sensorList.getAllNames():
                Communicator.saveSensor(Sensor(name=sensorName))

    @staticmethod
    def chooseSensor(sensorList):
        """Zuweisung der id zu einem Sensor"""
        assignDict = {}
        for sensor in sensorList:
            IDNumber = sensorList.index(sensor)+1
            print ("%2s: %s" %(IDNumber, sensor))
            assignDict[IDNumber] = sensor
        # Eingabeschleife
        while True:
            ID = raw_input("Auswahl: ")
            try:
                ID = int(ID)
                chosenSensor = assignDict[ID]
                print ('Du hast %s gewaehlt' %chosenSensor)
                return chosenSensor
            except KeyError:
                print("Sensorname nicht verfuegbar!")
            except ValueError:
                print("Ungueltige ID!")
            except Exception as e:
                print(e)

    def deleteSensor(self):
        sensorList = Communicator.getSensorList()
        print ('Waehle Sensorname der geloescht werdne soll:')
        choosenSensor = self.chooseSensor(sensorList)
        sensorList.remove(choosenSensor)
        Communicator.saveSensorList(sensorList, overwrite=True)
        self.checkSensorIDs()
        choice = raw_input('Weiteren Sensor loeschen(y/n): ')
        if choice == 'n':
            return
        else:
            self.deleteSensor()

    def renameSensor(self):
        # Waehle Sensorname der zu einer anderen Temperatur gehoert
        sensorList = Communicator.getSensorList()
        print ('Waehle den ersten Sensor zum tauschen')
        choosenSensor1 = self.chooseSensor(sensorList)
        print ('Waehle den zweiten Sensor zum tauschen')
        choosenSensor2 = self.chooseSensor(sensorList)
        temp1 = choosenSensor1.getTemperatur()
        id1 = choosenSensor1.getID()
        choosenSensor1.reset()
        choosenSensor1.setID(choosenSensor2.getID())
        choosenSensor1.setTemperatur(choosenSensor2.getTemperatur())
        choosenSensor2.reset()
        choosenSensor2.setID(id1)
        choosenSensor2.setTemperatur(temp1)
        Communicator.saveSensorList(sensorList)
        self.checkSensorIDs()
        choice = raw_input('Weiteren Sensor umbenennen(y/n): ')
        if choice == 'n':
            return
        else:
            self.renameSensor()

    def _assignID(self, identifier):
        print ('Neue Sensor ID gefunden!')
        chosenSensor = self.chooseSensor(Communicator.getSensorList())
        chosenSensor.setID(identifier) #Sensor id wird überschrieben
        Communicator.saveSensor(chosenSensor)

    def measurePrececdure(self,saveSingleSensors=True):
        try:
            # TODO: Sensor auf None schalten, falls dieser nicht gefunden wird

            # LOKALE MESSUNG
            print('\nMessung der lokalen Sensoren:')


            # Laden der aktuellen globalen Sensorliste
            sensorList = Communicator.loadObjectFromServer(name=SERVER_OBJEKT_SENSORLISTE)         
            if not sensorList:
                print("Keine Sensorliste vom Server erhalten.")
                sensorList = SensorListe()

            localSlaveList = Communicator.getSlaveList()     # Laden der lokal angeschlossenen SensorIDs
            for identifier in localSlaveList:  # Durchgehen der angeschlossenen Sensoren
                try:
                    # Versuche den Sensor aus der Liste des Servers zu holen
                    sensor = sensorList.getSensor(identifier=identifier)
                except KeyError:
                    # Falls der Sensor nicht in der Liste ist: Erzeuge neuen Sensor und speichere ihn in die lokale liste
                    sensor = Sensor(identifier=identifier)
                except AttributeError:
                    if sensorList is None:  # Die sensorListe vom Server ist Leer
                        sensor = Sensor(identifier=identifier)
                

                sensor.reload_name()
                sensor.measure(msg=False)

                # Upload
                if saveSingleSensors:   # Falls die Sensoren einzeln gespeichert werden sollen: Hier speichern und print
                    print(sensor)
                    Communicator.saveSensor(sensor)

            if not saveSingleSensors:
                Communicator.saveSensorList(sensorList)
                print(sensorList)
            elif sensorList is not None:   # Falls nicht die komplette Liste ausgegeben wird, wurden die globalen sensoren noch nicht geprintet
                print('\nWerte der restlichen Sensoren:')
                for sensorID in sensorList.getAllIDs():
                    if sensorID not in localSlaveList:
                        print (sensorList.getSensor(identifier=sensorID))

            #self.sensorOfflineCheck()
                # teste ob sich der Sensorwert geaendert hat, wenn ja, speichern
            #self.printMesswerte(sensorList)
        finally:
            # Warten, damit ein gewisser Abstand zwischen den Temperaturmessungen auch bei Fehlern bleibt
            time.sleep(TEMPERATURMESSUNG_PAUSE)

    @staticmethod
    def sensorOfflineCheck():
        """Schmeisst die Sensorwerte aller nicht angeschlossenen Sensoren raus"""
        for sensor in Communicator.getSensorList():
            if len(sensor.memory) > 0:
                if time.time()-sensor.memory[0][1] > TIME_UNTIL_SENSOR_OFFLINE:
                    sensor.setTemperatur(SENSOR_OFFLINE)
                    sensor.memoryInsert(SENSOR_OFFLINE)
                    Communicator.saveSensor(sensor)

    @staticmethod
    def printMesswerte(sensorList):  # Ausgabe
        """Ausgeben aller Messerwerte der uebergebenen Sensorliste"""
        for sensor in sensorList:
            print sensor

def CompleteReset():
    """ Loescht alle SensorDaten und SensorNamen """
    print (COMPLETE_RESET_MSG)
    try:
        os.remove(os.path.join(ORDNER_DATENMAP, SERVER_OBJEKT_SENSORLISTE + MACHINE_NAME))
    except OSError as e:
        print (e)

def Initialisierung(argv):  # öffnet Komm-Daten und erstellt bei bedarf neue
    MessProgramm = SensorAuswertung()
    for params in argv:
        if params == "-reset":
            eingabe = raw_input("Wirklich CompleteReset durchführen? (j/n)")
            while eingabe != "j" and eingabe != "n":
                print("Falsche Eingabe")
                eingabe = raw_input("Wirklich CompleteReset durchführen? (j/n)")
            if eingabe == "j":
                CompleteReset()
        if params == "-rename":
            MessProgramm.renameSensor()
        if params == "-del" or params == "-delete":
            MessProgramm.deleteSensor()
    return MessProgramm

def main(argv):
    Initialisierung(argv)
    MessProgramm = SensorAuswertung()
    try:
        while True:
            try:
                MessProgramm.measurePrececdure()
            except IOError as e:
                print (e)
            except Exception as e:
                Communicator.SchreibeFehler(e.message,'SensorAuswertung - Main' + str(e.args) + str(e.message) )
    except KeyboardInterrupt:
        exit()


if __name__ == "__main__":
    main(sys.argv)