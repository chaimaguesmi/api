from datetime import datetime
from fastapi import FastAPI, HTTPException, Form, Request,Depends
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Establish MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    database="mydb",
    password="12345"
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello World"}

# Modèle Pydantic pour le formulaire d'inscription
from pydantic import BaseModel

class SignUpForm(BaseModel):
    username: str
    email: str
    password: str
class LogInForm(BaseModel):
    username: str
    password: str
class OltForm(BaseModel):    
    id: int
    name: str
    location: str
    ip_address: str
    manufacturer: str
    model: str
    installation_date: str


# Endpoint pour l'inscription
@app.post("/signup")
async def sign_up(form: SignUpForm):
    cursor = conn.cursor()

    # Vérifier si l'utilisateur existe déjà
    cursor.execute("SELECT * FROM users WHERE email = %s", (form.email,))
    existing_user = cursor.fetchone()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Insérer l'utilisateur dans la base de données
    sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
    val = (form.username, form.email, form.password)
    cursor.execute(sql, val)
    conn.commit()

    return {"message": "User created successfully"}
# Endpoint for login
@app.post("/login")
async def log_in(form: LogInForm):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (form.username,))
    existing_user = cursor.fetchone()
    if not existing_user:
        raise HTTPException(status_code=401, detail="User dosen't exists")
    return {"message": "login successfully"}
@app.get("/olts")
def get_olts():
    cursor=conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM olts")
    return cursor.fetchall()
@app.post("/add_olts")
async def add_olts(olt: OltForm):
    cursor=conn.cursor(dictionary=True)
    # Vérifier si l'utilisateur existe déjà
    cursor.execute("SELECT * FROM olts WHERE id = %s", (olt.id,))
    existing_olt = cursor.fetchone()
    if existing_olt:
        raise HTTPException(status_code=400, detail="id token already exists")

    # Insérer l'utilisateur dans la base de données
    sql = "INSERT INTO olts (id,name, location, ip_address, manufacturer, model, installation_date) VALUES (%s, %s, %s, %s, %s, %s,%s);"
    val = (olt.id,olt.name,olt.location,olt.ip_address,olt.manufacturer,olt.model,olt.installation_date)
    cursor.execute(sql, val)
    conn.commit()
    return "added successfully"
@app.delete("/delete_olts/{id}")
async def delete_olts(id: int ):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM olts WHERE id = %s", (id,))
    olt = cursor.fetchone()
    if not olt:
        raise HTTPException(status_code=404, detail="olt not found")
    cursor.execute("delete from olts where id=%s",(id,))
    conn.commit()
    return "delete successfully"
@app.put("/update_olts/{id}")
async def update_olts(id: int, olt: OltForm):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
            UPDATE olts
            SET name = %s, location = %s, ip_address = %s, manufacturer = %s, model = %s, installation_date = %s
            WHERE id = %s
        """, (olt.name, olt.location, olt.ip_address,olt.manufacturer, olt.model, olt.installation_date, id))
    olt = cursor.fetchone()
    conn.commit()
    return {"message": "OLT updated successfully"}