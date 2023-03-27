import os
import base64
from io import BytesIO
from fastapi import FastAPI,Body,status,File, UploadFile,Form
from model.user_connection import UserConnection
from schema.user_schema import UserSchema,Video
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from fastapi.responses import JSONResponse
from PIL import Image
from typing import  List

app = FastAPI()
conn = UserConnection()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#Peticion para registrar usuarios
@app.post("/signin")
def insert(user_data: UserSchema =Body()):
    data= user_data.dict()
    data.pop("id")
    try:
        conn.write(data)
        print(data)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Registrado con exito"})
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Error inserting data"})

 #Peticion de Login   
@app.post("/login")
async def login(email:str = Body(), password: str = Body()):
    email_v = conn.authenticate_user(email,password)
    if not email_v:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "Correo electrónico o contraseña incorrectos"})
        #raise HTTPException(status_code=400, detail="Correo electrónico o contraseña incorrectos")
    id = conn.return_id(email_v)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"idUser": id})

#Todos los videos:
@app.get("/videos")
def get_all_videos():
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
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":"No se encontraron videos para el usuario especificado"})

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
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Error al conectarse en la base de datos"})
    

#Peticion para todos los videos de un usuario
@app.get("/{idvideo}")
def get_video_by_title(idvideo: str):
    try:
        data=conn.find_video_by_id(idvideo)
        if not data:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message":"No se encontraro video especificado"})

        video_date = data[8].strftime("%Y-%m-%d")
        video = Video(name=data[0],iduser=data[1],idvideo=data[2], title=data[3], privacy=data[4], duration=data[5], cover=data[6], category=data[7], date=video_date)
        return video

    except (Exception, psycopg2.Error) as error:
        print("Error al conectarse a la base de datos", error)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Error al conectarse en la base de datos"})

@app.delete("/delete/{id_video}")
async def delete_video(id_video: str):
    result = conn.delete_video_by_title(id_video)
    if result == 0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "El video no se pudo eliminar"})
    else:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "El video se elimino correctamente"})


@app.post("/create/{idUser}")
async def create_video(idUser: str, title: str = Form(...), privacy: str = Form(...), duration: float = Form(...), category: List[str] = Form(...), cover: str = Form(...), gift: str = Form(...), video_file: UploadFile = File(...)):    # Generar la ruta de archivos basada en la información del usuario y del video
    file_directory = f"recursos/{idUser}/{title}"
    video_file_path = os.path.join(file_directory, "videos", video_file.filename)
    cover_file_path = os.path.join(file_directory, "covers", "cover.jpeg")
    gift_file_path = os.path.join(file_directory, "gifts", "gift.jpeg")

    # Crear los directorios si no existen
    os.makedirs(os.path.dirname(video_file_path), exist_ok=True)
    os.makedirs(os.path.dirname(cover_file_path), exist_ok=True)
    os.makedirs(os.path.dirname(gift_file_path), exist_ok=True)

    # Guardar el archivo de video en la ruta especificada
    with open(video_file_path, "wb") as buffer:
        buffer.write(video_file.file.read())

    # Convertir la imagen de portada de base64 a formato de imagen y guardarla en la ruta especificada
    cover_image = Image.open(BytesIO(base64.b64decode(cover)))
    cover_image.save(cover_file_path, "JPEG")

    # Convertir la imagen de regalo de base64 a formato de imagen y guardarla en la ruta especificada
    gift_image = Image.open(BytesIO(base64.b64decode(gift)))
    gift_image.save(gift_file_path, "JPEG")




    
    

    # Insertar los datos del video en la base de datos
    data = conn.post_video_by_idUser(idUser,title,privacy,video_file_path,duration,cover_file_path,gift_file_path,category)
    
    # Devolver una respuesta de éxito
    return JSONResponse(content={"message": f"Video {data} creado para el usuario {idUser}"})