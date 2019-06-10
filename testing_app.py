import requests
import json
from utils_func import simulate_tag
from PIL import Image
import yaml
import pytest
import database
import time
import io
import pandas as pd
from sqlalchemy import create_engine

# pulisco il db e lo tiro su
database.drop_all()
database.initialize_db()

getNewImageUrl = 'http://127.0.0.1:5000/get_new_image/{}'
postTagUrl = 'http://127.0.0.1:5000/post_tagged_crop'
cfg = yaml.load(open('config.yaml', 'r'), Loader=yaml.BaseLoader)
dburl = cfg['dburl']


@pytest.mark.parametrize(
    'userid',
    [1,2,10]
)
def test_get_new_image(userid, show=False):
    '''
    Test per verificare che a getNewImage si risponda con un crop 100x100 con un certo id nel filename
    '''
    r = requests.get(url=getNewImageUrl.format(userid))
    print(r.headers)
    filename = r.headers['Content-Disposition']
    im = Image.open(io.BytesIO(r.content))
    if show:
        try:
            im.show()
        except Exception as err:
            assert False, f"Image non aperta, errore {err}"


    assert isinstance(r.content, bytes)
    assert im.size==(100,100)
    assert isinstance(filename, str)
    assert all(e.isdigit() for e in filename.split('=')[-1][:-4].split('_'))

@pytest.mark.parametrize(
    'email',
    [
        'daniele.cmp24@gmail.com',
        'email.maivista@prima.com'
    ]
)
def test_post_tag(email):
    '''
    Test per verificare che la post del tag sia corretta così come l'assegnazione dello score, per utenti nuovi e non
    '''
    payload = simulate_tag(email)

    print(simulate_tag)

    requests.post(url=postTagUrl, json=payload)

    qry_user = "SELECT * FROM maymays.user"
    qry_tag = f'''
    SELECT a.*, b.email
    FROM maymays.tag as a
    JOIN maymays.user as b
    ON a.iduser = b.iduser
    WHERE b.email = '{email}'
    '''

    with create_engine(dburl).begin() as conn:
        df_user = pd.read_sql(qry_user, conn)
        df_tag = pd.read_sql(qry_tag, conn)

    print(df_tag['tipotag'])

    assert (df_user[df_user.email==email]['score']>0).all()
    assert df_tag[df_tag.email==email]['coordsX'].tolist()[0]==int(payload['X'])
    #assert df_tag[df_tag.email==email]['tipotag']==payload['tipotag']
    assert df_tag[df_tag.email==email]['idpic'].tolist()[0]==int(payload['id_crop'].split('_')[0])

def test_requisito():
    email = 'foster.wallace@infinite.jest'

    payloadA = simulate_tag(email)
    payloadA['id_crop'] = '1_4_5'
    payloadB = simulate_tag(email)
    payloadB['id_crop'] = '1_3_4'

    requests.post(url=postTagUrl, json=payloadA)
    requests.post(url=postTagUrl, json=payloadB)

    for _ in range(100):
        r = requests.get(url=getNewImageUrl.format(2))

        idpic = r.headers['Content-Disposition'].split('=')[-1][:-4].split('_')[0]

        assert idpic != '1'
