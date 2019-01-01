#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Markus Weber'
from GlobalVariables import *
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from SocketServer import ThreadingMixIn
from Klassen import Communicator, Sensor, SensorListe, Puffer
from threading import Thread, Lock
import BaseHTTPServer
import SimpleHTTPServer
import pickle
import sys
import time
import os
import copy
import select
import errno
try:
    import threading
except ImportError:
    import dummy_threading as threading
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
lck = Lock()

class ServerThread(Thread):
    """Allgemeine Threadklasse um Server und Services auszufuehren"""
    def __init__(self, Server, name='serverthread'):
        Thread.__init__(self,name=name)
        self.server = Server

    def run(self):
        try:
            self.server.serve_forever()
        except Exception as e:
            Communicator.SchreibeFehler(e.message + '-->' + self.name + ' wurde liquidiert','in serve_forever@' + self.name)
            print (self.name + ' wurde liquidiert')


class Service(object):
    def __init__(self, DatenMap, Datenserver):
        self.Datenserver = Datenserver
        self.DatenMap = DatenMap
        self.lastLog = 0
        self.maximaleShutdownzeit=0.15 #in sekunden
        self.__stop = False

        self.serve_forever = PrintAtExit(self.serve_forever, classname=self.__class__.__name__)
        self.shutdown = PrintAtServerShutdown(self.shutdown, classname=self.__class__.__name__)

    def shutdown(self):
        self.__stop = True

    def serve_forever(self):
        time.sleep(1)
        while not self.__stop:
            try:
                # 1. Datenzeug ausgeben
                self.printDatenMap()

                # 2. Datenzeug bei zeiten loggen loggen
                self.logging(intervall=INTERVALL_DATENMAP_SPEICHERN)

                # 3. Kontrollieren ob neue Sensoren vorhanden sind
                self.searchForNewSensors()

                # 4. Pause machen
                self.sleep()
            except Exception as e:
                Communicator.SchreibeFehler(e.message,'in serve_forever@' + self.__class__.__name__)

    def printDatenMap(self):
        print ('\nData-Informations:')
        lck.acquire() # wird vor allem fuer 2getsizeof" benoetigt
        print ('Size of stored Data: %i Bytes ' %sys.getsizeof(self.DatenMap))
        if self.DatenMap:
            for key in self.DatenMap:
                #print ('{name:25s}: {values}'.format(name=key, values=pickle.loads(self.DatenMap[key])))
                if key == SERVER_OBJEKT_SENSORLISTE:
                    print (SERVER_OBJEKT_SENSORLISTE + ':')
                print (self.DatenMap[key])
        lck.release()
        print ('end of information-block\n')

    def sleep(self):
        """Sleepfunktion, welche in mehrere sleepabschnitte unterteilt ist, damit ein Keyboard interrupt schnell greifen kann"""
        print('Service sleeps now for {time} seconds'.format(time=TIME_SERVER_KONSOLENAUSGABE))
        print('_'*100)
        for i in range(int(TIME_SERVER_KONSOLENAUSGABE/self.maximaleShutdownzeit)): # Wartezeit wird mit __stopabfragen unterteilt
            if not self.__stop:
                time.sleep(self.maximaleShutdownzeit)
            else:   # Falls der __stop-Flag innerhalb der wartezeit gesetzt wurde
                break

    def logging(self, intervall):
        """logging der Serverdaten"""
        # Intervallabfrage zum abspeichern der DatenMap
        if time.time() - self.lastLog > intervall:
            self.lastLog = time.time()
            self.logDatenMap()

    def logSensorZuweisung(self):
        dateiname = DATEINAME_SENSOR_ZUWEISUNG
        dateiordner = ORDNER_SENSOR_ZUWEISUNG

        zuweisungsListe = Communicator.fileReader(dateiName=dateiname, ordner=dateiordner)
        sensorListe = Communicator.loadObjectFromServer(name=SERVER_OBJEKT_SENSORLISTE, expectedDatatype=SensorListe.SensorListe, create=True)

        # Jeden vorhandenen Sensor ggf. in die Liste aufnehmen, die Sensoren, die bereits in der Liste sind, koennen da bleiben
        flagSensorVorhanden = None # Flag wird benoetigt, damit nicht gespeichert wird, falls sich garnichts veraendert hat
        for sensor in sensorListe:
            if sensor.getName() is not None and sensor.getName() is not str(None):
                flagSensorVorhanden = False # initialisierung

                # Parsen der vorhandenen Datei nach der SensorId und ggf. ueberschreiben
                for lineNumber in range(len(zuweisungsListe)):
                    if sensor.getID() in zuweisungsListe[lineNumber]:    # Falls die SensorID bereits vorhanden ist, soll sie umgeschrieben werden
                        zuweisungsListe[lineNumber] = sensor.getName() + TRENNZEICHEN_SENSOR_ZUWEISUNG + sensor.getID()
                        flagSensorVorhanden=True
                        break   # herausspringen, damit der rest nicht ueberprueft werden muss

                # Falls der Sensor noch nicht in der Liste ist: Sensor hinzufuegen
                if not flagSensorVorhanden: # Falls der sensor in der obrigen Schleife noc nicht gefunden wurde
                    zuweisungsListe.append(sensor.getName() + TRENNZEICHEN_SENSOR_ZUWEISUNG + sensor.getID())
                    flagSensorVorhanden=True

        # Abspeichern der neuen zuweisungsliste
        if flagSensorVorhanden is True: # True wird nur dann gesetzt, falls sich etwas geaendert hat
            Communicator.fileSaver(zuweisungsListe,dateiname=dateiname,ordner=dateiordner)


    def logDatenMap(self):
        """abspeichern der DatenMap"""
        # todo: entferne diese funktion, falls sie nicht gebraucht wird
        Communicator.PickleWriter(daten=self.DatenMap, dateiname=DATEINAME_DATENMAP, ordner=ORDNER_DATENMAP)

    def searchForNewSensors(self):
        print ('\nSearching for new Sensors...')
        try:
            for sensor in self.DatenMap[SERVER_OBJEKT_SENSORLISTE]:
                if sensor.getName() == str(None):
                    sensor.setName(newname=None)
            for sensor in self.DatenMap[SERVER_OBJEKT_SENSORLISTE]:
                if sensor.getName() is None or sensor.getName() is str(None):
                    print ('Neuer Sensoren gefunden:' + str(sensor))
                    newSensorName = self.getNewSensorName(sensor=sensor)
                    print('Sensor {sensorname} wurde hinzugefuegt!\n'.format(sensorname=newSensorName))
                    lck.acquire()
                    sensor.setName(newname=newSensorName)
                    lck.release()
            #self.logSensorZuweisung()
            print ('search finished\n')
        except TypeError as e:
            if self.DatenMap[SERVER_OBJEKT_SENSORLISTE] is None:
                print ('Noch keine Sensorliste vorhanden')
            else:
                Communicator.SchreibeFehler(e.message, 'in searchForNewSensors@Datenserver')
        except KeyError:
                print ('{sensorliste} in Datenmap noch nicht vorhanden'.format(sensorliste=SERVER_OBJEKT_SENSORLISTE))


    def getNewSensorName(self, sensor):
        """Die Methode fuer einen neuen Sensor muss auf dem server sein, da man hier den Ueberblick ueber alle aktuellen
        informationen haben sollte"""
        #Erstmal schauen ob der Sensor in der idZuweisungsdatei gelistet ist:
        try:
            zuweisungsListe = Communicator.fileReader(dateiName=DATEINAME_SENSOR_ZUWEISUNG,ordner=ORDNER_SENSOR_ZUWEISUNG,createIfNotExisting=True)
            for line in zuweisungsListe:
                if sensor.getID() in line:
                    line = line.replace(sensor.getID(),'')
                    line = line.replace(' ','')
                    line = line.replace(TRENNZEICHEN_SENSOR_ZUWEISUNG,'')
                    line = line.replace('\t','')
                    line = line.replace('\n','')
                    line = line.replace('\r','')
                    return line
        except IOError:
            print ('Keine Zuweisungsdatei vorhanden')

        # Manuell den Sensor mithilfe der gegebenen Namensliste uaswaehlen
        ID={}
        for sensorname in SENSORLISTE:
            ID[str(SENSORLISTE.index(sensorname))]= sensorname

        for key in sorted(ID):
            print('{key:5s}: {name}'.format(key=str(key), name=ID[key]))
        eingbabe = None

        while eingbabe not in ID:
            eingbabe = raw_input('Auswahl:')
        return ID[eingbabe]


