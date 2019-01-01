#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase

from Modules.SensorAuswertung import SensorListe
from Sensor import Sensor

__author__ = 'Markus Weber'


def main():
    pass


if __name__ == "__main__":
    main()


class TestSensorAuswertung(TestCase):
    s1 = Sensor(name='sens1', temperatur=20, identifier='someID')
    s1_2 = Sensor(name='sens1', temperatur=20, identifier='someID')
    s2 = Sensor(name='sens2', temperatur=20, identifier='someotherID')
    s3 = Sensor(name='sens3', temperatur=20, identifier='someveryotherID')
    sList1 = SensorListe([s1,s2,s3])
    sList2 = SensorListe([s1,s1_2,s2,s3])

    sList3 = SensorListe()
    sList4 = SensorListe()
    sList5 = SensorListe()


    def test_checkSensorIDs(self):
        self.fail()

    def test_checkSensorNames(self):
        self.fail()

    def test__assignID(self):
        self.fail()

    def test_measurePrececdure(self):
        self.fail()

    def test_SensorValueCleaner(self):
        self.fail()

    def test_AusgabeMesswerte(self):
        self.fail()