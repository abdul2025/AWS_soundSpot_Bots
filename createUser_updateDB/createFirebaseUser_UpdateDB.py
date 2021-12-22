from sqlalchemy.sql import base, expression
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy import create_engine, engine
from sqlalchemy.inspection import inspect
from sqlalchemy import Column, String, Integer, Date, and_, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import UniqueConstraint  
import datetime
import psycopg2
import json
import requests
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())



def connectionDB():
    
    db_string =  os.getenv('DB_PASS')

    engine = create_engine(db_string) 

    
    base = declarative_base()

    class soundspotEmails(base):
        __tablename__ = 'SoundSpotUsers'

        id = Column(Integer, primary_key=True, autoincrement=True)
        cdt = Column(DateTime, default=datetime.datetime.now())
        Email = Column(String, nullable=False)
        Password = Column(String, nullable=False)
        FireBaseUID = Column(String, nullable=True)
        uuid = Column(String, nullable=False)
        EmailStatus = Column(Integer, nullable=True, default=0)

        __table_args__ = (UniqueConstraint('Email', name='Email',), )

    insp = inspect(engine)
    if not insp.has_table('SoundSpotUsers', schema=None):
        base.metadata.create_all(engine)

    Session = sessionmaker(engine, autoflush=False)  
    session = Session()
    print('DB connection Done !!!')

    return [soundspotEmails, session]


def firebaseCreateUser(email, password):
    try:
        data = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        url = 'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=' + os.getenv('FIREBASE_KEY')
        data_json = json.dumps(data)
        headers = {'Content-type': 'application/json'}

        response = requests.post(url, data=data_json, headers=headers)
        res = json.loads(response.text)
        # print(res['error']['code'])
        if response.status_code != 200:
            return res['error']['message']
        if res['localId']:
            return [res['localId']]
        
    except Exception as er:
        return er
print(firebaseCreateUser('abduslf.2020alsh@gmail.com', '123123'))

def main(token):
    soundspotEmails, session = connectionDB()
    # check if the records has passed 24 hours
    user = session.query(soundspotEmails).filter(and_(
                        soundspotEmails.EmailStatus == 0,
                        soundspotEmails.uuid == token,
                        )).first()
    if user != None:
        print('updating')
        message = firebaseCreateUser(user.Email, user.Password)
        if type(message) == str:
            return message
        else:
            user.EmailStatus = 1
            user.FireBaseUID = message[0]
            message = 'Verified Successfully, Please login'

    else:
        # record already exists 
        message = 'User Already Verified, Please login'


    

    session.commit()
    session.close()
    return message


    




