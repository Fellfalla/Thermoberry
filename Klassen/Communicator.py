#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import cPickle as pickle
import time
import datetime
import xmlrpclib
import SensorListe
from GlobalVariables import *
import traceback
import socket
import ConfigParser as configparser

FLOCK_OS_NAME = 'posix'
FLOCK_ENABLED = os.name is FLOCK_OS_NAME
if FLOCK_ENABLED:
    import fcntl
else:
    print("Warning: File locking only on " + FLOCK_OS_NAME + " systems available")

DATA_SERVER_ADDRESS = 'http://'+ DATENSERVER_NAME +':{port}'.format(port=PORT_DATENSERVER)

def load_sensor_name(sensor_id):
    """
    :param sensor_id: Die ID des Sensors.
    :returns: Name des Sensors oder None falls sensor nicht vorhanden
    """
    # Laden der Konfigurationsdatei
    config_parser = configparser.ConfigParser()
    config_parser.read(SENSOR_MAPPING_FILE_PATH)
    try:
        sensor_name = config_parser.get('DEFAULT', sensor_id, None)
    except configparser.NoOptionError:
        sensor_name = None
        
    return sensor_name

def _createServerClient():
    return xmlrpclib.ServerProxy(DATA_SERVER_ADDRESS, allow_none=True, verbose=False)

def loadObjectFromServer(name, expected_type=None, create=False):
    """
    :param name: Der Objektname zur Identifikation des Objektes auf dem Server
    """
    client = _createServerClient() # TODO: speichern dieses objektes für bessere performance
    # todo: das hier ist alles haesslich, die ueberpruefung nach expectedDatatype sollte einfacher gehen
    try:
        serializedObject = client.loadObject(name, create)
        instanz = pickle.loads(serializedObject)

        if expected_type is None or isinstance(instanz, expected_type):
            return instanz
        else:
            # Falls der Datentyp nicht passt
            return expected_type()

    except socket.error as e:
        SchreibeFehler("Error loading %s:\n%s"%(name, e), 'Communicator@loadObjectFromServer', verbose=False)
        print ('DatenServer ' + DATA_SERVER_ADDRESS +' ist offline!')


def storeObjectToServer(name, instanz, overwrite=True):
    client = _createServerClient()
    try:
        serializedObject = pickle.dumps(instanz)
        client.storeObject(name, serializedObject, overwrite)
    except socket.error as e:
        SchreibeFehler(e, 'Datenserver ist offline@storeObjectToServer')
        print ('DatenServer ist offline!')


def saveSensor(sensor):
    """Ermittelt den abgespeicherten Sensor per namen und ueberschreibt ihn bei aenderung des Inhaltes"""
    # Serverzugriff:
    if sensor.getName() is None or sensor.getName() is str(None):
        # storeObjectToServer(name=sensor.getName(), instanz=sensor, overwrite=False)
        print("Warnung: Sensor with id " + sensor.getID() + " hat keinen Namen und wird nicht auf dem Server gespeichert")
    else:
        storeObjectToServer(name=sensor.getName(), instanz=sensor, overwrite=True)

def saveSensorList(sensorList, overwrite=False):
    """Speichert eine komplette Sensorliste auf dem Server"""
    # Serverzugriff:
    for sensor in sensorList:
        storeObjectToServer(name=sensor.getName(), instanz=sensor, overwrite=overwrite)

def getSensorList():
    """Gibt die aktuelle SensorList zurueck. None fuer alle Dateien"""
    sensorliste = loadObjectFromServer(SERVER_OBJEKT_SENSORLISTE, expected_type=SensorListe.SensorListe, create=True)
    return sensorliste

def getSensorNameList():
    """ Gibt Namenliste der zur Auswahl stehenden Sensornamen zurueck"""
    sensorListe = fileReader(dateiName=DATEINAME_SENSORNAMEN, createIfNotExisting=False)
    CleanSensorList = SourceClean(sensorListe)
    CleanSensorList.sort()
    return CleanSensorList

