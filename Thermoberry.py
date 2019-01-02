#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Markus Weber'
import sys
from threading import Thread, Event
import time
import importlib

from Klassen import Communicator
import ConfigParser as configparser
import GlobalVariables as gv

# from Modules import Datenserver, PufferSteuerungRaspi1, PufferSteuerung, Mischer, SensorAuswertung

#todo: hinzufügen einer schnittstelle zum manuellen neustarten spezifischer module
#todo: parsen der argumente ( groß und kleinschreibung vernachlässigen )
#todo: schreibe an Server, welche module online bzw. offline sind
#todo unterscheiden ob module argv brauchen oder nicht


# Achte auf die reihendfolge der Module! Abhängige module ganz unten
# Modules = {"Datenserver" : Datenserver.main,
#             "Temperatursteuerung" : SensorAuswertung.main,
#             "Mischersteuerung" : Mischer.main,
#             "Puffersteuerung" : PufferSteuerung.main,
#             "Puffersteuerungraspi1" : PufferSteuerungRaspi1.main,
#            }

# Laden der modul config
configparser = configparser.ConfigParser()
configparser.optionxform = str # Deals with case sensitive module imports
configparser.read(gv.SETINGS_FILE_PATH)
modules_settings = [(key, enabled) for key, enabled in configparser.items('MODULES') if key not in configparser.defaults()]

# Define Module Threads
class ModuleThread(Thread):
    """
    Dieser thread startet die angegebene funktion mit den übergebenen argumenten
    """
    def __init__(self, target, module_name, *args):
        super(ModuleThread, self).__init__()
        self._target = None
        self._args = None

        self.setTarget(target)
        self.setArgs(args)
        self.setName(module_name)
        self._stop = Event()
        self.setDaemon(True)

    def run(self):
        try:
            self._target(*self._args)
        except Exception as exception:
            Communicator.SchreibeFehler(exception, self.getName())

    def stop(self):
        self._stop.set()

    def getTarget(self):
        return self._target

    def getArgs(self):
        return self._args

    def setTarget(self, target):
        self._target = target

    def setArgs(self, *args):
        self._args = args

    def stopped(self):
        return self._stop.isSet()

    def __str__(self):
        return "{name} is running: {status}".format(name=self.getName(), status=self.isAlive())

def restart_module(module, active_modules):
    """ Startet module neu und ersetzt das objekt in active_modules """
    active_modules.remove(module)
    module = ModuleThread(module.getTarget(), module.getName(), module.getArgs())
    active_modules.append(module)
    module.start()

def create_module_threads(argv):
    """
    erzeugt aus den in der Commandozeile übergebenen Modulen die Module, welche ausgeführt werden sollen
    :param argv: vom System übergebene variablen
    :return:
    """
    module_threads =  []
    
    # Laden der module
    for module_name, is_enabled in modules_settings:
        if is_enabled in [True, str(True), 'true', 'enabled', str(1), 1]:
            try:
                module = importlib.import_module("Modules." + module_name, package='')
            except ImportError as e:
                print("ERROR: Make shure you use the correct module name (" + module_name + ") in " + gv.SETINGS_FILE_PATH)
            module_entry = module.main
            module_thread = ModuleThread(module_entry, module_name, argv)
            module_threads.append(module_thread)

    return module_threads

if __name__ == "__main__" :
    try:

        # Ausgabe der verfügbaren module
        availableModules = ""
        for module_name, _ in modules_settings:
            availableModules += "\t- {key}\n".format(key=module_name)
        print("Verfügbare Module:\n{availableModules}".format(availableModules=availableModules))


        module_threads = create_module_threads(sys.argv)

        # Ausgabe der aktiven module
        selectedModules = ""
        for module in module_threads:
            selectedModules += "\t- {key}\n".format(key=module.getName())
        print("Aktive Module:\n{activemodules}".format(activemodules=selectedModules))

        # Starten der Module
        for module in module_threads:
            # print("\nStarting module: " + module.name)
            # TODO: warte bis modul fertig gestartet wurde, bevor das nächste modul gestartet wird
            module.start()
            print("\n" + str(module))


        while True:
            # Warten und die Threads ihre Sachen machen lassen
            for module in module_threads:
                if module.isAlive() is False:
                    Communicator.SchreibeFehler("Das Modul {name} ist offline!".format(name= module.getName()), "main@Thermoberry")
                    print("Trying to restart {moduleName}".format(moduleName=module.getName()))
                    restart_module(module, module_threads)
            time.sleep(25)

    except KeyboardInterrupt:
        print ('\n'*2)
        print ('-'*8 + 'SHUTDOWN' + '-'*8)
        for module in module_threads:
            print (module)
            module.stop() #todo: das funktioniert so noch nicht
        time.sleep(0.2)
        print ('-'*24)
        exit()
    except Exception as e:
        Communicator.SchreibeFehler(e,'main@Thermoberry')

