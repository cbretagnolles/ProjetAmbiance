import threading
import time
from gpiozero import Button
from gpiozero import OutputDevice
import RPi.GPIO as GPIO
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
import logging
from waveshare_epd import epd7in5_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import requests
import base64
import json
if os.path.exists(libdir):
    sys.path.append(libdir)
import math
from waveshare_epd import epd7in5_V2
from PIL import Image,ImageDraw,ImageFont
import traceback
import requests
import base64
import json
import time
from projetdelambiance_functions import initparamgit
# Remplacez ces valeurs par les vôtres
GITHUB_TOKEN, REPO_OWNER, REPO_NAME, FILE_PATH, BRANCH = initparamgit()
rasp_master_id=0;#0=clément,1=antoine,2=samuel,3=hugo, 4=fail_wifi

# Verrou pour synchroniser l'accès à la variable partagée
data_lock = threading.Lock()

# Définition des boutons (brevet déposé)
output16 = OutputDevice(16)
output16.off()
output22 = OutputDevice(22)
output22.off()
output15 = OutputDevice(15)
output15.off()
output3 = OutputDevice(3)
output3.off()
output6 = OutputDevice(6)
output6.off()
output19 = OutputDevice(19)
output19.off()
button4 = Button(21)
button5 = Button(20)
button3 = Button(12, pull_up=True)
button1 = Button(4)
button2 = Button(27, pull_up=True)
button6 = Button(13)
button7 = Button(5)
button8 = Button(2)
button9 = Button(14)

# Init

valeur_bouton = 0
affichage = 0
affichage_courant = 9
classement = [0, 0, 0, 0]
valeur_bouton=0
affichage=9
affichage_courant=9
buttonmaster=rasp_master_id
lastupdate=0

def boucle_1s():
    global valeur_bouton
    global affichage
    global affichage_courant
    global buttonmaster
    global classement
    global lastupdate
    while True:
        start_time = time.time()
        with data_lock:
            if button1.is_pressed:
                valeur_bouton, affichage,affichage_courant = 1, 1, 1
                affichagebouton1(rasp_master_id)
            elif button2.is_pressed:
                valeur_bouton, affichage,affichage_courant = 2, 2, 2
                affichagebouton2(rasp_master_id)
            elif button3.is_pressed:
                valeur_bouton,affichage,affichage_courant  = 3, 3, 3
                affichagebouton3(rasp_master_id)
            elif button4.is_pressed:
                valeur_bouton,affichage,affichage_courant = 4, 4, 4
                affichagebouton4(rasp_master_id)
            elif button5.is_pressed:
                valeur_bouton,affichage,affichage_courant = 5, 5, 5
                affichagebouton5(rasp_master_id)
            elif button6.is_pressed:
                valeur_bouton,affichage,affichage_courant = 6, 6, 6
                affichagebouton6(rasp_master_id)
            elif button7.is_pressed:
                valeur_bouton,affichage,affichage_courant = 7, 7, 7
                affichagebouton7(rasp_master_id)
            elif button8.is_pressed:
                valeur_bouton,affichage,affichage_courant = 8, 8, 8
                affichagebouton8(rasp_master_id)
            elif button9.is_pressed:
                valeur_bouton,affichage,affichage_courant = 9, 9, 9
                affichagebouton9(buttonmaster, classement, lastupdate)
            elif affichage != affichage_courant or ((buttonmaster!=rasp_master_id) and valeur_bouton==0):
                affichage_courant = affichage
                if affichage == 1:
                    affichagebouton1(buttonmaster)
                elif affichage == 2:
                    affichagebouton2(buttonmaster)
                elif affichage == 3:
                    affichagebouton3(buttonmaster)
                elif affichage == 4:
                    affichagebouton4(buttonmaster)
                elif affichage == 5:
                    affichagebouton5(buttonmaster)
                elif affichage == 6:
                    affichagebouton6(buttonmaster)
                elif affichage == 7:
                    affichagebouton7(buttonmaster)
                elif affichage == 8:
                    affichagebouton8(buttonmaster)
                elif affichage == 9:
                    affichagebouton9(buttonmaster, classement, lastupdate)
        elapsed_time = time.time() - start_time
        time.sleep(max(0, 1 - elapsed_time))

