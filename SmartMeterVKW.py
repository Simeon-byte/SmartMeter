from os import system, name
import sys
from time import sleep
import binascii
import datetime
import serial
from Cryptodome.Cipher import AES
import paho.mqtt.client as mqtt
import os
import json

f = open("config/config.json", "r")
config = json.load(f)

# Environment Variable setzen, damit der Fehler nicht auf der Console Kommt
os.environ['TERM'] = 'xterm'

#Aktuelle Werte auf Console ausgeben (True | False)
printValue = config["printValue"]

#MQTT Verwenden (True | False)
useMQTT = config["useMQTT"]
#Custom MQTT Credentials or use env provided
useEnvMqttConfig = config["useEnvMqttConfig"]
#MQTT Broker IP adresse Eingeben ohne Port!
if useMQTT:
    try:
        if (not useEnvMqttConfig) and config["mqttConfig"]:
            mqttBroker = config["mqttConfig"]["mqttBroker"] or "localhost"
            mqttuser = config["mqttConfig"]["mqttUser"] or ""
            mqttpasswort = config["mqttConfig"]["mqttPassword"] or ""
            mqttport = config["mqttConfig"]["mqttPort"] or 1883
        else:
            mqttBroker = os.environ["MQTT_BROKER"] or "localhost"
            mqttuser = os.environ["MQTT_USER"]  or ""
            mqttpasswort = os.environ["MQTT_PASSWORD"]  or ""
            mqttport = os.environ["MQTT_PORT"] or 1883
    except KeyError as e:
        print(f"Error: Missing configuration or environment variable: {e}")
        sys.exit()
#Comport Config/Init
comport = config["comport"] or '/dev/ttyUSB0'

# EVN Schlüssel eingeben zB. “36C66639E48A8CA4D6BC8B282A793BBB”
key = config["key"]
key=binascii.unhexlify(key)

def clear():
    if printValue:
        if name == 'nt':
            _ = system('cls')
    
        else:
            _ = system('clear')

def log(string):
    if printValue:
        print(string)

def mqttPublish(topic, payload):
    if useMQTT:
        client.publish(topic, payload)

#MQTT Init
if useMQTT:
    try:
        client = mqtt.Client("SmartMeter")
        client.username_pw_set(mqttuser, mqttpasswort)
        client.connect(mqttBroker, mqttport)
    except:
        print("Broker nicht erreichbar / Falsche Credentials !")
        sys.exit()

def recv(serial):
    while True:
        data = serial.read_all()
        if data == '':
            log ("\n...")
            continue
        else:
            #log ("\n...lausche auf Schnittstelle")
            break
    return data

	
