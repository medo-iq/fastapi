from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database

DATABASE_URL = "sqlite:///./test.db"

# إعداد قاعدة البيانات
database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# تعريف نموذج للبيانات
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)

# إنشاء الجداول في قاعدة البيانات
Base.metadata.create_all(bind=engine)

# تعريف FastAPI
app = FastAPI()

# تعريف نموذج البيانات باستخدام Pydantic
class ItemCreate(BaseModel):
    name: str
    description: str

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# طلب GET لعرض جميع العناصر
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    query = "SELECT * FROM items LIMIT :limit OFFSET :skip"
    return await database.fetch_all(query=query, values={"skip": skip, "limit": limit})

# طلب POST لإنشاء عنصر جديد
@app.post("/items/", response_model=ItemCreate)
async def create_item(item: ItemCreate):
    query = "INSERT INTO items(name, description) VALUES (:name, :description)"
    values = {"name": item.name, "description": item.description}
    await database.execute(query=query, values=values)
    return item
