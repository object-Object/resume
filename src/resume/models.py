from __future__ import annotations

from pydantic import BaseModel as _BaseModel, Field


class BaseModel(_BaseModel):
    model_config = {
        "extra": "forbid",
    }


class Resume(BaseModel):
    contact: Contact
    employment: list[Employment]
    education: list[Education]
    projects: list[Project]
    skills: dict[str, str]


class Contact(BaseModel):
    name: str
    phone: str
    email: str
    links: list[str]


class Employment(BaseModel):
    title: str
    company: str
    date: Date
    description: list[str] = Field(default_factory=list)


class Education(BaseModel):
    degree: str
    minor: str | None = None
    school: str
    date: Date
    description: dict[str, str] = Field(default_factory=dict)


class Project(BaseModel):
    name: str
    location: str | None = None
    summary: str
    date: Date
    links: list[str]
    description: list[str] = Field(default_factory=list)


type Date = str | DateRange


class DateRange(BaseModel):
    start: str
    end: str = "Present"
