'''
Script contenenti funzioni che operano sul db
'''
import os
from flask import send_file
from sqlalchemy import create_engine
from collections import defaultdict
from PIL import Image
from random import random, randint
from utils_func import crop, decode_idcrop, encode_idcrop, serve_pil_image
import io
import yaml

cfg = yaml.load(open('config.yaml', 'r'), Loader=yaml.BaseLoader)
dburl = cfg['dburl']

def insert_image_row_in_table(db, table, imageBD):
    qry = "INSERT INTO maymays.picture (photo) VALUES (%s)"
    with create_engine(dburl).begin() as conn:
        conn.execute(qry, (imageBD))

def insert_row_in_table(db, table, cols, values):
    qry = f"INSERT INTO {db}.{table} ({','.join(cols)}) VALUES ({','.join(values)})"
    print(qry)
    with create_engine(dburl).begin() as conn:
        conn.execute(qry)


def is_subscribed(email, dburl=dburl):
    qry = f"SELECT COUNT(*) FROM maymays.user WHERE email='{email}'"
    with create_engine(dburl).begin() as conn:
        res = conn.execute(qry).fetchall()[0][0]
        return True if res > 0 else False

def has_email(username, dburl=dburl):
    qry = f"SELECT email FROM maymays.user WHERE username = '{username}'"
    
    with create_engine(dburl).begin() as conn:
        res = conn.execute(qry).fetchall()[0][0]
        print(res)
        return True if res else False
        

def retrieve_user_id(email):
    qry = f"SELECT iduser FROM maymays.user WHERE email = '{email}'"
    with create_engine(dburl).begin() as conn:
        iduser = conn.execute(qry).fetchone()[0]

    return iduser

def retrieve_image(idpic):
    qry = f"SELECT photo FROM maymays.picture WHERE idpic={idpic}"
    with create_engine(dburl).begin() as conn:
        image_data = conn.execute(qry).fetchone()[0]
        
    image = Image.open(io.BytesIO(image_data))
    
    return image

def compute_and_update_user_score(user_id, dburl=dburl):
    qry_get_score = '''
    SELECT score
    FROM maymays.user as a
    WHERE a.iduser = '{}'
    '''
    qry_update_score = '''
    UPDATE maymays.user SET score = {} WHERE iduser = '{}'
    '''
    with create_engine(dburl).begin() as conn:
        score = conn.execute(qry_get_score.format(user_id)).fetchone()[0]
        print(f'score: {score+1}')
        conn.execute(qry_update_score.format(score+1, user_id))


def retrieve_image_for_user(iduser, dburl=dburl):
    '''
    Funzione che restituisce ad un dato utente un crop di un'immagine secondo requisiti
    '''
    # query che estrae la prima immagine con al più UN SOLO tag da parte dell'utente
    qry_image = '''
        SELECT pics.idpic
        FROM maymays.picture as pics
        LEFT JOIN
        (
        SELECT a.idpic, COUNT(DISTINCT a.idcrop) as num_crop
        FROM maymays.tag as a
        JOIN maymays.user as b
        ON a.iduser = b.iduser
        WHERE b.iduser = {}
        GROUP BY a.idpic
        ) as idpic_seen
        ON pics.idpic = idpic_seen.idpic
        WHERE idpic_seen.num_crop <= 1 OR idpic_seen.num_crop IS NULL
        ; 
    '''
    # query che raccoglie il crop già eseguito da un utente per una data immagine, se esistente
    # in modo da non riproporlo
    qry_crop = '''
    SELECT a.idcrop
    FROM maymays.tag as a
    JOIN maymays.user as b
    ON a.iduser = b.iduser
    WHERE b.iduser = {} and a.idpic = {}
    '''

    with create_engine(dburl).begin() as conn:
        # recupero l'id dell'immagine prescelta per l'utente
        res_idpic_col = conn.execute(qry_image.format(iduser)).fetchall()
        res_idpic = res_idpic_col[randint(0,len(res_idpic_col)-1)][0]
        # recupero l'eventuale UNICO crop già fatto
        crop_seen = conn.execute(qry_crop.format(iduser, res_idpic)).fetchone()

    # se c'è già questo crop, mi segno le coordinate di crop in modo da escluderle
    if crop_seen:
        ngridXFbd, ngridYFbd = decode_idcrop(crop_seen[0])
    else:
        ngridXFbd, ngridYFbd = None, None

    # recupero tramite id il blob come PIL.Image
    img_data = retrieve_image(res_idpic)
    # croppo l'immagine secondo requisiti e restituisco id del crop e PIL.Image del crop
    cropped_image, id_crop = crop(img_data, res_idpic, ngridXFbd, ngridYFbd)

    return cropped_image, id_crop, res_idpic


def retrieve_cropped_image(iduser):
    '''
    Funzione che per un dato utente recupera il crop 100X100 di un'immagine secondo requisiti, id dell'immagine e id del crop
    '''
    cropped_image, id_crop, idpic = retrieve_image_for_user(iduser)
    print(f"{idpic} {id_crop}")
    return send_file(
        serve_pil_image(cropped_image),
        mimetype='image/jpeg',
        as_attachment=True,
        attachment_filename=f'{idpic}_{id_crop}.jpg')