from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: str
    detail: str
    status_code: int


class NLPRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        examples=["¿Cuáles son las marcas más vendidas?"],
    )


class NLPResponse(BaseModel):
    question: str
    answer: str
