__author__ = 'tommy3001'

#import template engine
from jinja2 import Environment, FileSystemLoader

#import tornado
import tornado.ioloop
import tornado.web
import urllib.request

from datetime import date,timedelta
#load template file templates/site.html and base.html
templateLoader = FileSystemLoader( searchpath="templates/" )
templateEnv = Environment( loader=templateLoader )
template_main = templateEnv.get_template("base.html")
template_piratetable = templateEnv.get_template("site.html")

WochentagIndex ={"Montag":0, "Dienstag":1, "Mittwoch":2, "Donnerstag":3, "Freitag":4, "Samstag":5, "Sonntag":6}
StammtischModel = {"Wochentag":"","Ort":"", "Uhrzeit" :"","Typ":"","PPad-group": "","wkday":0}

Stammtisch = []
Stammtisch.append(dict(StammtischModel))
Stammtisch.append(dict(StammtischModel))

###### Konfiguration #########

#Anzahl der Protokolle pro Stammtisch
MAX_LINKS = 5
#Liste der Adressen
Orte = ["Wahlkreisbüro, Wichlinghauser Straße 61, 42277 Wuppertal-Wichlinghausen","Ort noch nicht bestimmt"]

Stammtisch[0]["Wochentag"] = "Montag"
Stammtisch[0]["Ort"] = Orte[0]
Stammtisch[0]["Uhrzeit"] = "19:30"
Stammtisch[0]["Typ"] = "Organisations-Stammtisch"

#Piraten-Pad-Gruppe auf piratenpad.de
Stammtisch[0]["PPad-group"] = "stammtisch"

Stammtisch[1]["Wochentag"] = "Dienstag"
Stammtisch[1]["Ort"] = Orte[0]
Stammtisch[1]["Uhrzeit"] = "19:30"
Stammtisch[1]["Typ"] = "AK-Kommunal-Stammtisch"

Stammtisch[1]["PPad-group"] = "ak-kommunalpolitik-wuppertal"

########### Konfiguration ende ##########

Stammtisch[0]["wkday"] =WochentagIndex[Stammtisch[0]["Wochentag"]]
Stammtisch[1]["wkday"] =WochentagIndex[Stammtisch[1]["Wochentag"]]

#date today
today = date.today()
isotoday = today.timetuple()
wkday = isotoday.tm_wday

meetings_len = len(Stammtisch)

#Globale Array-Variablen
datetextlinks=[[],[]]  #Link-Text-Array
links=[[],[]] #Link-Adress-Array

padInformation=[[],[]] #Kurzbeschreibungen der Treffen
html_output_protocol = []  #Html-Output der Stammtischseiten
piratetable_list = []  #Liste der Stammtische mit Ort-Zeit-Angaben für die Hauptseite

#Berechnung der Piraten-Protokollendung für die Link-Adresse (Datum-Basiert)
def calculateDateLink(day):
   return   "S" + (today-timedelta(days=(wkday-day))).strftime("%y%m%d")


#Berechnung für das Datum für den Linktext zum Piraten-PRotokoll
def calculateDateText(day):
    return (today-timedelta(days=(wkday-day))).strftime("%d.%m.%Y")


#Update der Variablen für alle Stammtische
def updateVariables():
    for i in range(meetings_len):
        updateVariable(i)

#Update der Variablen für ein bestimmten Stammtisch i
def updateVariable(i):
    links[i] = []
    datetextlinks[i] = []
    padInformation[i] = []
    #Iteration über alle Treffen eines Stammtisches (Wochenweise)
    for j in range(MAX_LINKS):
            #Berechenung der Links-Adressen zu verschiedenen Wochen
            links[i].append(calculateDateLink(Stammtisch[i]["wkday"]-((MAX_LINKS*7-7)-j*7)))
            #Berechnung des Link-Textes zu den verschiedenen Wochen
            today = date.today()
            isotoday = today.timetuple()

            if (( isotoday.tm_wday == Stammtisch[i]["wkday"]) and  (j == (MAX_LINKS-1))):
                datetextlinks[i].append("Protokoll für Heute")
                links[i].append(calculateDateLink(Stammtisch[i]["wkday"]-((MAX_LINKS*7-7)-(j+1)*7)))
                datetextlinks[i].append("Vorbereitung für nächsten Stammtisch am: "
                                        + calculateDateText(Stammtisch[i]["wkday"]-((MAX_LINKS*7-7)-(j+1)*7)))
            elif j == (MAX_LINKS-1):
                datetextlinks[i].append("Vorbereitung für nächsten Stammtisch am: "
                                        + calculateDateText(Stammtisch[i]["wkday"]-((MAX_LINKS*7-7)-j*7)))
            else:
                datetextlinks[i].append("Protokoll von "+Stammtisch[i]["Wochentag"]+", den: "
                                        + calculateDateText(Stammtisch[i]["wkday"]-((MAX_LINKS*7-7)-j*7)))
            #Öffnen der Piratenpad-TXT-Datei
            try:
                file = urllib.request.urlopen('https://'+Stammtisch[i]["PPad-group"]+'.piratenpad.de/ep/pad/export/'+links[i][j]+'/latest?format=txt')
            except:
                padInformation[i].append('Piraten-Pad nicht vorhanden!')
            else:
                #Suchen nach der Kurzinformation
                for line in file:
                    string = str(line, encoding='utf-8')
                    InfAvail = False
                    if '"-' in string:
                        temp =string[string.find('"-')+2:string.find('-"')]
                        #Speichern der Kurzinformation zur entsprechenden Woche
                        padInformation[i].append(temp)
                        InfAvail = True
                        break

                if InfAvail == False:
                    padInformation[i].append("Keine Kurzinformationen vorhanden!")

#Erzeuge HTML output mit dem Template-System
def createHtmlOutput(i):
    return template_piratetable.render( title="Piratenpartei Wuppertal - Protokollübersicht " +
                                                                    Stammtisch[i]["Typ"],time_place = "Jeden" +
                                                                    Stammtisch[i]["Wochentag"] +"  ab " +
                                                                    Stammtisch[i]["Uhrzeit"] +
                                                                    "Uhr ("+ Stammtisch[i]["Typ"]+"). Ort: " +
                                                                    Stammtisch[i]["Ort"],
                                                                link=links[i],
                                                                date=datetextlinks[i],
                                                                group=Stammtisch[i]["PPad-group"],
                                                                Information= padInformation[i])

#Erzeuge Liste der Stammtische für Hauptseite
def createStammtische():
    piratetable_list = []
    for i in range(meetings_len):
        piratetable_list.append([Stammtisch[i]["Typ"],"Jeden " +Stammtisch[i]["Wochentag"] +" ab " + Stammtisch[i]["Uhrzeit"],
        "Ort: " + Stammtisch[i]["Ort"]])
    return piratetable_list

#Handler für Hauptseite
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(html_output_main)

#Handler für Stammtisch-Protokoll-Seiten
class ProtocolHandler(tornado.web.RequestHandler):
    def get(self,Protocol_id):
        updateVariable(int(Protocol_id))
        self.write(createHtmlOutput(int(Protocol_id)))


# Assign handler to the server root  (127.0.0.1:PORT/)
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/piratemeeting/([0-9]+)", ProtocolHandler),
])

PORT=8000
if __name__ == "__main__":
    # Setup and start the server
    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")
    updateVariables()
    html_output_main = template_main.render(list=createStammtische())
    application.listen(PORT)
    tornado.ioloop.IOLoop.instance().start()


