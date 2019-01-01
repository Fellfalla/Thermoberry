#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Klassen.Classes as Classes
import Klassen.Communicator as Communicator
from GlobalVariables import *
import os
import socket
import time

#1) todo: Hinweis: starte dein script (process) in der /etc/inittab mit dem keyword respawn d.h. der process wird neu gesartet wenn er aus irgendeinem grund beendet wird

class WatchDog():
	def __init__(self):
		self.Stoerung = False
		self.Parameter = Communicator.GetParameter()
		self.Lampe = Classes.Warnlampe()
		self.Intervall = KONTROLL_INTERVALL

	def ProtokolliereDaten(self):
		sensorList = Communicator.getSensorList()
		self.Parameter = Communicator.GetParameter()
		try:
			MinLogZeit = self.Parameter["MinProtokollierteZeitspanne"]
			if MinLogZeit < 0.1 :
				MinLogZeit = 0.1
		except KeyError:
			print ("In ProtokolliereDaten() Parameter[\"MinProtokollierteZeitspanne\"] ist nicht vorhanden")
			MinLogZeit = 20 #stunden
		Daten = ["SensornameZuTemperatur: " + str(sensorList) + "\n",
		         "Parameter: " + str(self.Parameter) + "\n"]
		Zeilen = len(Daten)+1#Zeitstempel wird in Log() hinzugefügt
		MaxZeilen = (MinLogZeit*3600)/(self.Intervall/Zeilen)
		print ("Protokollierte Zeitspanne: %6.2f Stunden" %MinLogZeit)
		if self.Intervall < 3600:
			print ("ProtokollierungsIntervall: %6.2f Sekunden" %self.Intervall)
		else:
			print ("ProtokollierungsIntervall: %6.2f Stunden" %(self.Intervall/3600))
		print ("Geschaetzte Protokollgroeße: %6.3f MB" %((float(MaxZeilen)*0.173)/1000))
		Communicator.Log (Daten,MaxZeilen=MaxZeilen) # Daten enthält 6 Zeilen

	def run(self):
		self.Parameter = Communicator.GetParameter()
		try:
			self.Intervall = self.Parameter["ProtokollierungsIntervall"]
			if self.Intervall < 0.01:
				self.Intervall = 0.01
		except KeyError:
			print ("KeyError in Warnung --- ProtokollierungsIntervall in Parameterdatei nicht vorhanden")
			self.Intervall = KONTROLL_INTERVALL
		WarnText=""
		try:
			WarnDatei = Communicator.fileReader(dateiName=DATEINAME_ERROR_LOG, createIfNotExisting=False, errorMsg = False)  #vorhandene fehler einlesen
			for line in WarnDatei:
				WarnText+=line #Email mit exception lines erstellen
				self.Stoerung = True
			if WarnText == "":
				os.remove(DATEINAME_ERROR_LOG)
				self.Stoerung = False
			#
		except IOError:
			self.Stoerung = False

		# todo: test ob alle programmteile Laufen
		#KOmmunikationsprozess der von jedem programmteil aufgerufen wird und in datei geschrieben wird
		#test ob die Dateien aktualisiert werden
		if self.Stoerung:
			print ("Es sind Fehler vorhanden!!!")
			try:
				self.Intervall = self.Parameter["ProtokollierungsIntervallBeiFehler"]*3600
			except KeyError:
				self.Intervall = KONTROLL_INTERVALL_FEHLER #3 Stunden
			self.Lampe.Ein() #Alarmlampe an
			#print WarnText
			try:
				if self.Parameter["MailsAktiviert"] == "True":
					os.system ("sudo python Mailsoftware.py " + "\"\"\"" + WarnText + "\"\"\"") #eMail versenden
					os.remove(DATEINAME_ERROR_LOG)
			except KeyError:
				print ("KeyError in Watchdog: Parameter[\"MailsAktiviert\"] nicht vorhanden")
				os.system ("sudo python Mailsoftware.py " + "\"\"\"" + WarnText + "\"\"\"") #eMail versenden
				os.remove(DATEINAME_ERROR_LOG)
		else:
			print ("Keine Fehler vorhanden")
		self.ProtokolliereDaten()
		time.sleep(self.Intervall)

	def checkWarnlampe(self):
		try:
			warnGPIO = Communicator.GetGPIO()[BEZEICHNUNG_WARNLAMPE]
			if warnGPIO != self.Lampe.GPIO_EinAus:
				del self.Lampe
				self.Lampe = Classes.Warnlampe(warnGPIO)
		except KeyError:
			print ('Warnlampe an %s nicht angeschlossen' %socket.gethostname())
			self.Lampe.angeschlossen = False


def main():
	waechter = WatchDog()
	while True:
		try:
			waechter.run()
		except Exception as e:
			Communicator.SchreibeFehler(e,'WatchDog - Main')
		except KeyboardInterrupt:
			exit()

if __name__ == "__main__":
	main()