#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase
from Klassen.SensorListe import SensorListe
from Klassen.Sensor import Sensor

__author__ = 'Markus Weber'


def main():
    pass


if __name__ == "__main__":
    main()


class TestSensorListe(TestCase):
    ID1 = 'ID1'
    ID2 = 'ID2'
    name1 = 'Sensor1'
    name2 = 'Sensor2'
    name3 = '3Sens3'
    temperatur1 = 123.549787421
    temperatur2 = 123.549787420
    temperatur3 = 0
    temperatur4 = -45
    temperatur5 = 'stringelding'
    temperatur6 = '-123.15'
    s1 = Sensor(name=name1,temperatur=temperatur4,identifier=ID1)
    s2 = Sensor(name=name2,temperatur=temperatur1,identifier=ID2)
    s1_1 = Sensor(name=name1,temperatur=temperatur3,identifier=ID1)
    s3 = Sensor(name=name1,temperatur=temperatur2,identifier=ID1)
    s4 = Sensor(name=name1,temperatur=temperatur5,identifier=ID1)
    s5 = Sensor(name=name1,temperatur=temperatur6,identifier=ID1)

    notExistingSensor = Sensor(name='not existing')

    sList = SensorListe()
    sensList = SensorListe()
    sensList2 = SensorListe([s1,s5,s2,s1_1,s3,s4])
    sList.append(s1)
    sList.append(s2)


    def test_specialMethods(self):
        sensList = SensorListe()
        s1 = Sensor(name='testSensor', identifier='1')
        s2 = Sensor(name='testSensor', identifier='1')
        iterable1 = [Sensor(),s1,Sensor()]
        iterable2 = [Sensor(),Sensor(),'string',Sensor()]
        iterable3 = [Sensor(),Sensor(),25.15,Sensor()]
        iterable4 = [Sensor(),Sensor(),SensorListe(),Sensor()]
        iterable5 = [Sensor(),Sensor(),15,Sensor()]
        iterable6 = [s1,s2]

        self.assertRaises(TypeError,self.sensList.append,'string')
        self.assertRaises(TypeError,sensList.append,25)
        self.assertRaises(TypeError,sensList.append,25.123)
        self.assertRaises(TypeError,sensList.append,sensList.append(Sensor()))
        self.assertRaises(TypeError,sensList.append,sensList.append(Sensor()))

        #__init__ darf nur Sensoren annehmen
        self.assertRaises(TypeError,SensorListe,iterable2)
        self.assertRaises(TypeError,SensorListe,iterable3)
        self.assertRaises(TypeError,SensorListe,iterable4)
        self.assertRaises(TypeError,SensorListe,iterable5)

        # __init__ muss funktionieren
        sensList1 = SensorListe(iterable1)
        for sensor in iterable1:
            sensList1.append(sensor)
        testsensList1 = SensorListe([Sensor(),s1])
        self.assertEqual(sensList1,testsensList1) #achtung!! Gilt nicht falls die reihenfolge geändert wurde
        self.assertEqual(SensorListe(),[])
        self.assertEqual(SensorListe(iterable6),SensorListe([s1]))

        # type muss gleich type(Sensorlist() sein
        self.assertEqual(SensorListe,type(sensList))
        self.assertEqual(SensorListe,type(sensList1))

        #__contains__
        self.assertEqual(self.name1 in self.sList, True)
        self.assertEqual(self.name2 in self.sList, True)
        self.assertEqual(self.ID1 in self.sList, True)
        self.assertEqual(self.ID2 in self.sList, True)
        self.assertEqual(self.s1 in self.sList, True)
        self.assertEqual(self.s2 in self.sList, True)
        self.assertTrue(self.s1_1 in self.sList)
        self.s1_1._temperatur=985
        self.assertTrue(self.s1_1 in self.sList)
        self.assertEqual(self.notExistingSensor in self.sList, False)
        self.assertEqual([] in self.sList, False)
        self.assertEqual(25 in self.sList, False)

        # index muss funktionieren
        sensList3 = SensorListe()
        for sensor in iterable1:
            sensList3.append(sensor)
        self.assertEqual(sensList3.index(s1),iterable1.index(s1))



    def test_append(self):
        ID1 = 'ID1'
        ID2 = 'ID2'
        name1 = 'Sensor1'
        name2 = 'Sensor2'

        s1 = Sensor(name=name1,temperatur=20,identifier=ID1)
        s1_1 = Sensor(name=name1,temperatur=20,identifier=ID1)
        s2 = Sensor(name=name2,temperatur=20,identifier=ID2)
        s3 = Sensor(name=name1,temperatur=10,identifier=ID1)
        sensList = SensorListe()
        sensList.append(s1)
        sensList.append(s1_1)
        self.assertTrue(s1 in sensList)
        self.assertTrue(s1_1 in sensList)
        self.assertEqual(sensList,SensorListe([s1]))
        sensList.append(s3)
        self.assertTrue(s1 in sensList)
        sensList.append(s2)
        self.assertEqual(sensList,SensorListe([s3,s2]))

    def test_getSensorName(self):
        self.assertEqual(self.sList.getSensorName(identifier=self.ID1),self.name1)
        self.assertEqual(self.sList.getSensorName(name=self.name1),self.name1)
        self.assertEqual(self.sList.getSensorName(sensor=self.s1),self.name1)
        self.assertRaises(KeyError,self.sList.getSensorName,name='not existing')

    def test_getSensorID(self):
        self.assertEqual(self.sList.getSensorID(identifier=self.ID1),self.ID1)
        self.assertEqual(self.sList.getSensorID(name=self.name1),self.ID1)
        self.assertEqual(self.sList.getSensorID(sensor=self.s1),self.ID1)
        self.assertRaises(KeyError,self.sList.getSensorID,identifier='not existing')


    def test_getSensor(self):
        self.assertEqual(self.sList.getSensor(identifier=self.ID1),self.s1)
        self.assertEqual(self.sList.getSensor(name=self.name1),self.s1)
        self.assertEqual(self.sList.getSensor(sensor=self.s1),self.s1)
        self.assertRaises(KeyError,self.sList.getSensor,sensor=self.notExistingSensor)

    def test_getAllIDs(self):
        self.assertEqual(sorted(self.sList.getAllIDs()),sorted([self.ID1,self.ID2]))

    def test_getAllNames(self):
        self.assertEqual(sorted(self.sList.getAllNames()),sorted([self.name1,self.name2]))

    def test_getALLTemperatures(self):
        self.assertEqual(self.sensList2.getAllTemperatures(),[self.temperatur1,self.temperatur2,self.temperatur3,self.temperatur4, float(self.temperatur6)])
        self.sensList2.sort(reverse=True)
        self.assertEqual(self.sensList2.getAllTemperatures(),[self.temperatur1,self.temperatur2,self.temperatur3,self.temperatur4, float(self.temperatur6)])
