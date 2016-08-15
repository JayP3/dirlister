import os
from dirlister import scanwalk
from sqlalchemy import Column, Integer, Float, String, create_engine, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

try:
    os.unlink('test.db')
except:
    pass

Base = declarative_base()

class DirListing(Base):
    __tablename__ = 'dir_listing'
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255))
    filepath = Column(String(255))

    size = Column(BigInteger)
    last_modified = Column(Float)
    last_accessed = Column(Float)
    create_time = Column(Float)

    @classmethod
    def from_dir_entry(cls, dent):
        stat = dent.stat()
        ob = cls(filename=dent.name,
                 filepath=os.path.dirname(os.path.abspath(dent.path)),
                 size=stat.st_size,
                 last_modified=stat.st_mtime,
                 last_accessed=stat.st_atime,
                 create_time=stat.st_ctime)
        return ob

# os.system('cls')
# engine = create_engine('mysql+pymysql://pradmin:detpuzz8@localhost/dirscan')
engine = create_engine('sqlite:///test.db')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

counter = 0
for root, subs, files in scanwalk.scantree('C:\\Users\\Jay\\Desktop'):
    # print('Dir Entry dir listing:\n', dir(root), '\n')
    # print('Stat object dir listing:\n', type(root.stat()),
    #       '\n', dir(root.stat()), '\n')
    # print('Stat Fields:\n', root.stat().n_fields, '\n')
    for s in subs:
        listing = DirListing.from_dir_entry(s)
        session.add(listing)
        counter += 1
        if counter > 10000:
            session.commit()
            counter = 0
    # break

    for f in files:
        listing = DirListing.from_dir_entry(f)
        try:
            listing.filename.encode('latin-1')
            listing.filepath.encode('latin-1')
        except Exception as e:
            print(e)

        session.add(listing)
        counter += 1
        if counter > 10000:
            try:
                session.commit()
            except SQLAlchemyError as e:
                print(e)
            except UnicodeEncodeError as e:
                print(e)
            counter = 0
try:
    session.commit()
except SQLAlchemyError as e:
    print(e)
