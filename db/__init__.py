from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.elements import Null
from sqlalchemy.sql.functions import user
from sqlalchemy.sql.sqltypes import DateTime
from datetime import datetime
# NOTE: Eliminar al llevar a productivo <--
from sqlalchemy.event import listen
from sqlalchemy import event, DDL
# -->

DATABASE_URI = 'sqlite:///db/production.db'
Base = declarative_base()

class Entry(Base):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key = True)
    user_id = Column(Integer)
    entry_name = Column(String(200))
    tickets = Column(Integer)
    view_date = Column(DateTime)

    def __repr__(self):
        return "user_id:{} entry_name:{} tickets{}".format(
                'user_id',
                'entry_name',
                'tickets',
                'view_date'
                )


# NOTE: Eliminar al llevar a productivo <--
@event.listens_for(Entry.__table__, 'after_create')
def insert_initial_values(*args, **kwargs):
    session = Session()
    session.commit()
    session.close()
# -->

engine = create_engine(DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def get_all_entries():
    session = Session()
    entries = session.query(Entry).all()
    session.close()
    return entries


def get_entry_from_name(new_entry_name:str):
    session = Session()
    entry = session.query(Entry).filter(
            Entry.entry_name.ilike("%{}%".format(new_entry_name))
            ).one_or_none()
    session.close()
    return entry


def get_entry_from_user(user_id):
    session = Session()
    entry = session.query(Entry).filter(
            Entry.user_id == user_id
            ).one_or_none()
    session.close()
    return entry


def get_entries_from_user(user_id):
    session = Session()
    entries = session.query(Entry).filter(
            Entry.user_id == user_id
            ).all()
    session.close()
    return entries


def get_not_viewed_entries():
    session = Session()
    entries = session.query(Entry).filter(Entry.view_date == None).all()
    session.close()
    return entries


def get_viewed_entries():
    session = Session()
    entries = session.query(Entry).filter(Entry.view_date != None).all()
    session.close()
    return entries


def add_entry(user_id, entry_name, tickets=1):
    session = Session()
    entry = Entry(user_id=user_id, entry_name=entry_name, tickets=tickets)
    session.add(entry)
    session.commit()
    session.close()


def remove_entry(entry):
    session = Session()
    session.delete(entry)
    session.commit()
    session.close()


def set_date_to_entry(entry_name, new_date):
    session = Session()
    entry = get_entry_from_name(entry_name)
    if new_date == Null:
        entry.view_date = datetime.now()
    else:
        entry.view_date = datetime.strptime(new_date, "%d-%m-%Y").date()
    session.add(entry)
    session.commit()
    session.close()


def change_user_id_to_entry(entry_name, user_id):
    session = Session()
    entry = get_entry_from_name(entry_name)
    entry.user_id = user_id
    session.add(entry)
    session.commit()
    session.close()


def increment_tickets():
    session = Session()
    for entry in session.query(Entry):
        if entry.tickets < 5:
            entry.tickets += 1
    session.commit()
    session.close()


def get_5_ticks():
    session = Session()
    entries = session.query(Entry).filter_by(tickets=5).all()
    session.close()
    return entries