def PickleReader(dateiname, dateipfad=EMPTY_STRING, createFile=True, datentyp=None):
    """Liest serialisierte Datei aus dateipfad/dateiname und gibt diese zurueck """
    for _ in range(LESEVERSUCHE):
        try:
            with open(dateipfad + dateiname, "rb") as Source:
                if FLOCK_ENABLED:
                    fcntl.flock (Source.fileno(), fcntl.LOCK_SH)
                Datei = pickle.load(Source)
            return Datei
        except EOFError:		#falls Source leer
            return None
        except IOError:		    #falls Source nicht vorhanden ist
            time.sleep(RETRY_SLEEP_TIME)
            continue
    # Falls alle Leseversuche fehlgeschlagen sind
    if createFile:
        FileCreator(dateiname, dateipfad = dateipfad)
    return datentyp

def PickleWriter(daten, dateiname, ordner=EMPTY_STRING):
    """ Schreibt DatenMap serialisiert in Dateiname in PFAD_DATEN """
    for _ in range(SCHREIBVERSUCHE):
        try:
            daten = pickle.dumps(daten)
            fileSaver(daten,dateiname=dateiname,ordner=ordner)
            return
        except IOError: #falls Datei nicht forhanden
            time.sleep(RETRY_SLEEP_TIME)
            continue
    #Falls alle Schreibversuche Fehlgeschlagen sind
    FileCreator(dateiname=dateiname,dateipfad=ordner)


def _openLockAndRead(dateiname, ordnerPfad=EMPTY_STRING):
    with open (os.path.join(ordnerPfad, dateiname),"r") as Datei:
        if FLOCK_ENABLED:
            fcntl.flock (Datei.fileno(), fcntl.LOCK_SH)
        Inhalt = Datei.readlines()
    return Inhalt

def fileSaver(daten, dateiname, ordner=PFAD_HAUPTPROGRAMM):
    with open(os.path.join(ordner, dateiname), "rb+") as Datei:
        if FLOCK_ENABLED:
            fcntl.flock (Datei.fileno(), fcntl.LOCK_EX) #Datei wird gesperrt
        Datei.truncate (0)
        Datei.write (daten)
    print ('saved Data at {dateipfad}'.format(dateipfad=os.path.join(ordner,dateiname)))
    return

def fileReader(dateiName, ordner=PFAD_HAUPTPROGRAMM, createIfNotExisting=False, errorMsg=True):
    """Oeffnet Datei"""
    for attempt in range(LESEVERSUCHE):
        try:
            return _openLockAndRead(dateiName, ordnerPfad=ordner)
        except IOError:
            time.sleep(RETRY_SLEEP_TIME)
    if createIfNotExisting:
        FileCreator(dateiName,dateipfad=ordner)
    else:
        if errorMsg:
            SchreibeFehler(os.path.join(ordner, dateiName) + ' existiert nicht', 'fileReader')
        raise IOError
    return []

def FileCreator(dateiname, dateipfad=PFAD_HAUPTPROGRAMM):
    """ Erzeugt Datei mit Dateiname in PFAD_DATEN"""
    print('Erstelle Datei "%s%s"' %(dateipfad, dateiname))
    path = os.path.join(dateipfad, dateiname)
    if not os.path.exists(dateipfad) and dateipfad != EMPTY_STRING:
        os.mkdir(dateipfad)
    with  open(path, "w+") as _:
        pass

def LineClean(Line, KommentarzeichenString = PARAMETER_KOMMENTAR_ZEICHEN):
    """ Saeubert die eingelesenen Zeilen von diversen Unreinheiten und Kommentaren """
    Line = Line.replace("\n",EMPTY_STRING)
    Line = Line.replace("\r",EMPTY_STRING)
    Line = Line.replace("\t",EMPTY_STRING)
    Line = Line.replace(" ",EMPTY_STRING)
    Line = Line.replace(",",".")
    for Kommentarzeichen in KommentarzeichenString:
        try:
            Line = Line.split(Kommentarzeichen)[0]
        except ValueError:
            pass
    return Line

def SourceClean(Source):
    """ Saeubert die eingelesene ZeilenListe """
    CleanSource = []
    for Line in Source:
        Line = LineClean(Line)
        if Line != EMPTY_STRING:
            CleanSource.append(Line)
    return CleanSource

