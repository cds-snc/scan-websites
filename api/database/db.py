import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_engine = create_engine(os.environ.get("SQLALCHEMY_DATABASE_URI"))
db_session = sessionmaker(bind=db_engine)