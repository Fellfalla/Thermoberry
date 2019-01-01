#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Markus Weber'
import sys
from threading import Thread, Lock, Event
import time

from Klassen import Communicator
from Modules import Datenserver, PufferSteuerungRaspi1, PufferSteuerung, Mischer, SensorAuswertung

#todo: hinzufügen einer schnittstelle zum manuellen neustarten spezifischer module
#todo: parsen der argumente ( groß und kleinschreibung vernachlässigen )
#todo: schreibe an Server, welche module online bzw. offline sind
#todo unterscheiden ob module argv brauchen oder nicht


# Achte auf die reihendfolge der Module! Abhängige module ganz unten
Modules = {"Datenserver" : Datenserver.main,
            "Temperatursteuerung" : SensorAuswertung.main,
            "Mischersteuerung" : Mischer.main,
            "Puffersteuerung" : PufferSteuerung.main,
            "Puffersteuerungraspi1" : PufferSteuerungRaspi1.main,
           }


# Define Module Threads
class FuncThread(Thread):
    """
    Dieser thread startet die angegebene funktion mit den übergebenen argumenten
    """
    def __init__(self, target, name="unnamed Module", *args):
        super(FuncThread, self).__init__()
        self._target = None
        self._args = None

        self.setTarget(target)
        self.setArgs(args)
        self.setName(name)
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

def RestartModule(module, active_modules):
    active_modules.remove(module)
    module = FuncThread(module.getTarget(), module.getName(), module.getArgs())
    active_modules.append(module)
    module.start()

def CreateModules(argv):
    """
    erzeugt aus den in der Commandozeile übergebenen Modulen die Module, welche ausgeführt werden sollen
    :param argv: vom System übergebene variablen
    :return:
    """
    modules_to_run = []
    for arg in argv:
        if Modules.has_key(arg):
            module_entry = Modules[arg]
            module_name = arg
            module = FuncThread(module_entry, module_name, argv)
            modules_to_run.append(module)

    return modules_to_run

if __name__ == "__main__" :
    try:

        # Ausgabe der verfügbaren module
        availableModules = ""
        for key in Modules.keys():
            availableModules += "\t- {key}\n".format(key=key)
        print("Verfügbare Module:\n{availableModules}".format(availableModules=availableModules))


        active_modules = CreateModules(sys.argv)

        # Ausgabe der aktiven module
        selectedModules = ""
        for module in active_modules:
            selectedModules += "\t- {key}\n".format(key=module.getName())
        print("Aktive Module:\n{activemodules}".format(activemodules=selectedModules))

        # Starten der Module
        for module in active_modules:
            # print("\nStarting module: " + module.name)
            # TODO: warte bis modul fertig gestartet wurde, bevor das nächste modul gestartet wird
            module.start()
            print("\n" + str(module))


        while True:
            # Warten und die Threads ihre Sachen machen lassen
            for module in active_modules:
                if module.isAlive() is False:
                    Communicator.SchreibeFehler("Das Modul {name} ist offline!".format(name= module.getName()), "main@Thermoberry")
                    print("Trying to restart {moduleName}".format(moduleName=module.getName()))
                    RestartModule(module, active_modules)
            time.sleep(25)

    except KeyboardInterrupt:
        print ('\n'*2)
        print ('-'*8 + 'SHUTDOWN' + '-'*8)
        for module in active_modules:
            print (module)
            module.stop() #todo: das funktioniert so noch nicht
        time.sleep(0.2)
        print ('-'*24)
        exit()
    except Exception as e:
        Communicator.SchreibeFehler(e,'main@Thermoberry')

