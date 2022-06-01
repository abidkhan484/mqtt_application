from typing import List, Union

from pydantic import BaseModel


class HomeIoTBase(BaseModel):
    payload: str

class HomeIoT(HomeIoTBase):
    id: int
    topic: str
    device_id: str
    voltage: str
    current: str
    power: str
    status: str

    class Config:
        orm_mode = True