def GetSensorTemperatur(sensorname):
    client = _createServerClient()
    try:
        return client.getSensorTemperatur(sensorname)
    except socket.error:
        print ('DatenServer ist offline!')

    sensorList = getSensorList()
    sensor = sensorList.getSensor(name=sensorname)
    return sensor.getTemperatur()

def SourceToDictionary(Source, Datentyp = None, TrennzeichenString = PARAMETER_SPLIT_ZEICHEN_PARAMETER):
    """ Liest Daten ein und konvertiert diese in Dictionarys """
    Dictionary= {}
    try:
        Source = SourceClean(Source)
        for Line in Source:
            try:
                Wert = Name = None
                for Trennzeichen in TrennzeichenString:
                    try:
                        Name,Wert = Line.split(Trennzeichen)[0:2]
                        break       # Falls Trennzeichen gefunden: abbrechen
                    except ValueError:
                        continue    # Falls Trennzeichen nicht vorhanden: naechstes Trennzeichen
                if not Wert or str(Wert) == EMPTY_STRING:     # Falls hinter dem Trennzeichen kein Wert steht
                    continue
                elif Datentyp == DATENTYP_FLOAT:    # Falls Daten als Float einzulesen sind
                    try:
                        Dictionary[Name] = float(Wert) #Versuche Wert als Float zu interpretieren
                    except ValueError:				#Falls Wert kein Float ist
                        Dictionary[Name] = Wert 		#Wert als String einfuegen
                elif Datentyp == DATENTYP_INT:      # Falls Daten als int einzulesen sind
                    try:
                        Dictionary[Wert] = int(Name) 	#Versuche PinNR als int zu interpretieren
                    except ValueError as e:				#Falls Name kein int ist
                        print (e)
                else:                       # Falls kein Datentyp dabeisteht oder dieser unbekannt ist
                    Dictionary[Name] = Wert
            except Exception as e:
                SchreibeFehler(e, " --- In SourceToDictionary() ausgeloest mit Datentyp = " + str(Datentyp))
    except Exception as e:
        SchreibeFehler(e, " --- In SourceToDictionary() ausgeloest mit Datentyp = " + str(Datentyp))
    return Dictionary


def GetGPIO(machine_name=MACHINE_NAME):
    """ 
    Liest die GPIO-Pinbelegungen in eine TupleListe (master, gpioliste)  ein 
    :param machine: None gibt die gpio listen aller machines zurück
    """
    gpio_dir = ORDNER_GPIO_ZUWEISUNG

    machines = [] # a list of all available GPIO machine names
    if machine_name is None:
        # Alle GPIO dateien laden
        
        # Hierzu alle verfügbaren machine names aus den GPIO dateien lesen
        for gpioDateiname in [datei for datei in os.listdir(gpio_dir) if DATEINAME_GPIO_PREFIX in datei]:
            m_name = gpioDateiname
            m_name = m_name.replace(DATEINAME_GPIO_PREFIX,'') # remove prefix
            m_name = m_name[:m_name.find('.')] # remove postfix
            machines.append(m_name)
    else:
        # Nur passende GPIO datei laden
        machines.append(machine_name)

    result = []
    for m in machines:
        dateiname = os.path.join(DATEINAME_GPIO_PREFIX + m + DATEINAME_GPIO_POSTFIX)

        gpioDictionary = {}
        try:
            GPIOSource = fileReader(dateiname, ordner=gpio_dir, createIfNotExisting=False)
            gpioDictionary = SourceToDictionary(GPIOSource,Datentyp=DATENTYP_INT, TrennzeichenString=PARAMETER_SPLIT_ZEICHEN_GPIO)
            result_tuple = (m, gpioDictionary)
            result.append(result_tuple)

        except ValueError as e:
            SchreibeFehler( "Fehler: " + str(e), 'in GetGPIO mit Parametern:' + gpio_dir + dateiname + ". HINWEIS: PinNr. zu int konvertierbar?")

    if machine_name is None: 
        return result
    else:
        # in diesem fall erwarten wir nur die GPIO liste
        # Schande ueber mein haupt
        return result[0][1]


