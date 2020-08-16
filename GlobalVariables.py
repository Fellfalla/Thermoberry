"""
Hier sind alle Parameter und "Magic Numbers" des gesamten Programmes aufgelistet.
Alle Programmteile greifen auf diese Bibliothek zu.

Im Programm selber sollten daher keine scheinbar willkuerlichen Zahlen mehr vorkommen
"""
import socket
import os
import ConfigParser as configparser
"""
_______________________________________________________________________________________
!!! Diese werte sollten nicht veraendert werden, da diese nicht vom Programm bestimmt wurden !!!
======> NICHT HIER MURXEN <======
"""

SETINGS_FILE_PATH = "settings.ini"
SENSOR_MAPPING_FILE_PATH = "sensor_mapping.ini"

# Laden der Konfigurationsdatei
config_parser = configparser.ConfigParser()
config_parser.read(SETINGS_FILE_PATH)

# Lesen der config datei
MACHINE_NAME = config_parser.get('DEFAULT','MACHINE_NAME','unknown_machine')
DATENSERVER_NAME = config_parser.get('DEFAULT','DATA_SERVER_ADDRESS')
PORT_DATENSERVER = 7070
PFAD_HAUPTPROGRAMM = config_parser.get('DEFAULT','PATH_TO_SOFTWARE', os.path.dirname(os.path.abspath(__file__)))


# Datenbankzeug
DATABASE = 'heizung'        #Name der Datenbank fuer das logging der Heizungsdaten
TABLENAME_TEMPERATUREN = 'Temperaturen' # Tabellenname fuer das Temperaturlogging
COLUMN_TIMESTAMP = 'timestamp'  # SQL-Befehl fuer den Datentyp timestamp
HOST = 'raspi1'       # IP-Adresse des Datenbankservers bzw. von raspi1
USER = 'pi'     # Benutzername zum Einloggen in die Datenbank
USER_PW = 'raspberry'   # Passwort zu o.g. Benutzernamen

# Hostnames
RASPBERRY1_NAME = 'raspi1'
RASPBERRY2_NAME = 'raspi2'

PORT_WEBSERVER = 62001


SENSOR_DEVICES_LOCATION = "/sys/bus/w1/devices/"
PATH_SLAVE_LIST = "/sys/bus/w1/devices/w1_bus_master1/"

# Dateinamen
SLAVE_LIST_DATEINAME = "w1_master_slaves"
DATEINAME_MESSDATEN = "w1_slave"

# Sonstiges
EMPTY_STRING = ''
KEINE_SENSOREN_GEFUNDEN = "notfound."
TRENNZEICHEN_SENSOR_ZUWEISUNG = '='


"""
_______________________________________________________________________________________
!!! Falls hier Werte geaendert werden, muessen die Dateinamen auch geaendert werden !!!
"""
DATEINAME_PARAMETERDATEI = 'Parameter.txt'
DATEINAME_SENSORNAMEN = 'sensor_names.txt'
DATEINAME_ERROR_LOG = 'ErrorLog.txt'
DATEINAME_LOG = 'Log.txt'
DATEINAME_SCHALTBEFEHLE = 'Befehlsliste'
DATEINAME_GPIO_PREFIX = 'GPIO_'
DATEINAME_GPIO_POSTFIX = '.txt'
DATEINAME_DATENMAP = 'Zustandsdaten'
DATEINAME_WEBSITE_HEIZUNG = 'heizung.html'
DATEINAME_SENSOR_ZUWEISUNG = 'idZuweisung.txt'

# Pfade
PFAD_DATEN = 'Daten/'
PFAD_SONSTIGES= 'Sonstiges/'
PFAD_KONFIGURATION = "Konfiguration/"
PFAD_WEBSITE = 'website/'

# Sortierung der Daten
ORDNER_SENSOR_ZUWEISUNG = os.path.join(PFAD_HAUPTPROGRAMM,PFAD_SONSTIGES)
ORDNER_GPIO_ZUWEISUNG = os.path.join(PFAD_HAUPTPROGRAMM,PFAD_KONFIGURATION)
ORDNER_PARAMETER = os.path.join(PFAD_HAUPTPROGRAMM,PFAD_KONFIGURATION)
ORDNER_SENSORNAMEN = os.path.join(PFAD_HAUPTPROGRAMM,PFAD_KONFIGURATION)
ORDNER_DATENMAP = os.path.join(PFAD_HAUPTPROGRAMM,PFAD_DATEN)
ORDNER_LOGS = os.path.join(PFAD_HAUPTPROGRAMM,PFAD_DATEN)
ORDNER_WEBSITE = os.path.join(PFAD_HAUPTPROGRAMM,PFAD_WEBSITE)

