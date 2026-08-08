from pydantic import BaseModel


class contact(BaseModel):
    email: str
    phone: str


class Resume(BaseModel):
    name: str
    title: str
    contact: contact
