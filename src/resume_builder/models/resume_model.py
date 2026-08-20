from pydantic import BaseModel


class main(BaseModel):
    name: str
    title: str
    description: str


class contact(BaseModel):
    email: str
    phone: str


class experience(BaseModel):
    company: str
    position: str
    start_date: str
    end_date: str


class Resume(BaseModel):
    main: main
    contact: contact
    experiences: list[experience]