"""
_______________________________________________________________________________________
!!! Falls hier Werte geaendert werden, muessen die Werte der entsprechenden Liste auch geaendert werden !!!
"""
# Namensgebung fuer GPIOs
BEZEICHNUNG_KELLER = 'Keller'
BEZEICHNUNG_HEIZRAUM = 'Heizraum'
BEZEICHNUNG_HEIZUNGSPUMPE = 'HeizungsPumpe'
BEZEICHNUNG_WARNLAMPE = 'Warnlampe'
BEZEICHNUNG_MASTER_RASPI = 'raspi2'
PUFFERNAME_HYGIENE = 'Hygiene'
PUFFERNAME_HEIZUNG = 'Heizung'
PUFFERNAME_HEIZRAUM = BEZEICHNUNG_HEIZRAUM
BEZEICHNNG_ENTLADEPUMPE = 'Entladepumpe'
BEZEICHNUNG_BELADEPUMPE = 'Beladepumpe'
BEZEICHNUNG_SENSOR = 'Sensor'
BEZEICHNUNG_MISCHER = 'Mischer'
BEZEICHNUNG_PUFFER = 'Puffer'
BEZEICHNUNG_PUMPE = 'Pumpe'
BEZEICHNUNG_PUMPE_HEIZRAUM = BEZEICHNUNG_PUMPE + BEZEICHNUNG_HEIZRAUM
BEZEICHNUNG_PUMPE_KELLER = BEZEICHNUNG_PUMPE + BEZEICHNUNG_KELLER
BEZEICHNUNG_MISCHERSENSOR = BEZEICHNUNG_SENSOR + BEZEICHNUNG_MISCHER
BEZEICHNUNG_PUFFERSENSOR = BEZEICHNUNG_SENSOR + BEZEICHNUNG_PUFFER
BEZEICHNUNG_AUSSENTEMPERATUR = 'Aussentemperatur'
BEZEICHNUNG_AUSSENSENSOR = BEZEICHNUNG_SENSOR + BEZEICHNUNG_AUSSENTEMPERATUR
BEZEICHNUNG_SOLLTEMPERATUR = 'Soll'
BEZEICHNUNG_AUSGANG = 'Ausgang'
KAELTER_POSTFIX = 'Kaelter'
WAERMER_POSTFIX = 'Waermer'
POSTFIX_MAXIMAL = 'Max'
POSTFIX_MINIMAL = 'Min'

# Sensornamen
SENSORLISTE = ['SensorPufferHygiene1',
               'SensorPufferHygiene2',
               'SensorPufferHygiene3',
               'SensorPufferHygiene4',
               'SensorPufferHeizung1',
               'SensorPufferHeizung2',
               'SensorPufferHeizung3',
               'SensorPufferHeizung4',
               'SensorPufferHeizraum1',
               'SensorPufferHeizraum2',
               'SensorPufferHeizraum3',
               'SensorPufferHeizraum4',
               'SensorPufferHeizraum5',
               'SensorPufferHeizraum6',
               'SensorAussentemperatur',
               'SensorMischerKeller']


