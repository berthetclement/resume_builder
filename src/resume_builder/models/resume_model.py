from pydantic import BaseModel


class contact(BaseModel):
    email: str
    phone: str


class experience(BaseModel):
    company: str
    position: str
    start_date: str
    end_date: str


class Resume(BaseModel):
    name: str
    title: str
    contact: contact
    experiences: list[experience]
