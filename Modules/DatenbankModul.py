#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Markus Weber'

import MySQLdb as mydb
import sys
from Klassen import Communicator
import time
import types
import _mysql_exceptions as mydb_exceptions
from GlobalVariables import *

class DatenbankManager():
    def __init__(self):
        self.connected = False
        self.db = mydb.connection
        self.cursor = None

    def disconnect(self):
        try:
            print ("\ndisconnecting...")
            self.cursor.close()
            self.connected=False
        except Exception as e:
            print ('In disconnect: ' + str(e))
        try:
            self.db.close()
            self.connected=False
        except Exception as e:
            print ('In disconnect: ' + str(e))

    def connect(self):
        try:
            self.db = mydb.connect(HOST,USER,USER_PW,DATABASE)
            self.cursor = self.db.cursor()
            self.connected=True
            #atexit.register(self.disconnect())
        except mydb_exceptions.Error as e:
            print ('In DatenbankManager.connect:' + str(e))
            self.connected=False


    def writeTemperatures(self):
        #print ('Logging temperatures...')
        self.connect()
        if self.db.open and self.connected:
            sensorList = Communicator.getSensorList()
            sensornames = ''
            sensorvalues = ''
            for sensor in sensorList:
                sensornames += sensor.getName() + ','
                sensorvalues += str(sensor.getTemperatur()) + ','
            sensornames = sensornames[:-1]
            sensorvalues = sensorvalues[:-1]
            self._tableInsert(TABLENAME_TEMPERATUREN,sensornames,sensorvalues,datatype = 'VARCHAR',create = True)
        else:
            print ('Connection Error')

    def _tableInsert(self, tableName, columnName, value, datatype = 'VARCHAR', create=False):
        try:
            print ('logging data in: %s' %tableName)
            sql = "INSERT INTO %s (%s) VALUES (%s);" %(tableName,columnName,str(value))
            self.cursor.execute(sql)
            self.db.commit()

        except mydb_exceptions.OperationalError as e:
            print (e)
            error = str(e)
            missingColumnMessage = """(1054, \"Unknown column """
            if str(e).find(tableName) != -1:
                columns=['']
                for i in range(len(columnName)):
                    if columnName[i] != ",":
                        columns[-1] += columnName[i]
                    else:
                        columns += ['']
                print columns
                for column in columns:
                    self.createColumn(tableName,column,datatype)

            #Create missing columns
            if error.find(missingColumnMessage) != -1 and create:
                missingColumn = error[error.find(missingColumnMessage)+len(missingColumnMessage)+1:]
                missingColumn = missingColumn[:missingColumn.find('\'')]
                print (error)
                print (missingColumn)
                self.createColumn(tableName,missingColumn,datatype)
                self._tableInsert(tableName,columnName,value,datatype,create)
        except mydb_exceptions.ProgrammingError as e:
            print (e)
            error = str(e)
            missingTableMessage = "Table "
            #Create missing tables
            if error.find(missingTableMessage) != -1 and create:
                self.createTable(tableName)
                self._tableInsert(tableName,columnName,value,datatype,create)
        try:
            self.db.commit()
        except mydb_exceptions.OperationalError as e:
            Communicator.SchreibeFehler(e, ' tableInsert()')


    def createColumn(self,tableName, columnName, datatype = 'VARCHAR'):
        try:
            sql = """ALTER TABLE %s ADD COLUMN %s %s(40) ;""" %(str(tableName),str(columnName),str(datatype))
            print (sql)
            self.cursor.execute(sql)
            self.db.commit()
        except mydb_exceptions.OperationalError:
            pass

    def createTable(self,tableName):
        print (tableName)
        sql = "CREATE TABLE IF NOT EXISTS %s ( ID INT NOT NULL AUTO_INCREMENT, timestamp TIMESTAMP, PRIMARY KEY (ID));" %tableName
        print (sql)
        self.cursor.execute(sql)
        self.db.commit()
        sql = "CREATE INDEX %s ON %s(timestamp) " %(COLUMN_TIMESTAMP, tableName)
        print (sql)
        self.cursor.execute(sql)
        self.db.commit()

    def logObject(self,objectName,classObject):
        self.connect()
        if self.db.open:
            objectVariables = self.prepareObjectVariables(classObject)
            varList = ""
            valList = ""
            for variable in objectVariables.keys():
                if objectVariables[variable]:
                    varList += str(variable) + ','
                    valList += str(objectVariables[variable]) + ','
            varList = varList[:-1]
            valList = valList[:-1]
            self._tableInsert(str(objectName),str(varList),str(valList),'VARCHAR',True)

    def prepareObjectVariables(self, object):
        try:
            variableDictionary = vars(object)
            self.prepareVariables(variableDictionary)
        except TypeError:
            variableDictionary = object
        return variableDictionary

    def prepareVariables(self, variableDictionary):
        for variable in variableDictionary.keys():
            if type(variableDictionary[variable]) is types.InstanceType:
                del variableDictionary[variable]
            elif type(variableDictionary[variable]) is types.ListType:
                for element in range(len(variableDictionary[variable])):
                    newName = str(variable) + str(element)
                    variableDictionary[newName]=variableDictionary[variable][element]
                del variableDictionary[variable]
            elif type(variableDictionary[variable]) is types.DictionaryType:
                for key in variableDictionary[variable].keys():
                    newName = str(key) + "_from_" + str(variable)
                    variableDictionary[newName]=variableDictionary[variable][key]
                del variableDictionary[variable]
            elif str(variableDictionary[variable]) == '':
                del variableDictionary[variable]
        for variable in variableDictionary.values():
            if type(variable) is types.InstanceType or type(variable) is types.ListType or type(variable) is types.DictionaryType:
                self.prepareVariables(variableDictionary)
        #return variableDictionary


def main(argv):
    global dbManager
    try:
        dbManager = DatenbankManager()
        #
        while True:
            dbManager.writeTemperatures()
            time.sleep(TIME_BETWEEN_LOGS)
    except KeyboardInterrupt:
        exit()
    finally:
        dbManager.disconnect()


if __name__ == "__main__":
    main(sys.argv)