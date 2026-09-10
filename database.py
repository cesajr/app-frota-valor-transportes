import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Define o caminho do arquivo de banco de dados SQLite local
DB_FILE = "frota.db"
engine = create_engine(f"sqlite:///{DB_FILE}", echo=False)

# Configuração da base para os modelos relacionais
Base = declarative_base()

# Tabela para armazenar os dados consolidados por mês (substituindo as antigas abas da planilha)
class FechamentoMensal(Base):
    __tablename__ = 'fechamentos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mes_ano = Column(String, unique=True, nullable=False) # Ex: "Junho/2026"
    km_inicial = Column(Float, default=0.0)
    km_final = Column(Float, default=0.0)
    litros_diesel = Column(Float, default=0.0)
    
    # Relacionamentos com fretes e despesas
    fretes = relationship("Frete", back_populates="fechamento", cascade="all, delete-orphan")
    despesas = relationship("Despesa", back_populates="fechamento", cascade="all, delete-orphan")

# Tabela para registrar cada viagem e sua respectiva receita bruta
class Frete(Base):
    __tablename__ = 'fretes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String, nullable=False)
    origem = Column(String, nullable=False)
    destino = Column(String, nullable=False)
    valor_bruto = Column(Float, nullable=False)
    data_registro = Column(DateTime, default=datetime.utcnow)
    
    fechamento_id = Column(Integer, ForeignKey('fechamentos.id'), nullable=False)
    fechamento = relationship("FechamentoMensal", back_populates="fretes")

# Tabela para registrar custos operacionais e despesas fixas
class Despesa(Base):
    __tablename__ = 'despesas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String, nullable=False) # "Fixo" ou "Operacional"
    descricao = Column(String, nullable=False) # Ex: Pneu, Manutenção, Salário
    valor = Column(Float, nullable=False)
    
    fechamento_id = Column(Integer, ForeignKey('fechamentos.id'), nullable=False)
    fechamento = relationship("FechamentoMensal", back_populates="despesas")

# Função executada para criar o arquivo físico do banco de dados na máquina
def inicializar_banco():
    Base.metadata.create_all(engine)

# Configuração da sessão para manipulação dos dados
Session = sessionmaker(bind=engine)

def obter_sessao():
    return Session()