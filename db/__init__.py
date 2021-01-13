from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URI = 'sqlite:///:memory:'
Base = declarative_base()

class Entry(Base):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key = True)
    user_id = Column(Integer)
    entry_name = Column(String(200))
    tickets = Column(Integer)

    def __repr__(self):
        return "user_id:{} entry_name:{} tickets{}".format(
                user_id,
                entry_name,
                tickets
                )

engine = create_engine(DATABASE_URI, echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def remove_entry(entry):
    session = Session()
    session.delete(entry)
    session.commit()
    session.close()


def add_entry(user_id, entry_name):
    session = Session()
    entry = Entry(user_id=user_id, entry_name=entry_name, tickets=1)
    session.add(entry)
    session.commit()
    session.close()


def get_all_entries():
    session = Session()
    entries = session.query(Entry).all()
    session.close()
    return entries


def get_entry_from_name(entry_name):
    session = Session()
    entry = session.query(Entry).filter(Entry.entry_name == entry_name).one_or_none()
    session.close()
    return entry


def get_entry_from_user(user_id):
    session = Session()
    entry = session.query(Entry).filter(Entry.user_id == user_id).one_or_none()
    session.close()
    return entry


def increment_tickets():
    session = Session()
    for entry in session.query(Entry):
        if entry.tickets != 5:
            entry.tickets += 1
    session.commit()
    session.close()