# Parameter
PARAMETER_SPLIT_ZEICHEN_GPIO = "=:"
PARAMETER_SPLIT_ZEICHEN_PARAMETER = "="
PARAMETER_KOMMENTAR_ZEICHEN = "#"
PARAMETER_NOTFALL_AUSSENTEMPERATUR = "AussentemperaturErsatz"
PARAMETER_NOTFALL_HEIZUNG_VORLAUF_SOLL = "HeizungVorlaufTemperaturSollNotfall"
PARAMETER_HEIZUNG_VORLAUF_STEIGUNG = "HeizungVorlaufSollSteigung"
PARAMETER_HEIZUNG_VORLAUF_ANHEBUNG = 'HeizungVorlaufParallelverschiebung'
PARAMETER_TEMPERATUR_ZIMMER_TAG_SOLL = "TemperaturRaumSollTag"
PARAMETER_TEMPERATUR_ZIMMER_NACHT_SOLL = "TemperaturRaumSollNacht"
PARAMETER_PUFFER_TEMPERATUR_MAX = "MaxTemperatur"
PARAMETER_PUFFER_TEMPERATUR_MIN = "MinTemperatur"
PARAMETER_HEIZUNGSWASSER_TEMPERATUR_UEBER_RAUM_SOLL = "HeizungswasserUeberRaumSollMin"
PARAMETER_TAG_BEGINN = "TagBeginn"
PARAMETER_TAG_ENDE = "TagEnde"
PARAMETER_MISCHER_MODUS = "MischerModus"
PARAMETER_MISCHER_HYSTERESE = 'MischerHysterese'
PARAMETER_TEMPERATUR_ZEIT_KOEFFIZIENT = "TempZeitKoeff"
PARAMETER_MISCHER_TENDENZGEWICHTUNG = 'Tendenzgewichtung'
PARAMETER_MISCHER_ZYKLENZEIT = "Zyklenzeit"
PARAMETER_DELTA_TEMPERATUR_INNEN_AUSSEN_MIN = 'DeltaTMinInnenAussen'
PARAMETER_LOGGING_PUFFER = 'Pufferlogging'
PARAMETER_FEHLER_FALLS_PUFFER_VOLL = 'FehlerPufferVoll'
PARAMETER_MINDESTVOLUMEN_PUMPEN = 'MindestPumpVolumen'
PARAMETER_HEIZBETRIEB_MINIMALTEMPERATUR = "MinimalTemperaturHeizbetrieb"
PARAMETER_ZEILENANZAHL_FEHLERDATEI = 'ZeilenanzahlFehlerDatei'
PARAMETER_TEMPERATUR_PUMPVERLUSTE = 'Pumpverluste'
"""
_______________________________________________________________________________________
!!! Folgende Werte koennen geaendert werden, haben allerdings auswirkungen auf das Programm und die Nachrichten
"""
# Ersatzparameter
ERSATZPARAMETER_NOTFALL_AUSSENTEMPERATUR = 0
ERSATZPARAMETER_HEIZUNG_VORLAUF_SOLL = 50
ERSATZPARAMETER_HEIZUNG_VORLAUF_BEGRENZUNG = 75
ERSATZPARAMETER_TEMPERATUR_ZIMMER_TAG_SOLL = 20
ERSATZPARAMETER_TEMPERATUR_ZIMMER_NACHT_SOLL = 17
ERSATZPARAMETER_ZYKLENZEIT_MISCHER = 30
ERSATZPARAMETER_TEMPERATUR_ZEIT_KOEFFIZIENT = 2.3
ERSATZPARAMETER_MISCHER_TENDENZGEWICHTUNG = 3.5
ERSATZPARAMETER_MISCHER_EINSCHALTZEIT_MIN = 0.05 # Anteil an Zyklenzeit
ERSATZPARAMETER_PUFFER_TEMPERATUR_MAX = 80
ERSATZPARAMETER_PUFFER_TEMPERATUR_MIN = 30
ERSATZPARAMETER_PUFFER_TEMPERATUR_SCHWELLWERT = 0.01 # Wert ab dem nicht mehr durch DeltaTAusgangSollIst geteilt wird
ERSATZPARAMETER_PUFFER_HEIZRAUM_SCHWELLE_VOLL = 0.95
ERSATZPARAMETER_PUFFER_HEIZRAUM_SCHWELLE_LEER = 0.0
ERSATZPARAMETER_PUFFER_HEIZUNG_SCHWELLE_VOLL = 0.95
ERSATZPARAMETER_PUFFER_HEIZUNG_SCHWELLE_LEER = 0.05
ERSATZPARAMETER_PUFFER_HYGIENE_SCHWELLE_VOLL = 1.0
ERSATZPARAMETER_PUFFER_HYGIENE_SCHWELLE_LEER = 0.05
ERSATZPARAMETER_MINDESTVOLUMEN_PUMPEN = 350
ERSATZPARAMETER_TEMPERATUR_PUMPVERLUSTE = 6 # in C
ERSATZPARAMETER_TEMPERATURDIFFERENZ_MIN_PUMPEN = 2
ERSATZPARAMETER_LOGGING_PUFFER = False
ERSATZPARAMETER_FEHLER_FALLS_PUFFER_VOLL = True
ERSATZPARAMETER_MISCHER_HYSTERESE = 0.5
ERSATZPARAMETER_HEIZUNG_VORLAUF_STEIGUNG = 4.0
ERSATZPARAMETER_HEIZBETRIEB_MINIMALTEMPERATUR = 30
ERSATZPARAMETER_HEIZUNG_VORLAUF_ANHEBUNG = 2    # TemperaturDelta um die der Vorlauf pauschal angehoben wird
ERSATZPARAMETER_DELTA_TEMPERATUR_INNEN_AUSSEN_MIN = 3
ERSATZPARAMETER_ZEILENANZAHL_FEHLERDATEI = 3000
ERSATZPARAMETER_HEIZUNGSWASSER_TEMPERATUR_UEBER_RAUM_SOLL = 3

