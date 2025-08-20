from app.infrastructure.db import engine
from app.domain.models import Base

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
