#!/usr/bin/python
# -*- coding: utf-8 -*.

from email.parser import Parser
import smtplib
import sys


def main(argv):
    to = ['marweb@alice.de', 'weberol@alice-dsl.net']
    #to.append('tobias.obermayer@gmail.com')

    user = 'myraspberry@web.de'
    raise NotImplementedError('The password has to be read from local file')
    passwort= 'REMOVED'
    i = 0
    while i < 1:
        try:
            subject = 'Heizungssteuerung mit Raspberry'
            text = ""
            for schnipsel in argv:
                text+=schnipsel

            headers=[]
            for Adressat in to:
                headers.append(Parser().parsestr(
                    'From: ' + user + '\n'
                    'To: ' + Adressat + '\n'
                    'Subject: ' + subject +'\n'
                    '\n'
                    + text + '\n'))



            smtp = smtplib.SMTP(host='smtp.web.de', port=587)
            
            # smtp.ehlo()
            smtp.starttls()
            # smtp.ehlo()
            smtp.login("myraspberry@web.de", passwort)
            for header in headers:
                smtp.sendmail(header['from'], header['to'], header.as_string())
            #smtp.quit()
            i+=1
            print ("Mail versendet an:")
            for Empfaenger in to:
                print (Empfaenger)
            #time.sleep(2)
        except KeyboardInterrupt:
            exit()

if __name__ == "__main__":
   main(sys.argv[1:])