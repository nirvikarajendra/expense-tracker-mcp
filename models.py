from sqlalchemy import Column, Integer, String, Float
from database import Base

class Expenses(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String, default='')
    note = Column(String, default='')