def GetParameter(parameter=None, ersatzparameter=None):
    """ Liest Parameter aus Textdatei ein !!!TEXTFORMATIERUNG BEACHTEN!!!"""
    try:
        ParameterSource = fileReader(DATEINAME_PARAMETERDATEI, ordner=ORDNER_PARAMETER,createIfNotExisting=False)
        Parameter = SourceToDictionary(ParameterSource,Datentyp=DATENTYP_FLOAT, TrennzeichenString=PARAMETER_SPLIT_ZEICHEN_PARAMETER)
    except Exception as e:
        SchreibeFehler(e,"In GetParameter ausgeloest")
        Parameter = {}
    if parameter is None:
        return Parameter
    else:
        try:
            return Parameter[parameter]
        except KeyError:
            # Falls der parameter im Dictionary nicht gefunden wird, versuche ersatzparameter zu uebergeben
            if ersatzparameter is not None:
                SchreibeFehler('%s Ersatzparameter uebernommen' %parameter, 'GetParameter')
                return ersatzparameter
            else:
                raise KeyError

def getSlaveList():
    slaveList = []
    w1_master_slaves = fileReader(dateiName=SLAVE_LIST_DATEINAME, ordner=PATH_SLAVE_LIST, createIfNotExisting=False)  # liest SensorePfade ein
    for line in w1_master_slaves:
        line = LineClean(line)
        if line == KEINE_SENSOREN_GEFUNDEN: #Leerzeichen wird von LineClean() entfernt
            print("Keine Sensoren gefunden!")
        else:
            slaveList.append(line)
    return slaveList

def CleanStringForConsole(String = EMPTY_STRING):
    String = str(String)
    #String = String.replace("(","\(")
    #String = String.replace(")","\)")
    #String = String.replace("\"","\\\"")
    return String

def SchreibeFehler(exception, Programmteil = "Unbekannter Programmteil", dateiname = DATEINAME_ERROR_LOG, dateipfad = PFAD_HAUPTPROGRAMM, verbose=True):
    """Protokolliert auftretende Fehler"""
    # todo: Fehler die bereits drin sind nicht nochmal eintragen
    #EXCEPTION
    #LAMPE ANSCHALTEN
    #WarnDatei einlesen und zusaetzliche Fehler anhaengen
    Info = "Fehler in " + Programmteil + " auf " + MACHINE_NAME
    datum = str(time.strftime("%d.%m.%Y %H:%M:%S"))

    # Versuche Traceback miteinfließen zu lassen
    tracebackInformation = traceback.format_exc()
    exception = CleanStringForConsole(exception)

    Warnungen = ["------------- Datum: {datum} ------------- \n{info} \nException: {exception} \nTracebackInformation: {traceback}\n".format(datum=datum, info=Info,exception=exception, traceback= tracebackInformation) ]
    if verbose:
      print (Warnungen[0])
      
    try:
        with open (os.path.join(dateipfad,dateiname),"r") as WarnDatei:
            if FLOCK_ENABLED:
                fcntl.flock (WarnDatei, fcntl.LOCK_SH) #Datei wird gesperrt
            AlteErrors = WarnDatei.readlines()
            maxLines = GetParameter(PARAMETER_ZEILENANZAHL_FEHLERDATEI, ERSATZPARAMETER_ZEILENANZAHL_FEHLERDATEI)
            if len(AlteErrors) > maxLines and maxLines is not None:
                AlteErrors = AlteErrors [0: int(maxLines)]
            for line in AlteErrors:
                Warnungen.append(line)
        with open (os.path.join(dateipfad,dateiname),"r+") as WarnDatei:
            if FLOCK_ENABLED:
                fcntl.flock (WarnDatei, fcntl.LOCK_EX) #Datei wird gesperrt
            WarnDatei.truncate (0)
            WarnDatei.writelines(Warnungen)
            WarnDatei.close()
    except IOError: #falls Datei nicht forhanden
        FileCreator(dateiname=dateiname, dateipfad=dateipfad)
        with open (os.path.join(dateipfad,dateiname),"r+") as WarnDatei:
            if FLOCK_ENABLED:
                fcntl.flock (WarnDatei, fcntl.LOCK_EX) #Datei wird gesperrt
            WarnDatei.truncate (0)
            WarnDatei.writelines(Warnungen)
            WarnDatei.close()

