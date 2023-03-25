from fastapi import FastAPI,Body,HTTPException
from model.user_connection import UserConnection
from schema.user_schema import UserSchema,Video
from datetime import datetime, date, time
import psycopg2

app = FastAPI()
conn = UserConnection()

#Peticion para registrar usuarios
@app.post("/signin")
def insert(user_data: UserSchema =Body()):
    data= user_data.dict()
    data.pop("id")
    try:
        conn.write(data)
        print(data)
        return {"message": "Registrado con exito"}
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return {"message": "Error inserting data"}

 #Peticion de Login   
@app.post("/login")
async def login(email:str = Body(), password: str = Body()):
    email_v = conn.authenticate_user(email,password)
    if not email_v:
        raise HTTPException(status_code=400, detail="Correo electrónico o contraseña incorrectos")
    id = conn.return_id(email_v)
    return {"idUser": id}

#Todos los videos:
@app.get("/")
def root():
    try:
        items= []
        for data in conn.read_all():
            dictionary ={}
            dictionary["idvideo"]=data[0]
            dictionary["iduser"]=data[1]
            dictionary["title"]=data[2]
            dictionary["privacy"]= data[3]
            dictionary["video"]= data[4]
            dictionary["duration"]= data[5]
            dictionary["cover"]= data[6]
            dictionary["category"]= data[7]
            dictionary["date"]= data[8]
            items.append(dictionary)
            
        return items
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return {"message": "No se obtuvo la data"}
    
#Peticion para todos los videos de un usuario
@app.get("/video/{iduser}")
def get_videos_by_username(iduser: str):
    try:
        data=conn.all_videos_4_one(iduser)
        if not data:
            raise HTTPException(status_code=404, detail="No se encontraron videos para el usuario especificado")

        # Crear una lista de objetos Video a partir de los resultados de la consulta
        videos = []
        for row in data:
            # Convertir el objeto date a una cadena de caracteres
            video_date = row[8].strftime("%Y-%m-%d")
            # Crear un objeto Video
            video = Video(name=row[0],iduser=row[1],idvideo=row[2], title=row[3], privacy=row[4], duration=row[5], cover=row[6], category=row[7], date=video_date)
            # Agregar el objeto a la lista de videos
            videos.append(video)
        #print(videos)
        return videos

    except (Exception, psycopg2.Error) as error:
        print("Error al conectarse a la base de datos", error)
        raise HTTPException(status_code=500, detail="Error del servidor")
    

#Peticion para todos los videos de un usuario
@app.get("/{idvideo}")
def get_video_by_title(idvideo: str):
    try:
        data=conn.find_video_by_id(idvideo)
        if not data:
            raise HTTPException(status_code=404, detail="No se encontraro video especificado")

        video_date = data[8].strftime("%Y-%m-%d")
        video = Video(name=data[0],iduser=data[1],idvideo=data[2], title=data[3], privacy=data[4], duration=data[5], cover=data[6], category=data[7], date=video_date)
        return video

    except (Exception, psycopg2.Error) as error:
        print("Error al conectarse a la base de datos", error)
        raise HTTPException(status_code=500, detail="Error del servidor")


@app.delete("/borrar/{title}")
async def delete_video(title: str):
    result = conn.delete_video_by_title(title)
    if result is None:
        return {"message": "El video no existe"}
    elif result == 0:
        return {"message": "El video no se pudo eliminar"}
    else:
        return {"message": "El video se eliminó correctamente"}


