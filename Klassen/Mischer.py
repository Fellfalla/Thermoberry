#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Markus Weber'
import RPi.GPIO as GPIO
import Klassen.Communicator as Communicator
from GlobalVariables import *
import time
import socket
from textwrap import dedent

class Mischer:
    def __init__(self, Aufstellort, versorgungsPuffer=None):
        if not versorgungsPuffer:
            versorgungsPuffer = []

        self.Aufstellort = Aufstellort
        self._name = BEZEICHNUNG_MISCHER + self.Aufstellort
        self.MischerWaermer = BEZEICHNUNG_MISCHER + self.Aufstellort + WAERMER_POSTFIX  # Benennung der Pins in GPIO datei
        self.MischerKaelter = BEZEICHNUNG_MISCHER + self.Aufstellort + KAELTER_POSTFIX  # Benennung der Pins in GPIO datei
        # werte die vor dem ersten durchlauf nicht ermittelt werden können
        self.versorgungsPuffer = versorgungsPuffer
        self.SensorTemperaturMischer = BEZEICHNUNG_MISCHERSENSOR + Aufstellort

        # try:
        #     self.TemperaturAusgang = Communicator.GetSensorTemperatur(BEZEICHNUNG_MISCHERSENSOR + self.Aufstellort)  # C
        # except Exception as e:
        #     self.TemperaturAusgang = None
        #     print (e.message)

        self.EinschaltDauer = None

        #Werte die Aktualisiert werden können
        self.Parameter = None
        self.TemperaturAusgang = None
        self.TemperaturAusgangAlt = None  # C
        self.VirtuellesDeltaT = None
        self.DeltaTAusgangSollIst = 0
        self.PinWaermer = None
        self.PinKaelter = None
        self.TemperaturAussen = None
        self.DeltaTStart = None
        self.TemperaturAusgangSoll = None  # C
        self.TempZeitKoeff = None
        self.Zyklenzeit = None
        self.TemperaturRaumSoll = None
        self.Tag = None
        self.Heizbetrieb = None
        self.HeizTMin = None
        self.status = STATUS_MISCHER_IDLE


    def __str__(self):
        # detent um triple-quote strings einruecken zu koennen, ohne dass diese im string als einrueckung gewertet wird
        return dedent("""\
        {name}:
                 Heizbetrieb : {aktiv:7s} (min{heizmin}°C)
                 GPIO-Wärmer : {iowarm:02d}
                 GPIO-Kälter : {iokalt:02d}
                Tagschaltung : {tag}
                  Zykluszeit : {zykluszeit} s
                   Raum-Soll : {raumsoll} °C
            Aussentemperatur : {aussentemp} °C
                   Hysterese : {hysterese} °C
                Ausgang-Soll : {ausgangsoll} °C
                 Ausgang-Ist : {ausgangist} °C
                      Status : {status}""").format(name=self.getName(),
                                             aktiv=str(self.Heizbetrieb),
                                             heizmin=str(self.HeizTMin),
                                             iowarm=self.PinWaermer,
                                             iokalt=self.PinKaelter,
                                             raumsoll=self.TemperaturRaumSoll,
                                             aussentemp=self.TemperaturAussen,
                                             hysterese=self.DeltaTStart,
                                             ausgangsoll=self.TemperaturAusgangSoll,
                                             ausgangist=self.TemperaturAusgang,
                                             zykluszeit=self.Zyklenzeit,
                                             status=self.status,
                                             tag=self.Tag)

    def html(self):
        # todo: das hier machmache sodass a gscheide webseite zurueckgem werd
        pass

    def getName(self):
        return self._name

    def AktualisierePins(self):
        GPIOPins = Communicator.GetGPIO()
        if self.PinWaermer != GPIOPins[self.MischerWaermer]:
            self.CleanGPIOPins()
            self.SetGPIOPins()
        elif self.PinKaelter != GPIOPins[self.MischerKaelter]:
            self.CleanGPIOPins()
            self.SetGPIOPins()

    def CleanGPIOPins(self):
        try:
            GPIO.cleanup(self.PinWaermer)
            GPIO.cleanup(self.PinKaelter)
        except TypeError:
            print("TypeError in CleanGPIOPins")
        except ValueError:
            print("ValueError in CleanGPIOPins")


    def SetGPIOPins(self):
        GPIOPins = Communicator.GetGPIO()
        try:
            self.PinWaermer = GPIOPins[self.MischerWaermer]
            self.PinKaelter = GPIOPins[self.MischerKaelter]
            GPIO.setup(self.PinWaermer, GPIO.OUT)
            GPIO.setup(self.PinKaelter, GPIO.OUT)
            GPIO.output(self.PinWaermer, GPIO.HIGH)
            GPIO.output(self.PinKaelter, GPIO.HIGH)
        except KeyError:
            Communicator.SchreibeFehler(
                "Pins nicht belget oder falsch benannt! Korrekter Name: " + self.MischerWaermer + " oder " + self.MischerKaelter + "!",
                'SetGPIOPins')
            time.sleep(10)  # Solange durchfuehren bis Passender Wert drin ist
            self.SetGPIOPins()


    def KalkuliereAusgangSollTemperatur(self):
        self.TemperaturAussen = Communicator.GetSensorTemperatur(BEZEICHNUNG_AUSSENSENSOR)
        if isinstance(self.TemperaturAussen, basestring):
            Communicator.SchreibeFehler('AussentemperaturSensor: ' + self.TemperaturAussen, 'GetSollTemperatur')
            try:
                self.TemperaturAussen = self.Parameter[PARAMETER_NOTFALL_AUSSENTEMPERATUR]
            except KeyError:
                self.TemperaturAusgangSoll = Communicator.GetParameter(PARAMETER_NOTFALL_HEIZUNG_VORLAUF_SOLL, ERSATZPARAMETER_HEIZUNG_VORLAUF_SOLL)
                return

        steigung = Communicator.GetParameter(PARAMETER_HEIZUNG_VORLAUF_STEIGUNG, ERSATZPARAMETER_HEIZUNG_VORLAUF_STEIGUNG)
        parallelverschiebung = Communicator.GetParameter(PARAMETER_HEIZUNG_VORLAUF_ANHEBUNG, ERSATZPARAMETER_HEIZUNG_VORLAUF_ANHEBUNG)

        if self.TemperaturRaumSoll is not None and self.TemperaturAussen is not None: # Basiswerte für Berechnung sind gegeben
            DeltaT = self.TemperaturRaumSoll - self.TemperaturAussen
            DeltaTStart = Communicator.GetParameter(PARAMETER_DELTA_TEMPERATUR_INNEN_AUSSEN_MIN, ERSATZPARAMETER_DELTA_TEMPERATUR_INNEN_AUSSEN_MIN)
            if DeltaT <= DeltaTStart or DeltaT < 0:   # Falls DeltaTAusgangSollIst kleiner als ein minimales DeltaTAusgangSollIst ist, ist kein Heizbetrieb notwendig
                 self.SetHeizbetrieb(False)  # Mischer und Pumpe ausschalten
                 self.TemperaturAusgangSoll = self.TemperaturAusgang
            else:
                self.TemperaturAusgangSoll = steigung * DeltaT ** 0.5 + self.TemperaturRaumSoll + parallelverschiebung

            if self.TemperaturAusgangSoll > ERSATZPARAMETER_HEIZUNG_VORLAUF_BEGRENZUNG:  # Begrenzung nach oben
                self.TemperaturAusgangSoll = ERSATZPARAMETER_HEIZUNG_VORLAUF_BEGRENZUNG
        else:
            self.TemperaturAusgangSoll = ERSATZPARAMETER_HEIZUNG_VORLAUF_SOLL

        #zum ende hin noch runden
        self.TemperaturAusgangSoll = round(self.TemperaturAusgangSoll,ROUNDED_TEMPERATURE_DIGITS)
        return self.TemperaturAusgangSoll

    def KalkuliereRaumSollTemperatur(self,value=None):
        """Setzt die gewuenschte Raumtemperatur im Hinblick auf Eingabeparameter und Umgebungsvariablen des Mischers"""
        if value is not None:
            self.TemperaturRaumSoll = bool(value)
        else:
            try:
                self.Tag = Communicator.GetTageszeit(self.Parameter[PARAMETER_TAG_BEGINN], self.Parameter[PARAMETER_TAG_ENDE])
            except KeyError:
                print("KeyError: Parameter[\"%s\"],Parameter[\"%s\"] fehlen -> Tag = True !!!" %(PARAMETER_TAG_BEGINN, PARAMETER_TAG_ENDE))
                self.Tag = True
            if self.Tag:
                try:
                    self.TemperaturRaumSoll = self.Parameter[PARAMETER_TEMPERATUR_ZIMMER_TAG_SOLL]
                except KeyError:
                    self.TemperaturRaumSoll = ERSATZPARAMETER_TEMPERATUR_ZIMMER_TAG_SOLL
                    print("!!ERSATZPARAMETER_TEMPERATUR_ZIMMER_TAG_SOLL!!" )
            else:
                try:
                    self.TemperaturRaumSoll = self.Parameter[PARAMETER_TEMPERATUR_ZIMMER_NACHT_SOLL]
                except KeyError:
                    self.TemperaturRaumSoll = ERSATZPARAMETER_TEMPERATUR_ZIMMER_NACHT_SOLL
                    print("!!ERSATZPARAMETER_TEMPERATUR_ZIMMER_NACHT_SOLL!!")
        return self.TemperaturRaumSoll

    def SetHeizbetrieb(self, value=None):
        """Setzt den Heizbetrieb-Flag im Hinblick auf Eingabeparameter und Umgebungsvariablen des Mischers"""
        if value is not None:
            if self.Heizbetrieb is True and value is False: # Falls bisher Heizbetrieb war -> Mischer komplett schließen
                self.KomplettKalt()
            self.Heizbetrieb = bool(value)
        else:
            self.Heizbetrieb = True
            # Heizbetrieb abschalten, wenn die benötigte Temperatur nicht geliefert werden kann
            if self.versorgungsPuffer:  # Teste ob einer zugewiesen wurde
                # Ermittel die maximale lieferbare Temperatur
                versorgungspuffer = Communicator.loadObjectFromServer(name=self.versorgungsPuffer)
                if versorgungspuffer is None:
                    SchreibeFehler(self.versorgungsPuffer + " auf dem server nicht vorhanden. Heizbetrieb nicht möglich")
                
                
                # Abschalten falls minimaltemperatur unterschritten wurde
                try:
                    self.HeizTMin = self.Parameter[PARAMETER_HEIZBETRIEB_MINIMALTEMPERATUR]
                except KeyError:
                    self.HeizTMin = ERSATZPARAMETER_HEIZBETRIEB_MINIMALTEMPERATUR
                    print("!!ERSATZPARAMETER_HEIZBETRIEB_MINIMALTEMPERATUR!!")
                if versorgungspuffer.getMaxTemperatur() < self.HeizTMin:
                    self.SetHeizbetrieb(False)
                    return

            if self.TemperaturRaumSoll is not None and self.TemperaturAussen is not None:
                # Heizbetrieb abschalten, wenns draussen zu warm ist
                self.DeltaTStart = self.Parameter[PARAMETER_DELTA_TEMPERATUR_INNEN_AUSSEN_MIN]
                DeltaT = self.TemperaturRaumSoll - self.TemperaturAussen
                if DeltaT <= self.DeltaTStart:
                    self.SetHeizbetrieb(False)
                    return

    def StarteRegelZyklus(self):
        """
        Regelt den Mischer auf die gewünschte Ausgangstemperatur einen Zyklus lange.
        Die Zyklusdauer muss vorher festgelegt werden
        :return:
        """
        print ('\n')
        # ## Alle Notwendigen Daten sammeln ###
        self.Parameter = Communicator.GetParameter()  # Liest Parameter aus Datei ein !!!PARAMETERNAMEN NICHT VERAENDERN!!!!!
        try:
            self.TemperaturAusgang = Communicator.GetSensorTemperatur( BEZEICHNUNG_MISCHERSENSOR + self.Aufstellort)
        except Exception as e:
            Communicator.SchreibeFehler(e.message + '- die Mischertemperatur ist nicht verfuegbar', 'RegelZyklus@Mischer')

        ###________________________________###
        if self.Parameter[PARAMETER_MISCHER_MODUS] == 1:  #Waermer
            print("Parameter %s ist auf Waermer eingestellt" %PARAMETER_MISCHER_MODUS)
            print("AusgangsTemperatur: %-20s" % self.TemperaturAusgang)
            self.SetHeizbetrieb(value=True)
            self.EinschaltDauer = self.GetZyklenzeit()
            self.Waermer(dauerAktiv=self.EinschaltDauer)
            return
        elif self.Parameter[PARAMETER_MISCHER_MODUS] == 2:  #Kaelter
            print("Parameter %s ist auf Kaelter eingestellt" %PARAMETER_MISCHER_MODUS)
            print("AusgangsTemperatur: %-20s" % self.TemperaturAusgang)
            self.SetHeizbetrieb(value=True)
            self.EinschaltDauer = self.GetZyklenzeit()
            self.Kaelter(dauerAktiv=self.EinschaltDauer)
            return
        elif self.Parameter[PARAMETER_MISCHER_MODUS] == 3:  #Handbetrieb
            print ('Parameter %s ist auf Handbetrieb eingestellt' %PARAMETER_MISCHER_MODUS)
            print("AusgangsTemperatur: %-20s" % self.TemperaturAusgang)
            self.SetHeizbetrieb(value=True)
            self.EinschaltDauer = 0
            self.Idle(dauer=self.GetZyklenzeit()) # Setzt die Pins zurueck
            return
        elif self.Parameter[PARAMETER_MISCHER_MODUS] == 4:  #Sleep
            print ('Parameter %s ist auf Sleep-Modus eingestellt' %PARAMETER_MISCHER_MODUS)
            print("AusgangsTemperatur: %-20s" % self.TemperaturAusgang)
            self.SetHeizbetrieb(value=False)
            self.EinschaltDauer = 0
            self.Idle(dauer=self.GetZyklenzeit())
            return
        elif self.Parameter[PARAMETER_MISCHER_MODUS] == 0:  # 0-automatic
            self.Regeln()  #Daten anwenden

    def Kalkulieren(self):
        self.TesteAusgangsSensorAufFehler()
        self.SetHeizbetrieb()
        self.KalkuliereRaumSollTemperatur()
        self.KalkuliereAusgangSollTemperatur()
        self.KalkuliereEinschaltDauer()

    def Aktualisieren(self):
        self.Parameter = Communicator.GetParameter()
        self.AktualisierePins() # Pins sind evtl. abhängig von self.Parameter
        self.AktualisiereTemperaturen()

    def AktualisiereTemperaturen(self):
        self.TemperaturAusgang = Communicator.GetSensorTemperatur(BEZEICHNUNG_MISCHERSENSOR + self.Aufstellort)

    def TesteAusgangsSensorAufFehler(self):
        while type(self.TemperaturAusgang) == str:
            Communicator.SchreibeFehler( BEZEICHNUNG_MISCHERSENSOR + self.Aufstellort + ":" + self.TemperaturAusgang,
                                         'TestSensorFehler')
            time.sleep(10)
            try:
                self.TemperaturAusgang = Communicator.GetSensorTemperatur( BEZEICHNUNG_MISCHERSENSOR + self.Aufstellort)
            except Exception as e:
                Communicator.SchreibeFehler(e.message + '- die Mischertemperatur ist nicht verfuegbar', 'RegelZyklus@Mischer')

    def PrintParameterWerte(self):
        print('Regelung von Mischer ' + self.Aufstellort + ' auf Basis folgender Werte:')
        print('Uhrzeit: %-20s' % time.strftime("%d.%m.%Y %H:%M:%S"))
        print (self)

    def Regeln(self, dauerZyklus=None):
        if dauerZyklus is None:
            dauerZyklus = self.GetZyklenzeit()
        if not self.Heizbetrieb:
            print("Kein Heizbetrieb")
            self.Idle(dauer=dauerZyklus)
            return
        try:
            Hysterese = self.Parameter[PARAMETER_MISCHER_HYSTERESE]
        except KeyError:
            Hysterese = ERSATZPARAMETER_MISCHER_HYSTERESE
        if self.VirtuellesDeltaT > Hysterese:
            self.Waermer(dauerAktiv=self.EinschaltDauer, dauerInaktiv=dauerZyklus-self.EinschaltDauer)
        elif abs(self.VirtuellesDeltaT) > Hysterese:
            self.Kaelter(dauerAktiv=self.EinschaltDauer, dauerInaktiv=dauerZyklus-self.EinschaltDauer)
        else:
            self.Idle(dauer=dauerZyklus)

    def KalkuliereEinschaltDauer(self):
        try:
            Tendenz = self.TemperaturAusgang - self.TemperaturAusgangAlt
        except TypeError:
            Tendenz = 0
        self.TemperaturAusgangAlt = self.TemperaturAusgang
        try:
            Tendenzgewichtung = self.Parameter[PARAMETER_MISCHER_TENDENZGEWICHTUNG]
        except KeyError:
            Tendenzgewichtung = ERSATZPARAMETER_MISCHER_TENDENZGEWICHTUNG
        
        try:
            self.VirtuellesDeltaT = (self.GetDeltaT() - Tendenzgewichtung * Tendenz)
        except TypeError:
            print("Warning: Unzureichende Temperaturinformationen")
            self.VirtuellesDeltaT = 0

        self.EinschaltDauer = abs(self.VirtuellesDeltaT) * float(self.GetTempZeitKoeff())

        if self.EinschaltDauer > self.Zyklenzeit:
            self.EinschaltDauer = self.Zyklenzeit
        if self.EinschaltDauer < ERSATZPARAMETER_MISCHER_EINSCHALTZEIT_MIN:
            self.EinschaltDauer = 0


    def GetDeltaT(self):
        self.DeltaTAusgangSollIst = self.TemperaturAusgangSoll - self.TemperaturAusgang
        return self.DeltaTAusgangSollIst
        

    def GetZyklenzeit(self):
        try:
            self.Zyklenzeit = self.Parameter[PARAMETER_MISCHER_ZYKLENZEIT]
        except KeyError:
            Communicator.SchreibeFehler("KeyError in Mischer" + self.Aufstellort + ": %s fehlt!"%PARAMETER_MISCHER_ZYKLENZEIT, 'GetZyklenzeit' )
            self.Zyklenzeit = ERSATZPARAMETER_ZYKLENZEIT_MISCHER
        return self.Zyklenzeit

    def GetTempZeitKoeff(self):
        try:
            self.TempZeitKoeff = self.Parameter[PARAMETER_TEMPERATUR_ZEIT_KOEFFIZIENT]
        except KeyError:
            Communicator.SchreibeFehler("KeyError in Mischer" + self.Aufstellort + ": %s fehlt!" %PARAMETER_TEMPERATUR_ZEIT_KOEFFIZIENT, 'GetTempZeitKoeff')
            self.TempZeitKoeff = ERSATZPARAMETER_TEMPERATUR_ZEIT_KOEFFIZIENT
        return self.TempZeitKoeff

    def Waermer(self, dauerAktiv=0, dauerInaktiv=0):
        #print("Mischer macht %4.1f %% Waermer" % (self.EinschaltAnteil * 100))
        self.SetEinschaltAnteil(dauerAktiv, dauerInaktiv)

        self.status = "Mischer macht {prozent:4.1f}% Waermer".format(prozent=self.EinschaltAnteil)
        if dauerAktiv > 0: # Verhindert kurzes einschalten bei einem einschaltAnteil gleich 0
            self.GPIOHIGH(self.PinKaelter)
            self.GPIOLOW(self.PinWaermer)
            time.sleep(dauerAktiv)
        if dauerInaktiv > 0: # Verhindert kurzes ausschalten bei einem einschaltAnteil gleich 1
            GPIO.output(self.PinWaermer, GPIO.HIGH)
            time.sleep(dauerInaktiv)

    def Kaelter(self, dauerAktiv=0, dauerInaktiv=0):
        #print("Mischer macht %4.1f %% Kaelter" % (self.EinschaltAnteil * 100))
        self.SetEinschaltAnteil(dauerAktiv, dauerInaktiv)

        self.status = "Mischer macht {prozent:4.1f}% Kaelter".format(prozent=self.EinschaltAnteil)
        if dauerAktiv > 0: # Verhindert kurzes einschalten bei einem einschaltAnteil gleich 0
            self.GPIOHIGH(self.PinWaermer)
            self.GPIOLOW(self.PinKaelter)
            time.sleep(dauerAktiv)
        if dauerInaktiv > 0: # Verhindert kurzes ausschalten bei einem einschaltAnteil gleich 1
            GPIO.output(self.PinKaelter, GPIO.HIGH)
            time.sleep(dauerInaktiv)


    def SetEinschaltAnteil(self, dauerAktiv=0, dauerInaktiv=0):
        """Setzt den prozentualen Zyklusanteil, in der der Mischer seinen Zustand verändert"""
        if(dauerInaktiv > 0 or dauerAktiv > 0):
            self.EinschaltAnteil = (dauerAktiv / (dauerAktiv + dauerInaktiv)) * 100
        else:
            self.EinschaltAnteil = 0 # Beide werte sind auf 0

    def KomplettKalt(self):
        print("Mischer macht komplett zu")
        self.Kaelter(dauerAktiv=5*60, dauerInaktiv=0) # muss nicht abgeschaltet werden, da beim nächsten regelzyklus Idle aktiviert wird


    def Idle(self, dauer=None):
        self.status = STATUS_MISCHER_IDLE
        self.GPIOHIGH(self.PinWaermer)
        self.GPIOHIGH(self.PinKaelter)
        if dauer is None:
            time.sleep(self.Zyklenzeit)
        else:
            time.sleep(dauer)

    @staticmethod
    def GPIOHIGH(Pin):
        if GPIO.input(Pin) == GPIO.LOW:
            GPIO.output(Pin, GPIO.HIGH)

    @staticmethod
    def GPIOLOW(Pin):
        if GPIO.input(Pin) == GPIO.HIGH:
            GPIO.output(Pin, GPIO.LOW)


def main():
    pass


if __name__ == "__main__":
    main()