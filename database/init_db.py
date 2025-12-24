from sqlalchemy import create_engine
from database.models import Base
from config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)
Base.metadata.create_all(engine)
print("✅ Database initialized successfully!")
