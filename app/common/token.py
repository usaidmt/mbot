from app.model import request_model
from ..common import utils
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os


load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXP_DELTA_SECONDS = int(os.getenv("JWT_EXP_DELTA_SECONDS")) # 1 hour expiration


def generate_token(request: request_model.token_request):
    try:

        para = {
            "user_code": request.user_code,
            "email": request.email_id,
        };

        data = utils.call_stored_procedure("sp_get_client_info", para);

        if not data or len(data) == 0:
            return None

        payload = create_jwt_payload(request, data[0]);
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM);

        return {
            "token": token,
            "token_type": "Bearer",
            "expires_in": int(JWT_EXP_DELTA_SECONDS / 60),
            "expires_at": datetime.fromtimestamp(payload["exp"])
        }

    except Exception as e:
        raise e


def create_jwt_payload(request, params_list):
    now = datetime.now(timezone.utc)  # Use timezone-aware datetime in UTC

    payload = {
        "user_code": request.user_code,
        "email_id": request.email_id,
        "company_name": params_list["company_name"],
        "industry_name": params_list["industries_company_operate_in_display"],
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=JWT_EXP_DELTA_SECONDS)).timestamp()),
    }
    
    # Optional: Debug info for clarity
    print("Issued at (UTC):", datetime.fromtimestamp(payload["iat"], tz=timezone.utc))
    print("Expires at (UTC):", datetime.fromtimestamp(payload["exp"], tz=timezone.utc))

    print("LOCAL Issued at (UTC):", datetime.fromtimestamp(payload["iat"]))
    print("LOCAL Expires at (UTC):", datetime.fromtimestamp(payload["exp"]))

    return payload;