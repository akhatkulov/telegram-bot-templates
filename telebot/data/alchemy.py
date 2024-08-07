from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, BigInteger, func,VARCHAR,desc
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from conf import DB_URL
engine = create_engine(DB_URL)
Base = declarative_base()

class User(Base):
    __tablename__ = 'user_ball'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cid = Column(BigInteger, unique=True)
    step = Column(VARCHAR(25), default=0)
    ball = Column(Integer)
    name = Column(String)
    phone = Column(String)



class Channels(Base):
    __tablename__ = 'channels_ball'
    id = Column(Integer, primary_key=True, autoincrement=True)
    link = Column(String, default="None", unique=True)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def get_all_user():
    try:
        x = session.query(User.cid).all()
        res = [i[0] for i in x]
        return res
    finally:
        session.close()

def user_count():
    try:
        x = session.query(func.count(User.id)).first()
        return x[0]
    finally:
        session.close()

def create_user(cid,name):
    try:
        user = User(cid=int(cid), step="0", ball=0,name=name,phone="*")
        session.add(user)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()


def get_members():
    try:
        x = session.query(User).where(User.cid >= 0).all()
        return x
    finally:
        session.close()
 


def get_step(cid):
    try:
        x = session.query(User).filter_by(cid=cid).first()
        return x.step if x else None
    finally:
        session.close()

def put_step(cid, step):
    try:
        x = session.query(User).filter_by(cid=cid).first()
        if x:
            x.step = str(step)
            session.commit()
            return True
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {e}")
        return False


def put_channel(channel: str):
    try:
        x = Channels(link=channel)
        session.add(x)
        session.commit()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {e}")
        return False

def get_channel():
    try:
        x = session.query(Channels).all()
        res = [i.link for i in x]
        return res
    finally:
        session.close()

def get_channel_with_id():
    try:
        x = session.query(Channels).all()
        res = ""
        for channel in x:
            res += f"\nID: {channel.id} \nLink: @{channel.link}"
        return res
    finally:
        session.close()

def delete_channel(ch_id):
    try:
        x = session.query(Channels).filter_by(id=int(ch_id)).first()
        if x:
            session.delete(x)
            session.commit()
            return True
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {e}")
        return False
