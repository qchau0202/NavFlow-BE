from pydantic import BaseModel, EmailStr

class UserModel(BaseModel):
    name: str
    email: EmailStr
    password: str  # Store hashed password!
    role: str = "guest"  # or "admin"

class UserResponseModel(BaseModel):
    name: str
    email: EmailStr
    role: str = "guest"