def boucle_60s():
    global valeur_bouton
    global lastupdate
    global affichage
    global classement
    global buttonmaster
    global Erreur_lecture
    while True:
        start_time = time.time()
        with data_lock:
            if valeur_bouton != 0:
                try:
                    sha, valeur_bouton_online, classement_online, buttonmaster_online, lastupdate_online = get_file_content()
                    if valeur_bouton_online != -1:
                        valeur_bouton_update = valeur_bouton
                        buttonmaster_update = rasp_master_id # ##a completer  #0=clement, 1=antoine, 2=samuel, 3=hugo
                        classement = classement_online
                        lastupdate_update = time.time()
                        classement[buttonmaster_online] += int(lastupdate_update - lastupdate_online)
                        classement_update = classement
                        update_file_content(valeur_bouton_update, classement_update, buttonmaster_update, lastupdate_update, sha)
                    valeur_bouton = 0
                except Exception as e:
                    print('Erreur envoi')
                    valeur_bouton = 0
            else:
                try:
                    sha, valeur_bouton_online, classement_online, buttonmaster_online, lastupdate_online = get_file_content()
                    if valeur_bouton_online != -1:
                        affichage = valeur_bouton_online
                        buttonmaster = buttonmaster_online
                        classement = classement_online
                        lastupdate = lastupdate_online
                        #('maj classement')
                        valeur_bouton = 0
                except Exception as e:
                    print('Erreur lecture')
                    buttonmaster = 4
        elapsed_time = time.time() - start_time
        time.sleep(max(0, 60 - elapsed_time))

def indices_liste_triee(lst):
    # Crée une liste de tuples (index, valeur)
    indexed_lst = list(enumerate(lst))
    
    # Trie la liste de tuples en fonction des valeurs
    indexed_lst.sort(key=lambda x: x[1])
    
    # Extrait et renvoie les indices de la liste triée
    sorted_indices = [index for index, value in indexed_lst]
    
    return sorted_indices
    
def affichagebouton1(ButtonMaster):
    master=["Clément","Antoine","Hugo","Samuel","WIFI ERR"]
    logging.basicConfig(level=logging.DEBUG)
    try:
        #logging.info("epd7in5_V2 Demo")
        epd = epd7in5_V2.EPD()
        #logging.info("init and Clear")
        epd.init()
        epd.Clear()
        #font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        #font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
        #logging.info("read bmp file")
        Himage = Image.open(os.path.join("/home/pi/UnifiedDisplay/ProjetAmbiance/", 'image1.bmp'))
        draw = ImageDraw.Draw(Himage)
        font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        draw.rectangle((10, 10, 110, 40), fill = 255)
        draw.text((10, 10), master[ButtonMaster], font = font24, fill = 0)
        epd.display(epd.getbuffer(Himage.rotate(180)))
        #logging.info("Goto Sleep...")
        epd.sleep()
    except IOError as e:
        logging.info(e)

def affichagebouton2(ButtonMaster):
    master=["Clément","Antoine","Hugo","Samuel","WIFI ERR"]
    logging.basicConfig(level=logging.DEBUG)
    try:
        #logging.info("epd7in5_V2 Demo")
        epd = epd7in5_V2.EPD()
        #logging.info("init and Clear")
        epd.init()
        epd.Clear()
        #logging.info("read bmp file")
        Himage = Image.open(os.path.join("/home/pi/UnifiedDisplay/ProjetAmbiance/", 'image2.bmp'))
        draw = ImageDraw.Draw(Himage)
        font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        draw.rectangle((10, 10, 110, 40), fill = 255)
        draw.text((10, 10), master[ButtonMaster], font = font24, fill = 0)
        epd.display(epd.getbuffer(Himage.rotate(180)))
        ##logging.info("Clear...")
        #epd.init()
        #epd.Clear()
        #logging.info("Goto Sleep...")
        epd.sleep()
        
    except IOError as e:
        logging.info(e)


