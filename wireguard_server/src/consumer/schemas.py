from pydantic import BaseModel
from enum import Enum

class StateEnum(Enum):
    running = 'running'
    stopped = 'stopped'

class ChangeStateMessage(BaseModel):
    interface: str
    status: StateEnum
