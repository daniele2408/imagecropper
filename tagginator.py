'''
Punti in sospeso:
* le info del tag vanno inserite nel db, con la MAIL
la mail non c'è già in tabella? se devo inserirla, la trova nel body della POST del tag?
* per ogni chiamata il front end invia una mail che identifica l'utente che usa il sistema
Quale chiamata? quando c'è un tag? a chi l'invia? all'admin?
* crea l'utente se non esiste la mail, altrimenti aumenta lo score per ogni tag
Quindi il primo tag niente score? Se non esiste la mail da che fonte la prendo la mail?
Forse non devo prenderla, però quindi aggiungo username senza mail, e non avranno score finché non ci sarà la mail?
'''
from datetime import datetime
from flask import Flask, jsonify, request, Response
import db_funcs as dbf
from random import choice, randint
import json
from utils_func import wa

app = Flask(__name__)


@app.route('/get_new_image/<int:iduser>', methods=['GET'])
def fetch_cropped_image(iduser):
    '''
    Richiesta di un'immagine da un utente, invia al front un crop 100X100. Per ora l'idcrop è nel filename
    '''
    res = dbf.retrieve_cropped_image(iduser)
    return res 


@app.route('/post_tagged_crop', methods=['POST'])
def get_tagged_crop():
    '''
    Funzione che gestisce un tag di un utente
    '''

    diz = json.loads(request.data)
    print(diz)
    id_crop_unico = diz['id_crop']
    X, Y, W, H = diz['X'], diz['Y'], diz['W'], diz['H']
    tipoTag = diz['tipoTag']
    timestamp = datetime.now()
    email = diz['email']
    # recuperiamo lo user id, se non esiste prima creiamo l'utente
    if dbf.is_subscribed(email):
        iduser = dbf.retrieve_user_id((email))
        # a patto che abbia la mail, aumentiamo lo score
        # if dbf.has_email(username): 
        dbf.compute_and_update_user_score(iduser)
    else:
        dbf.insert_row_in_table('maymays', 'user', ('email', 'score'), (wa(email, "'"), '1'))
        iduser = dbf.retrieve_user_id(email)


    idpic = id_crop_unico[:id_crop_unico.index('_')]
    idcrop = id_crop_unico[id_crop_unico.index('_')+1:]
    dbf.insert_row_in_table(
        'maymays',
        'tag',
        ('iduser', 'timestamp', 'coordsX', 'coordsY', 'coordsW', 'coordsH', 'tipotag', 'idpic', 'idcrop'),
        (str(iduser), wa(timestamp.strftime(format="%Y-%m-%d %H:%M:%S"), "'"), X, Y, W, H, wa(tipoTag, "'"), wa(idpic, "'"), wa(idcrop,"'"))
        )


    return Response("{'Crop caricato'}", status=201)
