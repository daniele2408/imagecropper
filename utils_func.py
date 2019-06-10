from random import randint, choice
import io
from flask import send_file

def simulate_tag(email):
    '''
    Funzione per simulare i dati inviati con un tag
    '''
    X = randint(0,50)
    Y = randint(0,75)
    W = randint(10, 50)
    H = randint(5,25)
    tipotag = choice(["nice", "cool", "sad", "fun", "terrific"])
    id_crop = '_'.join([str(randint(1,6)), encode_idcrop(randint(0,9), randint(0,9))])


    diz = {'X':X, 'Y':Y, 'W':W, 'H':H, 'tipoTag':tipotag, 'id_crop':id_crop, 'email':email}
    diz = {k:str(v) for k,v in diz.items()}

    return diz
     

def wa(s, d):
    return d+str(s)+d


def encode_idcrop(x,y):
    return f"{x}_{y}"


def decode_idcrop(idcrop):
    return idcrop.split('_')


def crop(image_obj, idpic, ngridXForbidden, ngridYForbidden):
    '''
    Funzione che prende un crop a caso dei 100 possibili nella griglia 10x10, genera id e lo restituisce con l'immagine
    '''
    image_obj = image_obj.resize((1000, 1000))

    # finché almeno una coordinata della griglia è forbidden definisco un altro crop
    ngridX, ngridY = randint(0, 9), randint(0, 9)
    while ngridX == ngridXForbidden or ngridY == ngridYForbidden:
        ngridX, ngridY = randint(0, 9), randint(0, 9)

    x, y = ngridX * 100, ngridY * 100

#    print(f"img {idpic} - croppo {ngridX}, {ngridY}, {x}, {y}, + 100")

    cropped_image = image_obj.crop((x,y,x+100,y+100))


    id_crop = f"{ngridX}_{ngridY}"

    return cropped_image, id_crop



def serve_pil_image(pil_img):
    '''
    Funzione che trasforma l'immagine PIL in binario
    '''
    img_io = io.BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return img_io #send_file(img_io, mimetype='image/jpeg')