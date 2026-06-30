from pydantic import BaseModel


class CVResponse(BaseModel):
    filename: str
    extracted_text: str
    length: int
