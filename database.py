'''
Script per inizializzare il database. Crea tre tabelle:

* realpics, dove sono le foto sotto forma di blob e relativo id
* users, dove sono gli utenti con username, email, score
* tags, dove ci sono i singole tag (timestampati) degli utenti

Inoltre inserisce due utenti già presenti
'''

import os
from sqlalchemy import create_engine
import yaml
from db_funcs import insert_image_row_in_table, insert_row_in_table

cfg = yaml.load(open('config.yaml'), Loader=yaml.BaseLoader)
dburl = cfg['dburl']

def convertToBinaryData(filename):
    with open(filename, 'rb') as f:
        binaryData = f.read()
    return binaryData

def drop_all():
    with create_engine(dburl).begin() as conn:
        conn.execute('SET FOREIGN_KEY_CHECKS = 0')
        for t in ['user', 'picture', 'tag']:
            conn.execute(f"DROP TABLE IF EXISTS {t}")
        conn.execute('SET FOREIGN_KEY_CHECKS = 1')

def initialize_db():
    qry_create_pics = '''
    CREATE TABLE IF NOT EXISTS maymays.picture (
        idpic INTEGER UNSIGNED NOT NULL AUTO_INCREMENT,
        photo LONGBLOB NOT NULL,
        PRIMARY KEY (idpic)
    )
    '''

    qry_create_users = '''
    CREATE TABLE IF NOT EXISTS maymays.user (
        iduser INTEGER UNSIGNED NOT NULL AUTO_INCREMENT,
        email VARCHAR(255) UNIQUE NOT NULL,
        score SMALLINT,
        PRIMARY KEY (iduser)
    )
    '''
    
    qry_create_tags = '''
    CREATE TABLE IF NOT EXISTS maymays.tag (
        iduser INTEGER UNSIGNED NOT NULL,
        timestamp TIMESTAMP,
        coordsX SMALLINT,
        coordsY SMALLINT,
        coordsW SMALLINT,
        coordsH SMALLINT,
        tipotag VARCHAR(255),
        idpic INTEGER UNSIGNED NOT NULL,
        idcrop VARCHAR(25),
        CONSTRAINT idpic FOREIGN KEY (idpic)
            REFERENCES maymays.picture(idpic),
        CONSTRAINT iduser FOREIGN KEY (iduser)
            REFERENCES maymays.user(iduser)
    )
    '''

    for qry_create in [qry_create_pics, qry_create_users, qry_create_tags]:
        with create_engine(dburl).begin() as conn:
            conn.execute(qry_create)

    
    imgFolder = r'C:\Users\Daniele\progetti\python\esercizio3bee\data_img'

    for f in os.listdir(imgFolder):
        imageFilepath = os.path.join(imgFolder, f).replace('\\', '\\\\')
        imageBD = convertToBinaryData(imageFilepath)
        insert_image_row_in_table('maymays', 'picture', imageBD)

    for email in [("'daniele.cmp24@gmail.com'"), ("'foster.wallace@infinite.jest'")]:
        insert_row_in_table('maymays', 'user', ['email', 'score'], (email, '0'))

if __name__ == '__main__':
    drop_all()
    initialize_db()