class WebServer(BaseHTTPServer.HTTPServer):
    """Server um per HTTP Daten der Heizung ansehen zu koennen"""
    def __init__(self,*args, **kwargs ):
        if 'DatenMap' in kwargs:
            self.DatenMap = kwargs['DatenMap']
            del kwargs['DatenMap']
        BaseHTTPServer.HTTPServer.__init__(self,*args, **kwargs)
        self.sensorList = SensorListe.SensorListe()
        self.valuesToShow = dict()

        self.serve_forever = PrintAtExit(self.serve_forever, classname=self.__class__.__name__)
        self.shutdown = PrintAtServerShutdown(self.shutdown, classname=self.__class__.__name__)

class DatenServer(object, ThreadingMixIn, SimpleXMLRPCServer):
    """Programmkern zum speichern und verteilen der Daten"""
    def __init__(self,*args,**kwargs):
        object.__init__(self)
        SimpleXMLRPCServer.__init__(self,*args,**kwargs)
        self.__is_shut_down = threading.Event()
        self.__shutdown_request = False
        self.DatenMap = Communicator.PickleReader(dateiname=DATEINAME_DATENMAP, dateipfad=ORDNER_DATENMAP, createFile=False, datentyp=dict())
        # self.DatenMap = None
        if self.DatenMap is None or not isinstance(self.DatenMap, dict):
            self.DatenMap = {}
        self.allow_reuse_address = True
        self.register_introspection_functions()
        self.register_function(self.storeObject)
        self.register_function(self.loadObject)
        self.register_function(self.getSensorTemperatur)

        self.serve_forever = PrintAtExit(self.serve_forever, classname=self.__class__.__name__)
        self.shutdown = PrintAtServerShutdown(self.shutdown, classname=self.__class__.__name__)

        self.client_address = None
        self.client_request = None

    def storeObject(self, name, serialisierteInstanz, overwrite):
        try:
            instanz = pickle.loads(serialisierteInstanz) # Damit keine ungepickelten Daten durchkommen
        except Exception as e:
            Message = '{error}: {instanz} war nicht serialisiert'.format(error=e.message, instanz=str(serialisierteInstanz))
            print(Message)
            return Message

        try:
            lck.acquire()
            if instanz.__class__.__name__ == Sensor.Sensor.__name__:
                self._storeSensor(sensor=instanz, overwrite=overwrite)
                return
            # Falls ueberschrieben werden darf
            if overwrite:
                self.DatenMap[name] = instanz
            # Falls das objekt noch nicht vorhanden ist und nicht ueberschrieben werden darf
            elif name not in self.DatenMap:
                self.DatenMap[name] = instanz
            # Falls das objekt vorhanden ist, aber nicht ueberschrieben werden darf
            else:
                print(str(name) + ' hat Schreibschutz in der Datenmap.')
        finally:
            lck.release()

    def _storeSensor(self, sensor, overwrite=True):
        if sensor.master is None: # Sensor nicht abspeichern wenn kein Master vorhanden ist
            print(sensor.getName() + ' hat keinen Master!')
            return
        else:
            try:
                if overwrite:
                    self.DatenMap[SERVER_OBJEKT_SENSORLISTE].append(sensor)
                else:
                    if sensor.getID() not in self.DatenMap[SERVER_OBJEKT_SENSORLISTE]:
                        self.DatenMap[SERVER_OBJEKT_SENSORLISTE].append(sensor)
            except KeyError:    # Sensorliste nicht vorhanden
                self.DatenMap[SERVER_OBJEKT_SENSORLISTE] = SensorListe.SensorListe()
                self.DatenMap[SERVER_OBJEKT_SENSORLISTE].append(sensor)
            except (TypeError, AttributeError):   # Datenmap ist None oder ein anderes Problem
                self.DatenMap[SERVER_OBJEKT_SENSORLISTE] = SensorListe.SensorListe()
                self.DatenMap[SERVER_OBJEKT_SENSORLISTE].append(sensor)

    def process_request(self, request, client_address):
        self.client_address = client_address
        self.client_request = request
        return SimpleXMLRPCServer.process_request(
            self, request, client_address)

    def loadObject(self,name, create=False):
        try:
            #if name in self.DatenMap:
            return pickle.dumps(self.DatenMap[name])
            #else:
            #    return pickle.dumps(None)
        except TypeError as e:
            if self.DatenMap is not None:
                Communicator.SchreibeFehler(e.message, ' loadObject@Datenserver')
            else:
                return 'DatenMap ist leer'
        except KeyError:
            if create:
                self.DatenMap[name]=None
                return pickle.dumps(None)
            else:
                Communicator.SchreibeFehler(name + ' in der DatenMap nicht vorhanden.\nCalled from {client} with request\"{request}\"'.format(self.client_address, self.client_request), ' loadObject@Datenserver')
                return pickle.dumps(None)

    def getSensorTemperatur(self, sensorname):
        try:
            sensor = self.DatenMap[SERVER_OBJEKT_SENSORLISTE].getSensor(name=sensorname)
            return sensor.getTemperatur()
        except KeyError:
            print (str(sensorname) + ' nicht vorhanden')
        except TypeError as e:
            Communicator.SchreibeFehler(e.message, 'in getSensorTemperatur@Datenserver')
        except AttributeError as e:
            if self.DatenMap[SERVER_OBJEKT_SENSORLISTE] is None:
                self.DatenMap[SERVER_OBJEKT_SENSORLISTE] = SensorListe.SensorListe()
            else:
                Communicator.SchreibeFehler(e.message, 'in getSensorTemperatur@Datenserver')
        except Exception as e:
            Communicator.SchreibeFehler(e.message, 'in getSensorTemperatur@Datenserver')

    @staticmethod
    def _eintr_retry(func, *args):
        """restart a system call interrupted by EINTR"""
        while True:
            try:
                return func(*args)
            except (OSError, select.error) as e:
                if e.args[0] != errno.EINTR:
                    raise

class httpHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, *args,**kwargs)

    def heizung(self, path):
        """Erzeugt die Website um Daten der Heizung ansehen zu können dynamisch"""
        valuesToShow, sensorList, pufferList = self.createLists()
        html = ""

        # Oeffne die html vorlage
        with open(path) as f:
            # Des zeug in die html datei eintragen
            for line in f.readlines():
                html += line

        # Erzeuge den rest, der anzuzeigen ist
        rest = ""
        html,openTag = self.openTag(placeholder='rest',html=html)
        html,closeTag = self.closingTag(placeholder='rest',html=html)
        for key in sorted(valuesToShow):
            try:
                value = self.server.DatenMap[key]
            except KeyError as e:
                Communicator.SchreibeFehler(e.message, 'heizung@httpHandler')
            finally:
                output = str(value)
                rest += openTag + '{value}'.format(value=output) + closeTag

        #Erzeugen des PufferBlocks
        puffer = ""
        html,openTag = self.openTag(placeholder='puffer',html=html)
        html,closeTag = self.closingTag(placeholder='puffer',html=html)
        for pufferObject in pufferList:
            puffer+=(openTag + '{pufferHTML}'.format(pufferHTML=pufferObject.html()) + closeTag)

        # Erzeugen des ParameterBlocks
        parameter = ""
        pDictionary = Communicator.GetParameter()
        html,openTag = self.openTag(placeholder='parameter',html=html)
        html,closeTag = self.closingTag(placeholder='parameter',html=html)
        for parameterKey in pDictionary:
            #parameter+=('<p class="pre">{key} = {value}\n</p>'.format(key=parameterKey, value=str(pDictionary[parameterKey])))
            parameter+=(openTag + '{key} = {value}'.format(key=parameterKey, value=str(pDictionary[parameterKey])) + closeTag)

        # Erzeugen des Fehlerblocks
        errors = ''
        html,openTag = self.openTag(placeholder='errors',html=html)
        html,closeTag = self.closingTag(placeholder='errors',html=html)
        try:
            with open(os.path.join(PFAD_HAUPTPROGRAMM,DATEINAME_ERROR_LOG)) as errorFile:
                for line in errorFile:
                    line = line.replace('\n','')
                    errors += openTag + line + closeTag
        except IOError: # Falls keine ErrorLog datei vorhanden ist
            errors = '<p class="pre" style="color: green">' + STATUS_KEINE_FEHLER + '</p>'


        # Alle Daten in die Vorlage reinschmeissen
        html = html.replace('\r','')
        while True:
            try:
                html = html.format( uhrzeit=str(time.strftime('%H:%M:%S')),
                                    sensoren=sensorList.html(),
                                    rest=rest,
                                    parameter=parameter,
                                    errors=errors,
                                    puffer=puffer)
                break
            except KeyError as e:
                html = html.replace('{'+e.message+'}','')
                #break

        #html in was brauchbares umwandeln
        f = StringIO()
        f.write(html)
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/html; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    @staticmethod
    def openTag(placeholder, html="", completeLine=True):
        """Parst die html Datei nach dem dem placeholder vorausgehenden Tag ab, um diesen Tag z.b. an jede Zeile anhaengen zu koennen
        und so die html Seite dynamisch mit der .html datei bearbeiten zu koennen, ohne dass ein Serverneustart erforderlich ist"""
        if placeholder[0] is not '{':
            placeholder = '{' + placeholder
        if placeholder[-1] is not '}':
            placeholder = placeholder + '}'

        posPlaceholder = html.index(placeholder)
        if completeLine:
            start = html.rfind('\n',0,posPlaceholder) # Rueckwaerts nach openTag suchen
            end = posPlaceholder
        else:
            start = html.rfind('<',0,posPlaceholder) # Rueckwaerts nach openTag suchen
            end = posPlaceholder
        openTag = html[start:end]
        html = html[:start] + html[end:]
        return html,openTag

    @staticmethod
    def closingTag(placeholder, html, completeLine=True):
        """Parst die html Datei nach dem dem placeholder nachfolgenden Tag ab, um diesen Tag z.b. an jede Zeile anhaengen zu koennen
        und so die html Seite dynamisch mit der .html datei bearbeiten zu koennen, ohne dass ein Serverneustart erforderlich ist"""
        if placeholder[0] is not '{':
            placeholder = '{' + placeholder
        if placeholder[-1] is not '}':
            placeholder = placeholder + '}'

        posPlaceholder = html.index(placeholder)
        if completeLine:
            start = posPlaceholder + len(placeholder)
            end = html.find('\n',start)
        else:
            posPlaceholder = html.index(placeholder)
            start = posPlaceholder + len(placeholder)
            end = html.find('>',start)+1
        closingTag = html[start:end]
        html = html[:start] + html[end:]
        return html,closingTag


    def createLists(self):
        valuesToShow = copy.copy(self.server.DatenMap)

        # Create SensorList:
        try:
            sensorList = self.server.DatenMap[SERVER_OBJEKT_SENSORLISTE]
            del valuesToShow[SERVER_OBJEKT_SENSORLISTE]
            if not sensorList.__class__.__name__ is SensorListe.SensorListe.__name__:
                sensorList = SensorListe.SensorListe()
        except TypeError:
            sensorList = SensorListe.SensorListe()
        except KeyError:
            sensorList = SensorListe.SensorListe()

        for key in self.server.DatenMap:
            try:
                value = self.server.DatenMap[key]
                # teste ob value ein sensor ist
                if value.__class__.__name__ == Sensor.Sensor.__name__:
                    sensorList.append(value)
                    del valuesToShow[key]
            except TypeError: # Falls value in DatenMap nicht gepickelt
                pass

        pufferListe = list()
        for key in self.server.DatenMap:
            try:
                value = self.server.DatenMap[key]
                # teste ob value ein sensor ist
                if value.__class__.__name__ == Puffer.Puffer.__name__:
                    pufferListe.append(value)
                    del valuesToShow[key]
            except TypeError: # Falls value in DatenMap nicht gepickelt
                pass

        return valuesToShow, sensorList, pufferListe

    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        #if not f:
        #    f = self.build_page()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        if path.endswith(DATEINAME_WEBSITE_HEIZUNG):
            return self.heizung(path)

        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def log_message(self, format, *args): # Hiermit wird der laestige print bei Seitenaufrufen zum schweigen gebracht
        return

