import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import initialize_sql

connection_string = os.environ.get("SQLALCHEMY_DATABASE_URI")
# Timeout is set to 10 seconds
db_engine = create_engine(connection_string, connect_args={"connect_timeout": 10})
db_session = sessionmaker(bind=db_engine)
# initialize_sql(db_engine)
