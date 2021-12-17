from sqlalchemy.sql import base, expression
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy import create_engine, engine
from sqlalchemy.inspection import inspect
from sqlalchemy import Column, String, Integer, Date, and_, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import UniqueConstraint  
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from uuid import uuid4
import os 
import datetime
import psycopg2
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())



 




def connectionDB():
    
    db_string = os.getenv('DB_PASS')

    engine = create_engine(db_string) 

    
    base = declarative_base()

    class soundspotEmails(base):
        __tablename__ = 'soundspotEmails'

        id = Column(Integer, primary_key=True, autoincrement=True)
        cdt = Column(DateTime, default=datetime.datetime.now())
        Email = Column(String, nullable=False)
        uuid = Column(String, nullable=False)
        EmailStatus = Column(Integer, nullable=True, default=0)

        __table_args__ = (UniqueConstraint('Email', name='Email',), )

    insp = inspect(engine)
    if not insp.has_table('soundspotEmails', schema=None):
        base.metadata.create_all(engine)

    Session = sessionmaker(engine, autoflush=False)  
    session = Session()
    print('DB connection Done !!!')

    return [soundspotEmails, session]

def sendEmails(ToEmail, token):
    try:
        print('email start sent')
        msg = MIMEMultipart('alterbative')
        msg['Subject'] = "SoundSpot Email Verification"
        msg['From'] = 'soundspotnoreply@gmail.com'
        msg['To'] = ToEmail


        html = open("email.html", encoding="utf8")
        html2 = html.read().replace("{{Name}}", str('Listener')).replace("{{token}}", str(token))

        
        msg.attach(MIMEText(html2, 'html', "utf-8"))
        print('email will sent')
        
        s = smtplib.SMTP('smtp.gmail.com',587)
        s.starttls()
        s.login('soundspotnoreply@gmail.com', os.getenv('GMAIL_STMP'))
        s.sendmail('soundspotnoreply@gmail.com', ToEmail, msg.as_string())
        s.quit()
        return True
    except Exception as er:
        print(er)
        return False

# sendEmails()

def emailExistence(email,soundspotEmails, session):
    email = session.query(soundspotEmails).filter(and_(
                            soundspotEmails.Email == str(email),
                            )).first()
    
    return True if email != None else False


def insertRecoards(email, uuid, session,soundspotEmails):
    try:
        record = soundspotEmails(
                    Email = email,
                    uuid = uuid,
                    )
        session.add(record)
    except Exception as er:
        print(er)

def main(email):
    soundspotEmails, session = connectionDB()
    
    uuid = uuid4()
    if not emailExistence(email, soundspotEmails, session):
        print('send email and insert')
        if sendEmails(email, uuid):
            print('inserting')
            insertRecoards(email, uuid, session, soundspotEmails)
    else:
        # Email already exists 
        print('email already exists')


    

    session.commit()
    session.close()

main('wahbi.jed.2013@gmail.com')



