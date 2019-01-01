#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Markus Weber'

from unittest import TestCase
from Puffer import Puffer
from Sensor import Sensor
from SensorListe import SensorListe
from GlobalVariables import *

RAUM_IMAGINAER1 = "Sauraum"
RAUM_IMAGINAER2 = "Keller"
RAUM_REAL_1 = "Heizung"
RAUM_REAL_2 = "Hygiene"
RAUM_REAL_3 = "Reserve"

def main():
    pass

if __name__ == "__main__":
    main()

class TestSensor(TestCase):
    #sensoren
    ID1 = 'ID1'
    ID2 = 'ID2'
    name1 = BEZEICHNUNG_PUFFERSENSOR + RAUM_IMAGINAER1 + '1'
    name2 = BEZEICHNUNG_PUFFERSENSOR + RAUM_IMAGINAER1 + '2'
    name3 = BEZEICHNUNG_PUFFERSENSOR + RAUM_IMAGINAER1 + '3'
    name4 = BEZEICHNUNG_PUFFERSENSOR + RAUM_IMAGINAER1 + '4'
    name5 = BEZEICHNUNG_PUFFERSENSOR + RAUM_IMAGINAER1 + '5'
    name6 = BEZEICHNUNG_PUFFERSENSOR + RAUM_IMAGINAER1 + '6'
    name7 = BEZEICHNUNG_PUFFERSENSOR + RAUM_IMAGINAER1 + '7'
    name8 = RAUM_IMAGINAER1 + '7'
    name9 = 'Schwammerlsau9'


    temperatur1 = 100
    temperatur2 = 0
    temperatur3 = 100
    temperatur4 = 100.0
    temperatur5 = 546189.14864414758

    s1 = Sensor(name=name1,temperatur=temperatur1,identifier=ID1)
    s2 = Sensor(name=name2,temperatur=temperatur2,identifier=ID2)

    s3 = Sensor(name=name3,temperatur=temperatur3,identifier=ID1)
    s4 = Sensor(name=name4,temperatur=temperatur4,identifier=ID2)

    s5 = Sensor(name=name5,temperatur=temperatur1,identifier=ID1)
    s6 = Sensor(name=name6,temperatur=temperatur1,identifier=ID2)
    s7 = Sensor(name=name7,temperatur=temperatur2,identifier=ID1)

    s8 = Sensor(name=name8,temperatur=temperatur3,identifier=ID1)
    s9 = Sensor(name=name9,temperatur=temperatur4,identifier=ID2)

    #Puffer1
    vol1 = 100
    pFiktiv1 = Puffer (vol1,RAUM_IMAGINAER1)
    pFiktiv1.PufferSensors = SensorListe([s1,s2])
    pFiktiv1.MaximaleTemperatur = temperatur1
    pFiktiv1.MinimaleTemperatur = temperatur2

    #Puffer2
    vol2 = 100
    pFiktiv2 = Puffer (vol2,RAUM_IMAGINAER2)
    pFiktiv2.PufferSensors = SensorListe([s3,s4])
    pFiktiv2.MaximaleTemperatur = temperatur1
    pFiktiv2.MinimaleTemperatur = temperatur2

    #Puffer3
    vol3 = 51546.126897
    pFiktiv3 = Puffer (vol3,RAUM_IMAGINAER2)
    pFiktiv3.PufferSensors = SensorListe([s2,s2])
    pFiktiv3.MaximaleTemperatur = temperatur5
    pFiktiv3.MinimaleTemperatur = temperatur2

    #Puffer4
    vol4 = 100
    pFiktiv4 = Puffer (vol3,RAUM_IMAGINAER2)
    pFiktiv4.PufferSensors = SensorListe([s5,s6,s7])
    pFiktiv4.MaximaleTemperatur = temperatur1
    pFiktiv4.MinimaleTemperatur = temperatur2


    def test_specialMethods(self):

        p1 = Puffer (Volumen = 1000, Heizkreis= RAUM_REAL_1)
        p2 = Puffer (1000,RAUM_REAL_2)
        p3 = Puffer (2000,RAUM_IMAGINAER2)
        p4 = Puffer (500,RAUM_IMAGINAER1)
        p5 = Puffer (1000,RAUM_IMAGINAER2)
        p6 = Puffer (1000,RAUM_IMAGINAER2)
        p7 = Puffer (1000,RAUM_IMAGINAER2)
        p8 = Puffer (1000,RAUM_IMAGINAER2)

        sMax = Sensor(identifier='irgendein scheiss',temperatur=ERSATZPARAMETER_PUFFER_TEMPERATUR_MAX,name='noname')
        sMin = Sensor(identifier='irgendein scheiss',temperatur=ERSATZPARAMETER_PUFFER_TEMPERATUR_MIN,name='noname')

        #__gt__
        self.assertGreater(p1, p4)
        self.assertGreater(p8, p4)
        self.assertGreater(p3, p8)
        self.assertGreater(p3, p7)

        #__ge__
        self.assertGreaterEqual(p1,p2)
        self.assertGreaterEqual(p3,p1)
        self.assertGreaterEqual(p1,p5)
        self.assertGreaterEqual(p2,p2)
        self.assertGreaterEqual(p8,p2)
        self.assertGreaterEqual(p8,p4)

        #__eq__
        self.assertEqual(p1,p2)
        self.assertEqual(p1,p5)
        self.assertEqual(p1,p6)
        self.assertEqual(p1,p7)
        self.assertEqual(p7,p8)

        #__ne__
        self.assertNotEqual(p3,p4)
        self.assertNotEqual(p2,p4)
        self.assertNotEqual(p2,p3)
        self.assertNotEqual(p8,p4)

        #__le__
        self.assertLessEqual(p1,p2)
        self.assertLessEqual(p1,p3)
        self.assertLessEqual(p1,p5)
        self.assertLessEqual(p2,p2)
        self.assertLessEqual(p8,p2)
        self.assertLessEqual(p4,p8)

        #__lt__
        self.assertLess(p4,p1)
        self.assertLess(p4,p2)
        self.assertLess(p4,p7)
        self.assertLess(p4,p8)
        self.assertLess(p1,p3)
        self.assertLess(p8,p3)

        #__str__
        self.assertEqual('{name:15s} {status:15s}\t\tLadung: {ladung}'.format(name=p4.Bezeichnung,status=p4.getStatus(),ladung=p4.Ladezustand),str(p4))
        self.assertEqual('{name:15s} {status:15s}\t\tLadung: {ladung}'.format(name=p8.Bezeichnung,status=p8.getStatus(),ladung=p8.Ladezustand),str(p8))

        p8.PufferSensors.append(sMax)
        p4.PufferSensors.append(sMin)
        for i in range(len(p1.PufferSensors.getAllTemperatures())):
            p1.PufferSensors.getAllTemperatures()[i] = p1.MinimaleTemperatur

        for i in range(len(p2.PufferSensors.getAllTemperatures())):
            p2.PufferSensors.getAllTemperatures()[i] = p2.MaximaleTemperatur

        for i in range(len(p8.PufferSensors.getAllTemperatures())):
            p8.PufferSensors.getAllTemperatures()[i] = p8.MaximaleTemperatur

        p1.ErmittleLadezustand()
        p2.ErmittleLadezustand()
        p8.ErmittleLadezustand()
        p4.ErmittleLadezustand()
        self.assertEqual("Name: %-25s Ladezustand: %4.2f Leeren: %6s Fuellen: %6s" %(BEZEICHNUNG_PUFFER+RAUM_REAL_1, round(p1.Ladezustand,2), str(None), str(None)),str(p1))
        self.assertEqual("Name: %-25s Ladezustand: %4.2f Leeren: %6s Fuellen: %6s" %(BEZEICHNUNG_PUFFER+RAUM_REAL_2, round(p2.Ladezustand,2), str(None), str(None)),str(p2))
        self.assertEqual("Name: %-25s Ladezustand: %4.2f Leeren: %6s Fuellen: %6s" %(BEZEICHNUNG_PUFFER+RAUM_IMAGINAER2, round(1.,2), str(None), str(None)),str(p8))
        self.assertEqual("Name: %-25s Ladezustand: %4.2f Leeren: %6s Fuellen: %6s" %(BEZEICHNUNG_PUFFER+RAUM_IMAGINAER1, round(.0,2), str(None), str(None)),str(p4))


    def test_getPufferSensors(self):
        """Ermittelt alle vorhandenen Sensoren die zu dem Puffer gehören anhand des Namens"""
        p1 = Puffer (Volumen = 1000, Heizkreis= RAUM_REAL_1)
        p2 = Puffer (1000,RAUM_REAL_2)
        p3 = Puffer (1000,RAUM_IMAGINAER1)
        p4 = Puffer (1000,RAUM_REAL_3)

        for i in range(len(p1.PufferSensors)):
            erwarteteSensorbezeichnung = BEZEICHNUNG_PUFFERSENSOR + RAUM_REAL_1 + str(i+1)
            self.assertEqual(erwarteteSensorbezeichnung in p1.PufferSensors, True)

        for i in range(len(p2.PufferSensors)):
            erwarteteSensorbezeichnung = BEZEICHNUNG_PUFFERSENSOR + RAUM_REAL_2 + str(i+1)
            self.assertEqual(erwarteteSensorbezeichnung in p2.PufferSensors, True)

        for i in range(len(p4.PufferSensors)):
            erwarteteSensorbezeichnung = BEZEICHNUNG_PUFFERSENSOR + RAUM_REAL_3 + str(i+1)
            self.assertEqual(erwarteteSensorbezeichnung in p4.PufferSensors, True)

        self.assertEqual(p3.PufferSensors, [])

        sensList = SensorListe([self.s1, self.s2,self.s3,self.s4])
        self.pFiktiv1.setPufferSensors(sensorListe=sensList)

        for i in range(len(self.pFiktiv1.PufferSensors)):
            erwarteteSensorbezeichnung = BEZEICHNUNG_PUFFERSENSOR + RAUM_IMAGINAER1 + str(i+1)
            self.assertEqual(erwarteteSensorbezeichnung in self.pFiktiv1.PufferSensors, True)
        self.assertEqual(self.pFiktiv1.PufferSensors, sensList)

        sensList = SensorListe([self.s1, self.s2,self.s3])
        self.pFiktiv1.setPufferSensors(sensorListe=sensList)
        for i in range(len(self.pFiktiv1.PufferSensors)):
            erwarteteSensorbezeichnung = BEZEICHNUNG_PUFFERSENSOR + RAUM_IMAGINAER1 + str(i+1)
            self.assertEqual(erwarteteSensorbezeichnung in self.pFiktiv1.PufferSensors, True)
        self.assertEqual(self.pFiktiv1.PufferSensors, sensList)

        sensList = SensorListe([self.s5, self.s6,self.s7])
        self.pFiktiv1.setPufferSensors(sensorListe=sensList)
        self.assertEqual(self.pFiktiv1.PufferSensors, sensList)

        #Reihenfolde in Input vertauschen sollte keine auswirkungen haben:
        sensListold = SensorListe([self.s5, self.s6, self.s7])
        sensList = SensorListe([self.s7, self.s6,self.s5])
        self.pFiktiv1.setPufferSensors(sensorListe=sensList)
        self.assertEqual(self.pFiktiv1.PufferSensors, sensListold)

        #Sensoren mit anderen Namen die aussortiert werden sollten
        sensListold = SensorListe([self.s5, self.s6, self.s7])
        sensList = SensorListe([self.s7, self.s6,self.s5, self.s8, self.s9])
        self.pFiktiv1.setPufferSensors(sensorListe=sensList)
        self.assertEqual(self.pFiktiv1.PufferSensors, sensListold)

        sensList = SensorListe()
        self.pFiktiv1.setPufferSensors(sensorListe=sensList)
        self.assertEqual(self.pFiktiv1.PufferSensors, [])


    def test_VolumenUeberTemperatur(self):
        ref1 = 50 #-> halbes Volumen
        ref2 = 0 # -> alles
        ref3 = 100 # -> garnix
        ref4 = -1456 #-> alles
        ref5 = 156.35 #-> garnix
        ref6 = 100./3 #-> 33°C
        ref7 = 2* (100./3) #-> 66°C

        self.assertEqual(self.pFiktiv1.VolumenUeberTemperatur(ref1),0.5*self.pFiktiv1.Volumen)
        self.assertEqual(self.pFiktiv1.VolumenUeberTemperatur(ref2),1*self.pFiktiv1.Volumen)
        self.assertEqual(self.pFiktiv1.VolumenUeberTemperatur(ref3),0*self.pFiktiv1.Volumen)
        self.assertEqual(self.pFiktiv1.VolumenUeberTemperatur(ref4),1*self.pFiktiv1.Volumen)
        self.assertEqual(self.pFiktiv1.VolumenUeberTemperatur(ref5),0*self.pFiktiv1.Volumen)
        self.assertEqual(self.pFiktiv1.VolumenUeberTemperatur(ref6),(2./3)*self.pFiktiv1.Volumen)
        self.assertEqual(self.pFiktiv1.VolumenUeberTemperatur(ref7),(1./3)*self.pFiktiv1.Volumen)

        self.assertEqual(self.pFiktiv3.VolumenUeberTemperatur(ref2),1*self.pFiktiv3.Volumen)
        self.assertEqual(self.pFiktiv3.VolumenUeberTemperatur(ref3),0*self.pFiktiv3.Volumen)

    def test_VolumenUnterTemperatur(self):
        ref1 = 50 #-> halbes Volumen
        ref2 = 0 # -> alles
        ref3 = 100 # -> garnix
        ref4 = -1456 #-> alles
        ref5 = 156.35 #-> garnix
        ref6 = 100./3 #-> 33°C
        ref7 = 2* (100./3) #-> 66°C

        self.assertEqual(self.pFiktiv1.VolumenUnterTemperatur(ref1),0.5*self.pFiktiv1.Volumen)
        self.assertEqual(self.pFiktiv1.VolumenUnterTemperatur(ref2),0*self.pFiktiv1.Volumen)
        self.assertEqual(self.pFiktiv1.VolumenUnterTemperatur(ref3),1*self.pFiktiv1.Volumen)
        self.assertEqual(self.pFiktiv1.VolumenUnterTemperatur(ref4),0*self.pFiktiv1.Volumen)
        self.assertEqual(self.pFiktiv1.VolumenUnterTemperatur(ref5),1*self.pFiktiv1.Volumen)
        self.assertAlmostEqual(self.pFiktiv1.VolumenUnterTemperatur(ref6),(1./3)*self.pFiktiv1.Volumen,8)
        self.assertAlmostEqual(self.pFiktiv1.VolumenUnterTemperatur(ref7),(2./3)*self.pFiktiv1.Volumen,8)

        self.assertEqual(self.pFiktiv3.VolumenUnterTemperatur(ref2),0*self.pFiktiv3.Volumen)
        self.assertEqual(self.pFiktiv3.VolumenUnterTemperatur(ref3),1*self.pFiktiv3.Volumen)

    def test_ErmittleLadezustand(self):
        self.pFiktiv1.ErmittleLadezustand()
        self.assertEqual(self.pFiktiv1.Ladezustand,0.5)

        self.pFiktiv2.ErmittleLadezustand()
        self.assertEqual(self.pFiktiv2.Ladezustand,1.)

        self.pFiktiv3.ErmittleLadezustand()
        self.assertEqual(self.pFiktiv3.Ladezustand,.0)

        self.pFiktiv4.ErmittleLadezustand()
        self.assertEqual(self.pFiktiv4.Ladezustand,round(2./3,ROUNDED_PERCENTAGE_DIGITS))


    def test_SetPumpen(self):
        pass

    def test_kontrolliereLadezustand(self):
        pass

    def test_EntladepumpeEin(self):
        pass

    def test_EntladepumpeAus(self):
        pass

    def test_BeladepumpeEin(self):
        pass

    def test_BeladepumpeAus(self):
        pass

    def test_EntladepumpeBlockieren(self):
        pass

    def test_EntladepumpeFreigeben(self):
        pass

    def test_BeladepumpeBlockieren(self):
        pass

    def test_BeladepumpeFreigeben(self):
        pass