def affichagebouton3(ButtonMaster):
    master=["Clément","Antoine","Hugo","Samuel","WIFI ERR"]
    #logging.basicConfig(level=logging.DEBUG)
    try:
        #logging.info("epd7in5_V2 Demo")
        epd = epd7in5_V2.EPD()
        #logging.info("init and Clear")
        epd.init()
        epd.Clear()
        #logging.info("read bmp file")
        Himage = Image.open(os.path.join("/home/pi/UnifiedDisplay/ProjetAmbiance/", 'image3.bmp'))
        draw = ImageDraw.Draw(Himage)
        font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        draw.rectangle((10, 10, 110, 40), fill = 255)
        draw.text((10, 10), master[ButtonMaster], font = font24, fill = 0)
        epd.display(epd.getbuffer(Himage.rotate(180)))
        ##logging.info("Clear...")
        #epd.init()
        #epd.Clear()
        #logging.info("Goto Sleep...")
        epd.sleep()
        
    except IOError as e:
        logging.info(e)
        
def affichagebouton4(ButtonMaster):
    master=["Clément","Antoine","Hugo","Samuel","WIFI ERR"]
    #logging.basicConfig(level=logging.DEBUG)
    try:
        #logging.info("epd7in5_V2 Demo")
        epd = epd7in5_V2.EPD()
        #logging.info("init and Clear")
        epd.init()
        epd.Clear()
        #logging.info("read bmp file")
        Himage = Image.open(os.path.join("/home/pi/UnifiedDisplay/ProjetAmbiance/", 'image4.bmp'))
        draw = ImageDraw.Draw(Himage)
        font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        draw.rectangle((10, 10, 110, 40), fill = 255)
        draw.text((10, 10), master[ButtonMaster], font = font24, fill = 0)
        epd.display(epd.getbuffer(Himage.rotate(180)))
        ##logging.info("Clear...")
        #epd.init()
        #epd.Clear()
        #logging.info("Goto Sleep...")
        epd.sleep()
        
    except IOError as e:
        logging.info(e)

def affichagebouton5(ButtonMaster):
    master=["Clément","Antoine","Hugo","Samuel","WIFI ERR"]
    #logging.basicConfig(level=logging.DEBUG)
    try:
        #logging.info("epd7in5_V2 Demo")
        epd = epd7in5_V2.EPD()
        #logging.info("init and Clear")
        epd.init()
        epd.Clear()
        #logging.info("read bmp file")
        Himage = Image.open(os.path.join("/home/pi/UnifiedDisplay/ProjetAmbiance/", 'image5.bmp'))
        draw = ImageDraw.Draw(Himage)
        font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        draw.rectangle((10, 10, 110, 40), fill = 255)
        draw.text((10, 10), master[ButtonMaster], font = font24, fill = 0)
        epd.display(epd.getbuffer(Himage.rotate(180)))
        ##logging.info("Clear...")
        #epd.init()
        #epd.Clear()
        #logging.info("Goto Sleep...")
        epd.sleep()
        
    except IOError as e:
        logging.info(e)

def affichagebouton6(ButtonMaster):
    master=["Clément","Antoine","Hugo","Samuel","WIFI ERR"]
    #logging.basicConfig(level=logging.DEBUG)
    try:
        #logging.info("epd7in5_V2 Demo")
        epd = epd7in5_V2.EPD()
        #logging.info("init and Clear")
        epd.init()
        epd.Clear()
        #logging.info("read bmp file")
        Himage = Image.open(os.path.join("/home/pi/UnifiedDisplay/ProjetAmbiance/", 'image6.bmp'))
        draw = ImageDraw.Draw(Himage)
        font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        draw.rectangle((10, 10, 110, 40), fill = 255)
        draw.text((10, 10), master[ButtonMaster], font = font24, fill = 0)
        epd.display(epd.getbuffer(Himage.rotate(180)))
        ##logging.info("Clear...")
        #epd.init()
        #epd.Clear()
        #logging.info("Goto Sleep...")
        epd.sleep()
        
    except IOError as e:
        logging.info(e)
        