def Log(Daten, MaxZeilen=0):
    """Loggt alle Daten"""
    Inhalt = fileReader(dateiName=DATEINAME_LOG, ordner=ORDNER_LOGS, createIfNotExisting=True)
    Inhalt = [EMPTY_STRING]*len(Daten) + Inhalt
    for i in range(len(Daten)):
        Inhalt[i] = Daten[i]
    Inhalt = [time.strftime("%d.%m.%Y --- %H:%M:%S ---\n")] + Inhalt
    if len(Inhalt) > MaxZeilen != 0:
        Inhalt = Inhalt[0:int(MaxZeilen)]
    with open (os.path.join(ORDNER_LOGS + DATEINAME_LOG),"r+") as LogBuch:
        if FLOCK_ENABLED:
            fcntl.flock (LogBuch, fcntl.LOCK_EX)
        for line in Inhalt:
            LogBuch.write ( str(line))
    print ("Logging abgeschlossen\n")

def hmTimeValidate(gettime):
    """Kontrolliert und Konvertiert ein eingegebenes Zeitformat"""
    #todo in hmTimeValidate hier ist noch ein fehler drin
    try:
        h,m = gettime.split(":")
        h = int(h)
        m = int(m)
        if m > 60:
            m -= 60
            h += 1
        elif m<0:
            m=0
        if h > 24:
            h -= 24
        elif h < 0:
            h = 0
        gettime = datetime.time(hour=h,minute=m)
        return gettime
    except ValueError:
        # todo: hmTimeValidate anfaellig fuer fehler
        h = int(gettime)
        gettime = datetime.time(hour=h)
        return gettime


def GetTageszeit (TagBeginn,TagEnde):
    """Schaut ob es Tag (True) oder Nacht (False) ist"""
    TagBeginn = hmTimeValidate(str(TagBeginn))
    TagEnde = hmTimeValidate(str(TagEnde))
    Tag = True
    TagesZeit = datetime.time(hour=int(time.strftime("%H")),minute=int(time.strftime("%M")))
    try:
        if TagBeginn > TagEnde: #Falls Tagessprung zwischen beginn und ende
            if TagesZeit > TagBeginn or TagesZeit < TagEnde: #Falls nach Tagesstart oder vor Tagesende
                Tag = True
            else:
                Tag = False
        elif TagBeginn < TagEnde:
            if TagBeginn < TagesZeit < TagEnde:
                Tag = True
            else:
                Tag = False
        else:
            print ("in Parameterliste: %s = %s!! " %(PARAMETER_TAG_BEGINN, PARAMETER_TAG_ENDE) )
            Tag = True
    except KeyboardInterrupt:
        pass
    except ValueError as e:
        SchreibeFehler(e, " in TagesZeit")
    return Tag

def SchreibeBefehl(GPIO_Name, value):
    """Schreibt GPIO-Befehle an den Server, von dort aus lesen die anderen Raspberry die Befehle"""
    Befehlsliste = loadObjectFromServer(DATEINAME_SCHALTBEFEHLE, expected_type=dict, create=True) # Serverzugriff
    Befehlsliste[GPIO_Name] = value     # neuen GPIO-Wert zuweisen
    print ('Befehlsliste gesendet: {befehle}'.format(befehle=str(Befehlsliste)))
    storeObjectToServer(DATEINAME_SCHALTBEFEHLE, instanz=Befehlsliste, overwrite=True)

def GetBefehle():
    """Liest die auf dem Server abgelegten GPIO-Befehle"""
    try:
        Befehlsliste = loadObjectFromServer(DATEINAME_SCHALTBEFEHLE, expected_type=dict, create=True)  # Serverzugriff
    except Exception as e:
        SchreibeFehler(e,Programmteil='GetBefehle')
        Befehlsliste = {}
    print ('Befehlsliste geladen: {befehle}'.format(befehle=str(Befehlsliste)))
    return Befehlsliste