#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase

__author__ = 'Markus Weber'
from Sensor import Sensor
from GlobalVariables import *
from Communicator import getSlaveList

def main():
    pass

if __name__ == "__main__":
    main()

class TestSensor(TestCase):
    def test_specialMethods(self):
        s1 = Sensor(name='a', temperatur=20)
        s2 = Sensor(name='a', temperatur=-20)
        s3 = Sensor(name='b', temperatur=20)
        s4 = Sensor(name='a', temperatur=20, identifier='someID')
        s4_2 = Sensor(name='a', temperatur=20, identifier='someID')
        s5 = Sensor(name='a', temperatur=20, identifier='someID')
        s6 = Sensor(name='b', temperatur=20, identifier='someID')
        s7 = Sensor(name='a', temperatur=10, identifier='someID')
        s8 = Sensor(name='a', temperatur=20, identifier='someotherID')

        self.assertGreater(s3, s1)
        self.assertNotEqual(s1, s2)
        self.assertEqual(s4, s5)
        s5._temperatur = 40
        self.assertNotEqual(s4, s5)
        self.assertNotEqual(s4, s6)
        self.assertNotEqual(s4, s7)
        s7._temperatur = 20
        self.assertEqual(s4, s7)
        self.assertNotEqual(s4, s8)
        self.assertLess(s1, s3)

        self.assertFalse(s1 == 25)
        self.assertFalse(s1 == 'kack')
        self.assertFalse(s1 == Sensor())
        self.assertFalse(s1 == s3)
        self.assertFalse(s1 == s2)
        self.assertTrue(s4 == s4_2)
        self.assertTrue(s4 != s5)
        self.assertFalse(s1 > 25.456)
        self.assertFalse(s1 > long(25.456))
        self.assertTrue(s1 > None)


    def test__memoryInsert(self):
        s1 = Sensor(name="s1", identifier='someID1', memorysize=0)
        s2 = Sensor(name="s2", identifier='someID2', memorysize=5)
        s3 = Sensor(name="s3", identifier='someID3', memorysize=500)
        s4 = Sensor(name="s4", identifier='someID4', memorysize=-1)

        testTemperatur1 = 25
        testTemperatur2 = -25
        testTemperatur3 = 500


        for i in range(s1._memorysize + 2):
            s1.memoryInsert(testTemperatur1)

        for i in range(s2._memorysize + 2):
            s2.memoryInsert(testTemperatur1)
            s2.memoryInsert(testTemperatur2)
            s2.memoryInsert(testTemperatur3)

        for i in range(s3._memorysize + 2):
            s3.memoryInsert(testTemperatur1)
            s3.memoryInsert(testTemperatur2)
            s3.memoryInsert(testTemperatur3)

        s4.memoryInsert(testTemperatur1)
        s4.memoryInsert(testTemperatur2)
        s4.memoryInsert(testTemperatur3)


        self.assertEqual(len(s1.memory), s1._memorysize)
        self.assertEqual(len(s2.memory), s2._memorysize)
        self.assertEqual(len(s3.memory), s3._memorysize)
        self.assertEqual(len(s4.memory), 0)


        for i in range(s1._memorysize):
            self.assertEqual(s1.memory[i][0], testTemperatur1)

        for i in range(s2._memorysize,2,3):
            self.assertEqual(s2.memory[i-2][0], testTemperatur1)
            self.assertEqual(s2.memory[i-1][0], testTemperatur2)
            self.assertEqual(s2.memory[i][0], testTemperatur3)

        for i in range(s3._memorysize,2,3):
            self.assertEqual(s3.memory[i-2][0], testTemperatur1)
            self.assertEqual(s3.memory[i-1][0], testTemperatur2)
            self.assertEqual(s3.memory[i][0], testTemperatur3)

        for i in range(s4._memorysize):
            self.assertEqual(s1.memory[i][0], testTemperatur1)

        s2.memoryInsert(5)
        self.assertEqual(s2.memory[0][0],5)
        s3.memoryInsert(5)
        self.assertEqual(s3.memory[0][0],5)

    def test_measure(self):
        s1 = Sensor(identifier='28-00044c86c8ff')
        s2 = Sensor('kaswurscht')
        s1.measure()
        s2.measure()
        if type(s1._temperatur) is str:
            print ('Warnung: Sensor in test_measure nicht ansprechbar!')
            self.assertIsInstance(s1._temperatur, str)
        else:
            self.assertIsInstance(s1._temperatur, float)
        self.assertEqual(s2._temperatur, SENSOR_OFFLINE)

    def test_isLinked(self):
        slaveList = getSlaveList()
        for identifier in slaveList:
            sensor = Sensor(identifier=identifier)
            self.assertTrue(sensor.isLinked())

        s2 = Sensor(identifier='kaswurscht')
        self.assertFalse(s2.isLinked())

    def test_getID(self):
        ID1 = 'someID'
        s1 = Sensor(name='a', temperatur=20, identifier=ID1)
        self.assertEqual(s1.getID(), ID1)

    def test_setID(self):
        ID1 = 'someID'
        s1 = Sensor(name='a', temperatur=20, identifier=ID1)
        newID = 'someNewId'
        s1.setID(newID)
        self.assertEqual(s1.getID(), newID)

    def test_getTemperatur(self):
        temperatur = 85
        ID1 = 'someID'
        s1 = Sensor(name='a', temperatur=temperatur, identifier=ID1)
        self.assertEqual(s1.getTemperatur(), temperatur)

    def test_setTemperatur(self):
        ID1 = 'someID'
        temperatur = 85
        newTemperatur = 40
        s1 = Sensor(name='a', temperatur=temperatur, identifier=ID1)
        s1.setTemperatur(newTemperatur)
        self.assertEqual(s1.getTemperatur(), newTemperatur)

    def test_getName(self):
        name1 = 'someName'
        ID1 = 'someID'
        s1 = Sensor(name='a', temperatur=20, identifier=ID1)
        self.assertTrue(s1.getName(), name1)

    def test_reset(self):
        name1 = 'someName'
        ID1 = 'someID'
        s1 = Sensor(name='a', temperatur=20, identifier=ID1)
        emptySensor = Sensor(name=name1)
        s1.reset()
        self.assertTrue(s1, emptySensor)