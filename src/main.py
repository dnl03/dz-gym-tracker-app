from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def hellow_world():
    return {"message": "Hello, World!"}
