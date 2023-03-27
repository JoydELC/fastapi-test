from pydantic import BaseModel
from typing import Optional, List

#Esquema de un usuario de la tabla "User"
class UserSchema(BaseModel):
    id: Optional[int]
    email: str
    password: str
    name: str

class Video(BaseModel):
    name: str
    iduser: Optional[int]
    idvideo: Optional[int]
    title: str
    privacy: str
    duration: int
    cover: str
    category: List[str]
    date: str

