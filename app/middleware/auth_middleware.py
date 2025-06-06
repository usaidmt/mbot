from fastapi.routing import APIRoute
from fastapi import Request, HTTPException
import jwt
from dotenv import load_dotenv
import os


load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

class auth_route(APIRoute):
    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request):
            # If endpoint is marked as allow_anonymous, skip auth
            if getattr(self.endpoint, "allow_anonymous", False):
                return await original_route_handler(request)

            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

            token = auth_header.split(" ")[1]
            try:
                jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=401, detail="Token expired")
            except jwt.InvalidTokenError:
                raise HTTPException(status_code=401, detail="Invalid token")

            return await original_route_handler(request)

        return custom_route_handler
