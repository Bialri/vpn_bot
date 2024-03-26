from pydantic import BaseModel


class CreateInterfaceSchema(BaseModel):
    peer_name: str

