#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Markus Weber'
from GlobalVariables import *
from SensorListe import SensorListe
import Communicator
from textwrap import dedent

#todo HygienePuffer Leer wenn oberste Temperatur unter 60 Grad
class Puffer(object):
    def __init__(self, Volumen, Heizkreis, Nummer = "", LadeSchwelleVoll=0.95, LadeSchwelleLeer=0.05):
        self.Volumen = Volumen
        self.Bezeichnung = BEZEICHNUNG_PUFFER + Heizkreis + Nummer
        self.Heizkreis = Heizkreis
        self.PufferSensors = SensorListe()
        self.Pumpe_Leeren = None
        self.Pumpe_Fuellen = None
        self.Ladezustand = None
        self.Leer = None
        self.Voll = None
        self._status = 'undefiniert'
        self.MaximaleTemperatur = None
        self.MinimaleTemperatur = None
        self.MinimaleStatusTemperatur = None
        self.LadeSchwelleVoll = LadeSchwelleVoll
        self.LadeSchwelleLeer = LadeSchwelleLeer

        self.VersorgungsPuffer = []
        self.VersorgtePuffer = []
        self.Mischer = []

        "dynamisches Initialisieren: Verknüpfen mit den realen Komponenten"
        self.Aktualisieren()

    def __gt__(self, other):
        """greater than"""
        if type(other) is type(self):
            return self.Volumen > other.Volumen
        elif type(other) is float or type(other) is int or type(other) is long:
            return self.Volumen > other
        else:
            return self > other


    def __ge__(self, other):
        """greater equal"""
        if type(other) is type(self):
            return self.Volumen >= other.Volumen
        elif type(other) is float or type(other) is int or type(other) is long:
            return self.Volumen >= other
        else:
            return self >= other

    def __eq__(self, other):
        """equal"""
        if type(other) is type(self):
            return self.Volumen == other.Volumen
        elif type(other) is float or type(other) is int or type(other) is long:
            return self.Volumen == other
        else:
            return self == other

    def __le__(self, other):
        """lower equal"""
        if type(other) is type(self):
            return self.Volumen <= other.Volumen
        elif type(other) is float or type(other) is int or type(other) is long:
            return self.Volumen <= other
        else:
            return self <= other

    def __lt__(self, other):
        """lower than"""
        if type(other) is type(self):
            return self.Volumen < other.Volumen
        elif type(other) is float or type(other) is int or type(other) is long:
            return self.Volumen < other
        else:
            return self < other

    def __ne__(self, other):
        """not equal"""
        return not self.Volumen == other.Volumen

    def __str__(self):
        """cast string method"""
        try:
            return str('{name:15s} {status:25s} Ladung: {ladung:3.2f}%'.format(name=self.Bezeichnung,status=self.getStatus(),ladung=self.Ladezustand*100))
        except ValueError:
            return str('{name:15s} {status:25s} Ladung: {ladung}'.format(name=self.Bezeichnung,status=self.getStatus(),ladung=self.Ladezustand))

    def html(self):
        """Gibt die daten des Puffers im html-Format zurueck"""
        # todo: html rueckgabe im Puffer implementieren

        html = dedent("""
        <h3>{name}</h3>
        <nav>
            <ul>
                <li>Volumen:                {vol}</li>
                <li>Heizkreis:              {heizkreis}</li>
                <li>Sensoren:               {sensoren}</li>
                <li>TemperaturMax:          {tempMax}</li>
                <li>TemperaturMin:          {tempMin}</li>
                <li>TemperaturMinStatus:    {tempMinStatus}</li>
                <li>SchwelleVoll:           {schwelleVoll}</li>
                <li>SchwelleLeer:           {schwelleLeer}</li>
                <li>Ladezustand:            {ladezustand}</li>
                <li>Voll:                   {voll}</li>
                <li>Leer:                   {leer}</li>
                <li>Status:                 {status}</li>
            </ul>
        </nav>""").format(name=self.Bezeichnung,
                        vol=self.Volumen,
                        heizkreis=self.Heizkreis,
                        sensoren=len(self.PufferSensors),
                        leer=self.Leer,
                        voll=self.Voll,
                        tempMax=self.MaximaleTemperatur,
                        tempMin=self.MinimaleTemperatur,
                        tempMinStatus=self.MinimaleStatusTemperatur,
                        schwelleVoll=self.LadeSchwelleVoll,
                        schwelleLeer=self.LadeSchwelleLeer,
                        ladezustand=self.Ladezustand,
                        status=self._status)
        return html

    def setEntladePumpe(self, PumpenInstanz):
        """Zuordnen einer PumpenInstanz als Entladepumpe"""
        self.Pumpe_Leeren = PumpenInstanz

    def setBeladePumpe(self, PumpenInstanz):
        """Zuordnen einer PumpenInstanz als Entladepumpe"""
        self.Pumpe_Fuellen = PumpenInstanz

    def setVersorgungsPuffer(self, PufferInstanz):
        """Zuordnen einer PufferInstanz als Puffer von dem Wasser in self stroemt"""
        self.VersorgungsPuffer.append(PufferInstanz)

    def removeVersorgungsPuffer(self, PufferInstanz):
        """Rausschmeissen der Uebergebenen PufferInstanz"""
        self.VersorgungsPuffer.remove(PufferInstanz)

    def setVersorgtePuffer(self, PufferInstanz):
        """Zuordnen einer PufferInstanz die von self beliefert wird"""
        self.VersorgtePuffer.append(PufferInstanz)

    def removeVersorgtePuffer(self, PufferInstanz):
        """Rausschmeissen der Uebergebenen PufferInstanz"""
        self.VersorgtePuffer.remove(PufferInstanz)

    def setMischer(self, MischerName):
        """Zuordnen einer MischerInstanz"""
        self.Mischer.append(MischerName)

    def removeMischer(self, MischerName):
        """Rausschmeissen der Uebergebenen MischerInstanz"""
        self.Mischer.remove(MischerName)

    def Aktualisieren(self):
        """Aktuelisiert Parameter und Anschluesse der Pumpen"""
        self.SetMinimalTemperaturen()
        self.SetMaximalTemperaturen()
        self.setPufferSensors()
        self.getLadung() # Ladezustand ermitteln

        # Refresh GPIO-Belegung
        if self.Pumpe_Leeren:
            self.Pumpe_Leeren.ControlPins()

        if self.Pumpe_Fuellen:
            self.Pumpe_Fuellen.ControlPins()

    def SetMinimalTemperaturen(self):
        """Bestimmt die unterste und die oberste geforderte Minimaltemperatur"""
        # Bestimme die Minimale Temperatur
        minimaleTemperaturen = list()
        # Suche nach minimaler Temperatur in Parameter
        minimaleTemperaturen.append(Communicator.GetParameter(self.Bezeichnung + PARAMETER_PUFFER_TEMPERATUR_MIN, ERSATZPARAMETER_PUFFER_TEMPERATUR_MIN))

        if self.VersorgtePuffer:    # Suche nach minimaler Temperatur in VersorgtePuffer[]
            for target_puffer in self.VersorgtePuffer:
                try:
                    minimaleTemperaturen.append(target_puffer.getMinTemperatur())
                except Exception as e:
                    Communicator.SchreibeFehler(e,'Aktualisieren@Puffer')

        # Suche nach minimaler MischerTemperatur
        for mischername in self.Mischer:
            mischer = Communicator.loadObjectFromServer(mischername)
            if mischer:
                try:
                    minimaleTemperaturen.append(mischer.TemperaturAusgangSoll)
                except Exception as e:
                    Communicator.SchreibeFehler(e,'Aktualisieren@Puffer')
        #print minimaleTemperaturen
        if minimaleTemperaturen:
            # Zuweisung der hoechsten mindest-Temperatur als minimalTemperatur
            self.MinimaleTemperatur = min(minimaleTemperaturen)
            self.MinimaleStatusTemperatur = max(minimaleTemperaturen)

    def SetMaximalTemperaturen(self):
        """Bestimmt die maximale Temperatur"""
        self.MaximaleTemperatur = Communicator.GetParameter(self.Bezeichnung + PARAMETER_PUFFER_TEMPERATUR_MAX, ERSATZPARAMETER_PUFFER_TEMPERATUR_MAX)

    def setPufferSensors(self, sensorListe = None):
        """Creates the Sensorlist of the Puffer"""
        #Ermitteln der zugehörigen Sensoren anhand der Namenskonvention
        self.PufferSensors = SensorListe()
        if sensorListe is None:
            sensorListe = Communicator.getSensorList()
        if sensorListe is not None:
            for sensor in sensorListe:
                if BEZEICHNUNG_SENSOR + self.Bezeichnung in sensor.getName():
                    self.PufferSensors.append(sensor)


    def getStatus(self):
        """Gibt den eigenen Zustandsstatus als integer zurück"""
        self.getLadung() # Erstmal den Ladezustand ermitteln

        if self.Pumpe_Fuellen is not None and self.Pumpe_Leeren is not None:
            if self.Pumpe_Fuellen.IstAktiv and self.Pumpe_Leeren.IstAktiv:
                self._status = STATUS_PUFFER_LEERT_UND_LAEDT
                return self._status
        if self.Pumpe_Leeren is not None:
            if self.Pumpe_Leeren.IstAktiv:
                self._status = STATUS_PUFFER_LEERT
                return self._status
        if self.Pumpe_Fuellen is not None:
            if self.Pumpe_Fuellen.IstAktiv:
                self._status = STATUS_PUFFER_LAEDT
                return self._status
        if self.Voll:
            self._status = STATUS_PUFFER_VOLL
            return self._status
        elif self.Leer:
            self._status = STATUS_PUFFER_LEER
            return self._status
        else:
            self._status = STATUS_PUFFER_NEUTRAL
            return self._status
        #return self._status

    def VolumenUeberTemperatur(self, ReferenzTemperatur):
        self.PufferSensors.refreshAllSensorTemperatures()
        Temperaturen = self.PufferSensors.getAllTemperatures()
        AnzahlSensoren = len(Temperaturen)
        if AnzahlSensoren == 0:
            Communicator.SchreibeFehler('%s hat keine Messwerte' %self.Bezeichnung, 'in Puffer.LiterUeberTemperatur()')
            return 0
        elif AnzahlSensoren > 0:
            # Falls unterster Sensor heißt genug
            if Temperaturen[-1] >= ReferenzTemperatur:
                return self.Volumen
            # Falls oberster Sensor zu kalt
            if ReferenzTemperatur >= Temperaturen[0]:
                return 0
            # Falls irgendwo dazwischen muss interpoliert werden:
            for i in range(1,AnzahlSensoren):
                sensorHeiss = i-1
                sensorKalt = i
                if Temperaturen[sensorHeiss] >= ReferenzTemperatur >= Temperaturen[sensorKalt]:
                    # Interpolieren zwischen den beiden Sensoren
                    DeltaT = Temperaturen[sensorHeiss] - Temperaturen[sensorKalt]
                    DeltaTVonHeissemSensor = Temperaturen[sensorHeiss] - ReferenzTemperatur
                    if DeltaT < ERSATZPARAMETER_PUFFER_TEMPERATUR_SCHWELLWERT:
                        AnteilInterpolierterVolumenInteravall = 1
                    else:
                        AnteilInterpolierterVolumenInteravall = DeltaTVonHeissemSensor/DeltaT
                    VolumenIntervalle = AnzahlSensoren - 1
                    VolleVolumenIntervalle = sensorHeiss
                    VollerPufferAnteil = (VolleVolumenIntervalle + AnteilInterpolierterVolumenInteravall) / VolumenIntervalle
                    return VollerPufferAnteil*self.Volumen
        else:
            Communicator.SchreibeFehler('%s hat %i Sensoren' %(self.Bezeichnung,AnzahlSensoren), 'in Puffer.LiterUeberTemperatur()')
            return 0

    def VolumenUnterTemperatur(self, ReferenzTemperatur):
        return self.Volumen - self.VolumenUeberTemperatur(ReferenzTemperatur=ReferenzTemperatur)

    def getLadung(self): # Ladezustand ermitteln
        # todo: Ladezustand an einer anderen Minimaltemperatur roientieren als Status
        # todo: Ladestatus der Puffer abhängig machen von : Mischer, anderen Puffer und Pauschaltemperaturen

        DeltaTNutz = []
        for temperatur in self.PufferSensors.getAllTemperatures():
            if temperatur is not None and self.MinimaleTemperatur is not None:
                if (temperatur - self.MinimaleTemperatur) <= 0:
                    DeltaTNutz.append(0)
                else:
                    DeltaTNutz.append(temperatur - self.MinimaleTemperatur)
        if DeltaTNutz:
            #Berechnung des Ladezustandes
            self.Ladezustand = (sum(DeltaTNutz) / len(DeltaTNutz)) / (self.MaximaleTemperatur - self.MinimaleTemperatur)
            self.Ladezustand = round(self.Ladezustand, ROUNDED_PERCENTAGE_DIGITS)
        else: # Falls Keine Temperaturen vorhanden sind
            self.Ladezustand = UNBEKANNTER_PUFFER_LADEZUSTAND
            return self.Ladezustand

        if self.Ladezustand < 0:
            self.Ladezustand = .0
        elif self.Ladezustand > 1:
            self.Ladezustand = 1.
            try:
                if Communicator.GetParameter(PARAMETER_FEHLER_FALLS_PUFFER_VOLL):
                    Communicator.SchreibeFehler("%s Ladezustand ist bei %.2f %%" % (self.Bezeichnung, (self.Ladezustand * 100)), "ErmittleLadezustand")
            except Exception as e:
                Communicator.SchreibeFehler(e.message + '- Ersatzparameter uebernommen', 'in getLadung@GetParameter' )
                if ERSATZPARAMETER_FEHLER_FALLS_PUFFER_VOLL:
                    #Communicator.SchreibeFehler("%s Ladezustand ist bei %.2f %%" % (self.Bezeichnung, (self.Ladezustand * 100)), "ErmittleLadezustand")
                    print ("%s Ladezustand ist bei %.2f" % (self.Bezeichnung, (self.Ladezustand * 100)))

        self.aktualisiereLadeStatus()
        return self.Ladezustand

    def aktualisiereLadeStatus(self):
        """Aktualisiert self.Voll und self.Leer"""
        # Ladestatus ueber einzelne Sensoren
        parameter = Communicator.GetParameter()
        for sensor in self.PufferSensors:
            #Suche die Maximalen und Minimalen Parameterwerte aus der parameterListe raus
            sensorTemperaturMax = sensor.getName() + POSTFIX_MAXIMAL
            sensorTemperaturMin = sensor.getName() + POSTFIX_MINIMAL
            if sensorTemperaturMax in parameter.keys():
                # Schau ob der Puffer voll ist
                if sensor.getTemperatur() >= parameter[sensorTemperaturMax]:
                    self.Voll = True
                    self.Leer = False
                    return
            if sensorTemperaturMin in parameter.keys():
                # Schau ob der Puffer leer ist
                if sensor.getTemperatur() < parameter[sensorTemperaturMin]:
                    self.Voll = False
                    self.Leer = True
                    return

        # Ladestatus ueber gesamtschnitt
        if isinstance(self.Ladezustand, str):
            self.Voll = False
            self.Leer = False
        elif self.Ladezustand > self.LadeSchwelleVoll:
            self.Voll = True
            self.Leer = False
            return
        elif self.Ladezustand < self.LadeSchwelleLeer:
            self.Voll = False
            self.Leer = True
            return
        else:
            self.Voll = False
            self.Leer = False

    def getMaxTemperatur(self):
        try:
            return max(self.PufferSensors.getAllTemperatures())
        except ValueError:
            return None

    def getMinTemperatur(self):
        try:
            return min(self.PufferSensors.getAllTemperatures())
        except ValueError:
            return None

    def kannKomplettFuellen(self, other):
        return self.VolumenUeberTemperatur(other.MaximaleTemperatur) > other.VolumenUnterTemperatur(other.MaximaleTemperatur)

    def EntladepumpeEin(self, prioritaet = 0):
        if not self.Pumpe_Leeren.IstAktiv:
            print ("{Pumpe} schaltet ein".format(Pumpe=self.Pumpe_Leeren.Bezeichnung))
        self.Pumpe_Leeren.Ein(prioritaet)  # Entladepumpe einschalten

    def EntladepumpeAus(self, prioritaet = 0):
        if self.Pumpe_Leeren.IstAktiv:
            print ("{Pumpe} schaltet aus".format(Pumpe=self.Pumpe_Leeren.Bezeichnung))
        self.Pumpe_Leeren.Aus(prioritaet)  # Entladepumpe ausschalten

    def BeladepumpeEin(self, prioritaet = 0):
        if not self.Pumpe_Fuellen.IstAktiv:
            print ("{Pumpe} schaltet ein".format(Pumpe=self.Pumpe_Fuellen.Bezeichnung))
        self.Pumpe_Fuellen.Ein(prioritaet)  # Beladepumpe einschalten

    def BeladepumpeAus(self, prioritaet = 0):
        if self.Pumpe_Fuellen.IstAktiv:
            print ("{Pumpe} schaltet aus".format(Pumpe=self.Pumpe_Fuellen.Bezeichnung))
        self.Pumpe_Fuellen.Aus(prioritaet)  # Beladepumpe ausschalten

    # def EntladepumpeBlockieren(self, prioritaet = 0):
    #     self.Pumpe_Leeren.Blockiert = True  # Entladepumpe blockieren
    #
    # def EntladepumpeFreigeben(self, prioritaet = 0):
    #     self.Pumpe_Leeren.Blockiert = False  # Entladepumpe blockieren
    #
    # def BeladepumpeBlockieren(self, prioritaet = 0):
    #     self.Pumpe_Fuellen.Blockiert = True  # Beladepumpe ausschalten
    #
    # def BeladepumpeFreigeben(self, prioritaet = 0):
    #     self.Pumpe_Fuellen.Blockiert = False  # Beladepumpe ausschalten

def main():
    pass


if __name__ == "__main__":
    main()