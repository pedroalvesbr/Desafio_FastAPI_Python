from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL do banco SQLite (arquivo local chamado "app.db")
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# conecta no SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# cria a "fábrica" de sessões (para abrir conexão com o banco)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# classe base que os modelos vão herdar
Base = declarative_base()
