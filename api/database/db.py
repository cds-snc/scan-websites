import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

connection_string = os.environ.get("SQLALCHEMY_DATABASE_URI")
db_engine = create_engine(connection_string, connect_args={"connect_timeout": 10})
db_session = sessionmaker(bind=db_engine)
