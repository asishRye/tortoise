from decouple import config
from typing import List

from fastapi import FastAPI, HTTPException
import tortoise
from models import User_Pydantic, UserIn_Pydantic, Users
from pydantic import BaseModel
from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise

app = FastAPI(title="Tortoise ORM FastAPI example")


class Status(BaseModel):
    message: str


@app.get("/users", response_model=List[User_Pydantic])
async def get_users():
    return await User_Pydantic.from_queryset(Users.all())


@app.post("/users", response_model=User_Pydantic)
async def create_user(user: UserIn_Pydantic):
    user_obj = await Users.create(**user.dict(exclude_unset=True))
    return await User_Pydantic.from_tortoise_orm(user_obj)


@app.get(
    "/user/{user_id}", response_model=User_Pydantic, responses={404: {"model": HTTPNotFoundError}}
)
async def get_user(user_id: int):
    return await User_Pydantic.from_queryset_single(Users.get(id=user_id))


@app.put(
    "/user/{user_id}", response_model=User_Pydantic, responses={404: {"model": HTTPNotFoundError}}
)
async def update_user(user_id: int, user: UserIn_Pydantic):
    await Users.filter(id=user_id).update(**user.dict(exclude_unset=True))
    return await User_Pydantic.from_queryset_single(Users.get(id=user_id))


@app.delete("/user/{user_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_user(user_id: int):
    deleted_count = await Users.filter(id=user_id).delete()
    if not deleted_count:
        raise HTTPException(
            status_code=404, detail=f"User {user_id} not found")
    return Status(message=f"Deleted user {user_id}")


POSTGRES_HOST = config('POSTGRES_HOST')
POSTGRES_PORT = config('POSTGRES_PORT')
POSTGRES_USER = config('POSTGRES_USER')
POSTGRES_PASSWORD = config('POSTGRES_PASSWORD')
POSTGRES_DB = config('POSTGRES_DB')
pg_url = f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

register_tortoise(
    app,
    db_url=pg_url,
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

TORTOISE_ORM = {
    "connections": {"default": "postgres://postgres:mysecretpassword@localhost:5432/mydb"},
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": 'default',
        },
    },
}