def affichagebouton7(ButtonMaster):
    master=["Clément","Antoine","Hugo","Samuel","WIFI ERR"]
    #logging.basicConfig(level=logging.DEBUG)
    try:
        #logging.info("epd7in5_V2 Demo")
        epd = epd7in5_V2.EPD()
        #logging.info("init and Clear")
        epd.init()
        epd.Clear()
        #logging.info("read bmp file")
        Himage = Image.open(os.path.join("/home/pi/UnifiedDisplay/ProjetAmbiance/", 'image7.bmp'))
        draw = ImageDraw.Draw(Himage)
        font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        draw.rectangle((10, 10, 110, 40), fill = 255)
        draw.text((10, 10), master[ButtonMaster], font = font24, fill = 0)
        epd.display(epd.getbuffer(Himage.rotate(180)))
        ##logging.info("Clear...")
        #epd.init()
        #epd.Clear()
        #logging.info("Goto Sleep...")
        epd.sleep()
        
    except IOError as e:
        logging.info(e)
        


def affichagebouton8(ButtonMaster):
    master=["Clément","Antoine","Hugo","Samuel","WIFI ERR"]
    #logging.basicConfig(level=logging.DEBUG)
    try:
        #logging.info("epd7in5_V2 Demo")
        epd = epd7in5_V2.EPD()
        #logging.info("init and Clear")
        epd.init()
        epd.Clear()
        #logging.info("read bmp file")
        Himage = Image.open(os.path.join("/home/pi/UnifiedDisplay/ProjetAmbiance/", 'image8.bmp'))
        draw = ImageDraw.Draw(Himage)
        font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        draw.rectangle((10, 10, 110, 40), fill = 255)
        draw.text((10, 10), master[ButtonMaster], font = font24, fill = 0)
        epd.display(epd.getbuffer(Himage.rotate(180)))
        ##logging.info("Clear...")
        #epd.init()
        #epd.Clear()
        #logging.info("Goto Sleep...")
        epd.sleep()
        
    except IOError as e:
        logging.info(e)
        


def affichagebouton9(buttonmaster, classement, lastupdate):
    master=["Clément","Antoine","Hugo","Samuel","WIFI ERR"]
    #logging.basicConfig(level=logging.DEBUG)
    try:
        #logging.info("epd7in5_V2 Demo")
        epd = epd7in5_V2.EPD()
        #logging.info("init and Clear")
        epd.init()
        epd.Clear()
        #logging.info("read bmp file")
        Himage = Image.open(os.path.join("/home/pi/UnifiedDisplay/ProjetAmbiance/", 'image9.bmp'))
        draw = ImageDraw.Draw(Himage)
        font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
        draw.rectangle((10, 10, 110, 40), fill = 255)
        draw.text((10, 10), master[buttonmaster], font = font24, fill = 0)
        indice_classement = indices_liste_triee(classement)
        draw.text((204, 30), master[indice_classement[3]]+" : \n"+str(int(classement[indice_classement[3]]/86400))+"j "+str(int(((classement[indice_classement[3]]/86400)-math.floor(classement[indice_classement[3]]/86400))*24))+"h "+str(int(((classement[indice_classement[3]]/3600)-math.floor(classement[indice_classement[3]]/3600))*60))+"min\nGAFAM du\nbouton", font = font18, fill = 0)
        draw.text((21, 105), master[indice_classement[2]]+" : \n"+str(int(classement[indice_classement[2]]/86400))+"j "+str(int(((classement[indice_classement[2]]/86400)-math.floor(classement[indice_classement[2]]/86400))*24))+"h "+str(int(((classement[indice_classement[2]]/3600)-math.floor(classement[indice_classement[2]]/3600))*60))+"min\nJeune licorne\ndu NASDAQ", font = font18, fill = 0)
        draw.text((377, 111), master[indice_classement[1]]+" : \n"+str(int(classement[indice_classement[1]]/86400))+"j "+str(int(((classement[indice_classement[1]]/86400)-math.floor(classement[indice_classement[1]]/86400))*24))+"h "+str(int(((classement[indice_classement[1]]/3600)-math.floor(classement[indice_classement[1]]/3600))*60))+"min\nDirection l'IOT\nValley", font = font18, fill = 0)
        draw.text((486, 229), master[indice_classement[0]]+" : \n"+str(int(classement[indice_classement[0]]/86400))+"j "+str(int(((classement[indice_classement[0]]/86400)-math.floor(classement[indice_classement[0]]/86400))*24))+"h "+str(int(((classement[indice_classement[0]]/3600)-math.floor(classement[indice_classement[0]]/3600))*60))+"min\nStartup qui pue\nla merde", font = font18, fill = 0)
        epd.display(epd.getbuffer(Himage.rotate(180)))
        ##logging.info("Clear...")
        #epd.init()
        #epd.Clear()
        #logging.info("Goto Sleep...")
        epd.sleep()
        
    except IOError as e:
        logging.info(e)
        
        


