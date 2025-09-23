from pydantic import BaseModel, Field

class UserModel(BaseModel):
    username: str
    hashed_password: str
    permissions: str

class UserInDB(UserModel):
    id: str = Field(alias="_id")