def PrintAtServerShutdown(func, classname):
    """Decorator der bei Eintritt in eine shutdown-Funktion eine "wird beendet" Ausgabe einfuegt"""
    def inner(*args):
        print (classname + ' wird beendet.')
        func(*args)
    return inner

def PrintAtExit(func, classname):
    """Decorator der bei Austritt der Funktion eine "wurde beendet" Ausgabe einfuegt"""
    def inner(*args):
        func(*args)
        print ('---> ' + classname + ' erfolgreich beendet.')
    return inner


def main(argv):
    # todo : Rueckmeldung welche Threads in welchem zustand sind

    ThreadDatenserver = ServerThread(DatenServer(('', PORT_DATENSERVER), allow_none=True, logRequests=False), name='Datenserver')#, requestHandler=httpHandler)
    ThreadWebServer = ServerThread(WebServer(('',PORT_WEBSERVER), httpHandler, DatenMap=ThreadDatenserver.server.DatenMap), name='Webserver')#, requestHandler=httpHandler)
    ThreadService = ServerThread(Service(DatenMap=ThreadDatenserver.server.DatenMap, Datenserver=ThreadDatenserver.server), name='Service')#, requestHandler=httpHandler)

    try:

        print("Starten der Serverstruktur:")
        ThreadDatenserver.start()
        print("\tDatenserver gestartet")
        ThreadService.start()
        print("\tDatenmap gestartet")
        ThreadWebServer.start()
        print("\tWebserver gestartet")

        while True:
            # Warten und die Threads ihre Sachen machen lassen
            time.sleep(0.5)
    except KeyboardInterrupt:
        print ('\n'*2)
        print ('-'*8 + 'SHUTDOWN' + '-'*8)
        ThreadWebServer.server.shutdown()
        ThreadService.server.shutdown()
        ThreadDatenserver.server.shutdown()
        time.sleep(0.1)
        print ('-'*24)
        exit()
    except Exception as e:
        Communicator.SchreibeFehler(e,'main@Datenserver')

if __name__ == "__main__" :
    main(sys.argv)