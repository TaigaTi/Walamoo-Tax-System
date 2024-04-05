from os import getenv
from dotenv import load_dotenv
load_dotenv()

from fastapi_login import LoginManager

SECRET = getenv("SECRET_KEY")
class NotAuthenticatedException(Exception):
    pass

manager = LoginManager(SECRET, "/login", not_authenticated_exception=NotAuthenticatedException, use_cookie=True)