# Physische Werte
VOLUMEN_RESERVE = 2200
VOLUMEN_HEIZUNG = 1000
VOLUMEN_HYGIENE = 800

# Timer
PUFFERSTEUERUNG_INTERVALL_BEFEHLE_LESEN = 10
PUFFERSTEUERUNG_INTERVALL_BEFEHLE_SCHREIBEN = 30  # Ausfuehren der hauptschleife alle * Sekunden
PUFFERSTEUERUNG_INTERVALL_DATALOGGING = 120
KONTROLL_INTERVALL = 30 # in Sekunden
KONTROLL_INTERVALL_FEHLER = 3600 * 5 #5 Stunden
TEMPERATURMESSUNG_PAUSE = 2
TIME_UNTIL_SENSOR_OFFLINE = 30
TIME_BETWEEN_LOGS = 60 # [s] Zeitintervall zwischen den Logging-Prozeduren
TIME_SERVER_KONSOLENAUSGABE = 25 # in sekunden
TIME_SERVER_WEBSITE_REFRESH = 5
INTERVALL_DATENMAP_SPEICHERN = 200 # [s]
TIME_UNTIL_RESTART = 10 # Zeit nach Programmabsturz die gewartet wird, um einzelne Module wieder zu starten -> verhindert Ueberschwemmung mit Fehlern

# Optik
SENSOR_TRANSMIT_ERROR = "TRANSMIT ERROR"  # Variableninhalt bei Uebertragungsfehler
SENSOR_OFFLINE = "SENSOR OFFLINE"  # String der in die Variable geschrieben wird, wenn der Sensor entfernt wurde
ROUNDED_TEMPERATURE_DIGITS = 1  # Anzahl der Nachkommastellen, auf die die Temperatur gerundet wird
ROUNDED_PERCENTAGE_DIGITS = 4
UNBEKANNTER_PUFFER_LADEZUSTAND = 'Unbekannter Ladezustand'
COMPLETE_RESET_MSG = '\n\n!!!COMPLETE RESET!!!\n\n'
STATUS_PUFFER_LEERT_UND_LAEDT = 'laedt und entlaedt'
STATUS_PUFFER_LAEDT = 'laedt'
STATUS_PUFFER_LEERT = 'entlaedt'
STATUS_PUFFER_VOLL = 'ist voll'    #Status des Puffers zum kontrollieren des Ladezustandes
STATUS_PUFFER_NEUTRAL = 'macht garnichts'
STATUS_PUFFER_LEER = 'ist leer'
STATUS_MISCHER_IDLE = 'Wartet'
STATUS_MISCHER_WAERMER = 'Oeffnet'
STATUS_MISCHER_KAELTER = 'Schliesst'
STATUS_MISCHER_ZULAUF_ZU_KALT = 'Versorgungspuffer zu kalt'

STATUS_KEINE_FEHLER = 'Alles im Butter!'

# Unsichtbare Werte
SCHREIBVERSUCHE = 10
LESEVERSUCHE = 4
RETRY_SLEEP_TIME = 2
SENSOR_MEMORYSIZE = 2   # legt fest welche Anzahl an alten Temperaturen in der Sensorkalsse gespeichert werden

# Eingabeoptionen - Programmkommunikation

# Serverwerte
SERVER_OBJEKT_SENSORLISTE = 'sensorliste'

"""
_______________________________________________________________________________________
!!! Folgende Werte duerften nach Belieben geaendert werden, jedoch wuerde dies keinen Einfluss auf das
Programm oder irgendetwas anderes haben, als das war hier steht, und macht somit keinen Sinn !!!
"""
# im Prinzip voellig willkuerliche Werte:

DATENTYP_INT = 'int'
DATENTYP_FLOAT = 'float'

