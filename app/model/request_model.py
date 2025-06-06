from pydantic import BaseModel

class token_request(BaseModel):
    user_code: int
    email_id: str

class generate_request(BaseModel):
    language: str
    prompt: str
    