if __name__ == '__main__':
    serial = serial.Serial(
     port=comport,
     baudrate = 2400,
     parity=serial.PARITY_EVEN,
     stopbits=serial.STOPBITS_ONE,
     bytesize=serial.EIGHTBITS
    )

    # Header Startbytes vom Vorarlberger Smartmeter
    headerstart = "68fafa68"

    while True:

        sleep(5)
 
        data = recv(serial)
        doit = 0
        if (data != b'') & (len(data) >= 355):
            startbytes = data[0:4].hex()

            if (startbytes == headerstart):
                doit = 1
                #log ("Laenge von data = ", len(data))
            else:
                # syncronisierung nötig
                clear()
                log ("\n*** Synchronisierung laeuft ***\n")
                #log ("Laenge von data = ", len(data))
                serial.flushInput()
                sleep(.5)



        if doit == 1 :
            clear()
            log ("data: " + data.hex())
            msglen1 = int(hex(data[1]),16) # 1. FA --- 250 Byte
            #log ("msg1: ", msglen1)

            if useMQTT and client.is_connected() == False:
                client.reconnect()
                log ("MQTT Reconnect")
            header1 = 27
            header2 = 9

            splitinfo = data[6] # wenn hier 00, dann gibts noch eine Nachricht

            systitle = data[11:19] # hier steht der SysTitle --- 8 Bytes
            #log ("systitle:", systitle.hex() )

            ic = data[23:27] # hier steht der SysTitle --- 4 Bytes
            iv = systitle + ic # iv ist 12 Bytes
            #log ("iv= ", iv.hex() , "Länge: ", len(iv))

            #log ("\nmsg1:")
            msg1 = data[header1:(6+msglen1-2)]
            #log (msg1.hex())
            #log ("Länge: ",len(msg1))

            #log ("\nmsg2:")
            msglen2 = int(hex(data[msglen1+7]),16) # 1. FA --- 38 Byte
            #log ("msglen2: ", msglen2)
            #log (hex(data[msglen1+7]))

            msg2 = data[msglen1+6+header2:(msglen1+5+5+msglen2)]
            #log (msg2.hex())
            #log ("Länge msg2 :" ,len(msg2))


            cyphertext = msg1 + msg2
            #log ("\ncyphertext:")
            #log (cyphertext.hex())
            #log ("Länge: ",len(cyphertext))

            cyphertext_bytes=binascii.unhexlify(cyphertext.hex())
            cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
            decrypted = cipher.decrypt(cyphertext_bytes)

            #log("\nDecrypted:")
            #log(decrypted.hex())

            # OBIS Code Werte aus decrypted.hex auslesen
            databin = decrypted.hex()
            ueberschrift = ("\n\t\t*** KUNDENSCHNITTSTELLE ***\n\nOBIS Code\tBezeichnung\t\t\t Wert")
            log (ueberschrift)
            #log(databin)

            obis_len = 12

            # Datum Uhrzeit lesen
            # 0000010000ff
            obis_zeitstempel = '0000010000ff'
            obis_zeitstempel_offset = 4
            obis_zeitlaenge = 24
            obis_zeitstempel_pos = databin.find(obis_zeitstempel)
            if obis_zeitstempel_pos > 1:
                obis_datum_zeit = databin[obis_len + obis_zeitstempel_pos + obis_zeitstempel_offset:obis_len + obis_zeitstempel_pos + obis_zeitstempel_offset + obis_zeitlaenge]
                jahr = int(obis_datum_zeit[:4],16)
                monat = int(obis_datum_zeit[4:6],16)
                tag = int(obis_datum_zeit[6:8],16)
                stunde = int(obis_datum_zeit[10:12],16)
                minute = int(obis_datum_zeit[12:14],16)
                sekunde = int(obis_datum_zeit[14:16],16)

                obis_datum_zeit = datetime.datetime(jahr,monat,tag, stunde, minute, sekunde)
                #datum_zeit = "0.0.1.0.0.255\tDatum Zeit:\t\t\t "+obis_datum_zeit.strftime("%d.%m.%Y %H:%M:%S")
                datum_zeit = obis_datum_zeit.strftime("%d.%m.%Y %H:%M:%S")
                
                log(datum_zeit)
                mqttPublish("Smartmeter/Zeit",obis_datum_zeit.strftime("%Y-%m-%d %H:%M:%S"))
            
            else:
                #obis fehler
                datum_zeit = "\n*** kann OBIS Code nicht finden ===> key Fehler? ***\n"
                log (datum_zeit)


            # Zählernummer des Netzbetreibers
            # 0000600100ff
            obis_zaehlernummer = '0000600100ff'
            obis_zaehlernummer_pos = databin.find(obis_zaehlernummer)
            if obis_zaehlernummer_pos > 1:
                obis_zaehlernummer_anzzeichen = 2*int(databin[obis_zaehlernummer_pos+obis_len+2:obis_zaehlernummer_pos+obis_len+4],16)
                obis_zaehlernummer = databin[obis_zaehlernummer_pos+obis_len+4:obis_zaehlernummer_pos+obis_len+4+obis_zaehlernummer_anzzeichen]
                bytes_object = bytes.fromhex(obis_zaehlernummer)
                zaehlernummer = "0.0.96.1.0.255\tZaehlernummer:\t\t\t "+bytes_object.decode("ASCII")
                zaehlernummerfilename = bytes_object.decode("ASCII")
                log(zaehlernummer)
                mqttPublish("Smartmeter/Zaehlernummer",bytes_object.decode("ASCII"))


            # COSEM Logical Device Name
            # 00002a0000ff
            obis_cosemlogdevname = '00002a0000ff'
            obis_cosemlogdevname_pos = databin.find(obis_cosemlogdevname)
            if obis_cosemlogdevname_pos > 1:
                obis_cosemlogdevname_anzzeichen = 2*int(databin[obis_cosemlogdevname_pos+obis_len+2:obis_cosemlogdevname_pos+obis_len+4],16)
                obis_cosemlogdevname = databin[obis_cosemlogdevname_pos+obis_len+4:obis_cosemlogdevname_pos+obis_len+4+obis_cosemlogdevname_anzzeichen]
                bytes_object = bytes.fromhex(obis_cosemlogdevname)
                cosemlogdevname = "0.0.42.0.0.255\tCOSEM logical device name:\t "+bytes_object.decode("ASCII")
                
                log(cosemlogdevname)
                mqttPublish("Smartmeter/Cosemlogdevname",bytes_object.decode("ASCII"))


            # Spannung L1 (V)
            # 0100200700ff
            obis_spannungl1 = '0100200700ff'
            obis_spannungl1_pos = databin.find(obis_spannungl1)
            if obis_spannungl1_pos > 1:
                obis_spannungl1_anzzeichen = 4
                obis_spannungl1 = databin[obis_spannungl1_pos+obis_len+2:obis_spannungl1_pos+obis_len+2+obis_spannungl1_anzzeichen]
                spannungl1 = "1.0.32.7.0.255\tSpannung L1 (V):\t\t "+str(int(obis_spannungl1,16)/10)
                
                log(spannungl1)
                mqttPublish("Smartmeter/SpannungL1",int(obis_spannungl1,16)/10)


            # Spannung L2 (V)
            # 0100340700FF
            obis_spannungl2 = '0100340700ff'
            obis_spannungl2_pos = databin.find(obis_spannungl2)
            if obis_spannungl2_pos > 1:
                obis_spannungl2_anzzeichen = 4
                obis_spannungl2 = databin[obis_spannungl2_pos+obis_len+2:obis_spannungl2_pos+obis_len+2+obis_spannungl2_anzzeichen]
                spannungl2 = "1.0.52.7.0.255\tSpannung L2 (V):\t\t "+str(int(obis_spannungl2,16)/10)
                
                log(spannungl2)
                mqttPublish("Smartmeter/SpannungL2",int(obis_spannungl2,16)/10) 


            # Spannung L3 (V)
            # 0100480700ff
            obis_spannungl3 = '0100480700ff'
            obis_spannungl3_pos = databin.find(obis_spannungl3)
            if obis_spannungl3_pos > 1:
                obis_spannungl3_anzzeichen = 4
                obis_spannungl3 = databin[obis_spannungl3_pos+obis_len+2:obis_spannungl3_pos+obis_len+2+obis_spannungl3_anzzeichen]
                spannungl3 = "1.0.72.7.0.255\tSpannung L3 (V):\t\t "+str(int(obis_spannungl3,16)/10)
                
                log(spannungl3)
                mqttPublish("Smartmeter/SpannungL3",int(obis_spannungl3,16)/10)


            # Strom L1 (A)
            # 01001f0700ff
            obis_stroml1 = '01001f0700ff'
            obis_stroml1_pos = databin.find(obis_stroml1)
            if obis_stroml1_pos > 1:
                obis_stroml1_anzzeichen = 4
                obis_stroml1 = databin[obis_stroml1_pos+obis_len+2:obis_stroml1_pos+obis_len+2+obis_stroml1_anzzeichen]
                stroml1 = "1.0.31.7.0.255\tStrom L1 (A):\t\t\t "+str(int(obis_stroml1,16)/100)
                
                log(stroml1)
                mqttPublish("Smartmeter/StromL1",int(obis_stroml1,16)/100)


            # Strom L2 (A)
            # 0100330700ff
            obis_stroml2 = '0100330700ff'
            obis_stroml2_pos = databin.find(obis_stroml2)
            if obis_stroml2_pos > 1:
                obis_stroml2_anzzeichen = 4
                obis_stroml2 = databin[obis_stroml2_pos+obis_len+2:obis_stroml2_pos+obis_len+2+obis_stroml2_anzzeichen]
                stroml2 = "1.0.51.7.0.255\tStrom L2 (A):\t\t\t "+str(int(obis_stroml2,16)/100)
                
                log(stroml2)
                mqttPublish("Smartmeter/StromL2",int(obis_stroml2,16)/100)


            # Strom L3 (A)
            # 0100470700ff
            obis_stroml3 = '0100470700ff'
            obis_stroml3_pos = databin.find(obis_stroml3)
            if obis_stroml3_pos > 1:
                obis_stroml3_anzzeichen = 4
                obis_stroml3 = databin[obis_stroml3_pos+obis_len+2:obis_stroml3_pos+obis_len+2+obis_stroml3_anzzeichen]
                stroml3 = "1.0.71.7.0.255\tStrom L3 (A):\t\t\t "+str(int(obis_stroml3,16)/100)
                
                log(stroml3)
                mqttPublish("Smartmeter/StromL3",int(obis_stroml3,16)/100)


            # Wirkleistung Bezug +P (W)
            # 0100010700ff
            obis_wirkleistungbezug = '0100010700ff'
            obis_wirkleistungbezug_pos = databin.find(obis_wirkleistungbezug)
            if obis_wirkleistungbezug_pos > 1:
                obis_wirkleistungbezug_anzzeichen = 8
                obis_wirkleistungbezug = databin[obis_wirkleistungbezug_pos+obis_len+2:obis_wirkleistungbezug_pos+obis_len+2+obis_wirkleistungbezug_anzzeichen]
                wirkleistungbezug = "1.0.1.7.0.255\tWirkleistung Bezug [kW]:\t "+str(int(obis_wirkleistungbezug,16)/1000)
                
                log(wirkleistungbezug)
                mqttPublish("Smartmeter/MomentanleistungP",int(obis_wirkleistungbezug,16)/1000)


            # Wirkleistung Lieferung -P (W)
            # 0100020700ff
            obis_wirkleistunglieferung = '0100020700ff'
            obis_wirkleistunglieferung_pos = databin.find(obis_wirkleistunglieferung)
            if obis_wirkleistunglieferung_pos > 1:
                obis_wirkleistunglieferung_anzzeichen = 8
                obis_wirkleistunglieferung = databin[obis_wirkleistunglieferung_pos+obis_len+2:obis_wirkleistunglieferung_pos+obis_len+2+obis_wirkleistunglieferung_anzzeichen]
                wirkleistunglieferung = "1.0.2.7.0.255\tWirkleistung Lieferung [kW]:\t "+str(int(obis_wirkleistunglieferung,16)/1000)
                
                log(wirkleistunglieferung)
                mqttPublish("Smartmeter/MomentanleistungN",int(obis_wirkleistunglieferung,16)/1000)


            # Wirkenergie Bezug +A (Wh)
            # 0100010800ff
            obis_wirkenergiebezug = '0100010800ff'
            obis_wirkenergiebezug_pos = databin.find(obis_wirkenergiebezug)
            if obis_wirkenergiebezug_pos > 1:
                obis_wirkenergiebezug_anzzeichen = 8
                obis_wirkenergiebezug = databin[obis_wirkenergiebezug_pos+obis_len+2:obis_wirkenergiebezug_pos+obis_len+2+obis_wirkenergiebezug_anzzeichen]
                wirkenergiebezug = "1.0.1.8.0.255\tWirkenergie Bezug [kWh]:\t "+str(int(obis_wirkenergiebezug,16)/1000)
                
                log(wirkenergiebezug)
                mqttPublish("Smartmeter/WirkenergieP",int(obis_wirkenergiebezug,16)/1000)


            # Wirkenergie Lieferung -A (Wh)
            # 0100020800ff
            obis_wirkenergielieferung = '0100020800ff'
            obis_wirkenergielieferung_pos = databin.find(obis_wirkenergielieferung)
            if obis_wirkenergielieferung_pos > 1:
                obis_wirkenergielieferung_anzzeichen = 8
                obis_wirkenergielieferung = databin[obis_wirkenergielieferung_pos+obis_len+2:obis_wirkenergielieferung_pos+obis_len+2+obis_wirkenergielieferung_anzzeichen]
                wirkenergielieferung = "1.0.2.8.0.255\tWirkenergie Lieferung [kWh]:\t "+str(int(obis_wirkenergielieferung,16)/1000)
            
                log(wirkenergielieferung)
                mqttPublish("Smartmeter/WirkenergieN",int(obis_wirkenergielieferung,16)/1000)


            # Blindleistung Bezug +R (Wh)
            # 0100030800ff
            obis_blindleistungbezug = '0100030800ff'
            obis_blindleistungbezug_pos = databin.find(obis_blindleistungbezug)
            if obis_blindleistungbezug_pos > 1:
                obis_blindleistungbezug_anzzeichen = 8
                obis_blindleistungbezug = databin[obis_blindleistungbezug_pos+obis_len+2:obis_blindleistungbezug_pos+obis_len+2+obis_blindleistungbezug_anzzeichen]
                blindleistungbezug = "1.0.3.8.0.255\tBlindleistung Bezug [kW]:\t "+str(int(obis_blindleistungbezug,16)/1000)
                
                log(blindleistungbezug)
                mqttPublish("Smartmeter/BlindLeistungP",int(obis_blindleistungbezug,16)/1000)


            # Blindleistung Lieferung -R (Wh)
            # 0100040800ff
            obis_blindleistunglieferung = '0100040800ff'
            obis_blindleistunglieferung_pos = databin.find(obis_blindleistunglieferung)
            if obis_blindleistunglieferung_pos > 1:
                obis_blindleistunglieferung_anzzeichen = 8
                obis_blindleistunglieferung = databin[obis_blindleistunglieferung_pos+obis_len+2:obis_blindleistunglieferung_pos+obis_len+2+obis_blindleistunglieferung_anzzeichen]
                blindleistunglieferung = "1.0.4.8.0.255\tBlindleistung Lieferung [kW]:\t "+str(int(obis_blindleistunglieferung,16)/1000)
                
                log(blindleistunglieferung)
                mqttPublish("Smartmeter/BlindLeistungN",int(obis_blindleistunglieferung,16)/1000)

serial.close()

