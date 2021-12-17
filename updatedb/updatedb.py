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
import os
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




def main(email = 'wahbi.jed.2013@gmail.com', uuid = 'd71e5924-e7d1-4634-a03d-28e96056a083'):
    soundspotEmails, session = connectionDB()
    # check if the records has passed 24 hours
    user = session.query(soundspotEmails).filter(and_(
                        soundspotEmails.Email == str(email),
                        soundspotEmails.EmailStatus == 0,
                        soundspotEmails.uuid == uuid,
                        )).first()

    if user != None:
        print('updating')
        user.EmailStatus = 1
    else:
        # record already exists 
        print('records already updated')
        return 0


    

    session.commit()
    session.close()

    return 1

main()