def encode_to_string(entier1, liste_entiers, entier2, entier3):
    # Vérification que la liste contient bien 4 entiers
    if len(liste_entiers) != 4:
        raise ValueError("La liste doit contenir exactement 4 entiers.")
    
    # Conversion des éléments en chaîne de caractères
    elements = [str(int(entier1))] + [str(int(i)) for i in liste_entiers] + [str(int(entier2)), str(int(entier3))]
    
    # Création d'une chaîne unique en joignant les éléments avec un séparateur
    chaine = ','.join(elements)
    return chaine

def decode_from_string(chaine):
    # Séparation de la chaîne en éléments individuels
    elements = chaine.split(',')
    
    # Extraction et conversion des éléments en entiers
    entier1 = int(elements[0])
    liste_entiers = [int(i) for i in elements[1:5]]
    entier2 = int(elements[5])
    entier3 = int(elements[6])
    
    return entier1, liste_entiers, entier2, entier3


def  get_file_content():
    valeur_bouton_online = -1
    classement_online = [-1,-1,-1,-1]
    buttonmaster_online = -1
    lastupdate_online = -1
    file_content=None
    sha=None
    try:
        url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}?ref={BRANCH}'
        headers = {'Authorization': f'token {GITHUB_TOKEN}'}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            content = response.json()
            file_content = base64.b64decode(content['content']).decode('utf-8')
            valeur_bouton_online,classement_online,buttonmaster_online,lastupdate_online=decode_from_string(file_content)
            sha = content['sha']
            return sha,valeur_bouton_online,classement_online,buttonmaster_online,lastupdate_online
        else:
            print('Erreur lors de la récupération du fichier:', response.status_code, response.json())
            return sha,valeur_bouton_online,classement_online,buttonmaster_online,lastupdate_online
    except Exception as e:
        return sha,valeur_bouton_online,classement_online,buttonmaster_online,lastupdate_online

def update_file_content(valeur_bouton_update,classement_update,buttonmaster_update,lastupdate_update, sha):
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    new_content=encode_to_string(valeur_bouton_update,classement_update,buttonmaster_update,lastupdate_update)
    data = {
        'message': 'Update value from cléménet',##commentaire à changer
        'content': base64.b64encode(new_content.encode('utf-8')).decode('utf-8'),
        'sha': sha,
        'branch': BRANCH
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200 or response.status_code == 201:
        #print('Fichier mis à jour avec succès.')
    else:
        print('Erreur lors de la mise à jour du fichier:', response.status_code, response.json())



producer_thread = threading.Thread(target=boucle_1s)
consumer_thread = threading.Thread(target=boucle_60s)
producer_thread.start()
consumer_thread.start()
producer_thread.join()
consumer_thread.join()
