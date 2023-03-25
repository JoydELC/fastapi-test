import psycopg2

#Conectarme a la base de datos cada vez que ejecute esta clase
#Esta va a instanciarme la conexcion a la base de datos.


class UserConnection():
    conn = None
#Constructor
    def __init__(self):
        try:
#conexion a la base de datos videoscribe_p
            self.conn =  psycopg2.connect(
                        database="videoscribe_p",
                        user="postgres",
                        password="sarA123456",
                        host="localhost",
                        port="5432")
# Verificar si las tablas existen y, si no existen, crearlas
            if not self.tables_exist():
                self.create_tables()
        except psycopg2.OperationalError as err:
            print(err)
            self.conn.close()
    
    # Función para verificar si las tablas existen en la base de datos
    def tables_exist(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_class WHERE relname = 'User')")
            user_exist = cur.fetchone()[0]
            cur.execute("SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_class WHERE relname = 'video')")
            video_exist = cur.fetchone()[0]
        return user_exist and video_exist
    
# Función para crear las tablas en la base de datos
    def create_tables(self):
        with self.conn.cursor() as cur:
            # Verificar si la tabla User existe
            cur.execute("SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_class WHERE relname = 'User')")
            user_exist = cur.fetchone()[0]
        
            # Si la tabla no existe, crearla
            if not user_exist:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS "User" (
                        idUser SERIAL PRIMARY KEY,
                        Email VARCHAR(255) NOT NULL,
                        Password VARCHAR(255) NOT NULL,
                        Name VARCHAR(255) NOT NULL
                    )
                """)
        
        # Verificar si la tabla Video existe
            cur.execute("SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_class WHERE relname = 'video')")
            video_exist = cur.fetchone()[0]
        
        # Si la tabla no existe, crearla
            if not video_exist:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS video (
                        idVideo SERIAL PRIMARY KEY,
                        idUser INTEGER REFERENCES "User"(idUser),
                        title VARCHAR(255) NOT NULL,
                        privacy VARCHAR(255) NOT NULL,
                        video VARCHAR(255) NOT NULL,
                        duration INTEGER NOT NULL,
                        cover VARCHAR(255) NOT NULL,
                        category TEXT[] NOT NULL,
                        date DATE
                    )
                """)
            self.conn.commit()


#Funcion para insertar datos en la db videoscribe en la tabla User
    def write(self, data):
        #Contexto donde funciona la db abre y la cierra
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO "User"(email, password,name) VALUES(%(email)s, %(password)s,%(name)s)
                """, data)
                self.conn.commit()

#Login para la db videoescribe
    def authenticate_user(self, email: str, password: str):
        cur = self.conn.cursor()
        cur.execute("SELECT email, password FROM \"User\" WHERE email = %s", (email,))
        user = cur.fetchone()
        if user is None:
            return False
        db_email, db_password = user
        if not password == db_password:
            return False
        return db_email
    
    def return_id(self,email_v:str):
        with self.conn.cursor() as cur:
            query= """SELECT idUser FROM \"User\" WHERE email = %s """
            cur.execute(query,(email_v,))
            data = cur.fetchall()
            id=data[0][0]
            return id
                
#Funcion para leer todo en la DB videoscribe en la tabla de videos
    def read_all(self):
        with self.conn.cursor() as cur:
            data= cur.execute("""
                SELECT * FROM video;     
            """)
            data = cur.fetchall()
            return data



#Funcion para traer todos los videos de un usuario utilizando el name del usuario:
    def all_videos_4_one(self,iduser:str):
        with self.conn.cursor() as cur:
             query = """SELECT \"User\".Name,Video.idUser, Video.idvideo, Video.title, Video.privacy, Video.duration, Video.cover, Video.category, Video.date
                        FROM \"User\"
                        JOIN Video ON \"User\".idUser = Video.idUser
                        WHERE \"User\".iduser = %s"""
             cur.execute(query,(iduser,))
             data = cur.fetchall()
             return data
        
#Funcion para obtener un video por el id de video 
    def find_video_by_id(self, idvideo: str):
        with self.conn.cursor() as cur:
            query = """SELECT \"User\".Name,Video.idUser,Video.idvideo, Video.title, Video.privacy, Video.duration, Video.cover, Video.category, Video.date
                FROM \"User\"
                JOIN Video ON \"User\".idUser = Video.idUser
                WHERE  Video.idvideo = %s"""
            cur.execute(query, (idvideo))
            data = cur.fetchone()
            return data

        
#Funcion para borrar videos de la tabla videos
    def delete_video_by_title(self, id_video: str):
        with self.conn.cursor() as cur:
        # Eliminar el video por su ID
            query = """DELETE FROM Video WHERE idVideo = %s"""
            cur.execute(query, (id_video,))
            self.conn.commit()

        # Retornar el número de filas afectadas (debe ser 1 si el video fue eliminado correctamente)
        return cur.rowcount


#Funcion para actualizar datos
    def update(self, data):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE "user" SET name = %(name)s, phone= %(phone)s WHERE id = %(id)s
            """, data)
        self.conn.commit()

#Destructor
    def __def__(self):
        self.conn.close()

