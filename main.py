from fastapi import FastAPI


from api.routes.orders import router as orders_router, router
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")

app = FastAPI(title="E-Commerce API")
app.include_router(orders_router)

@app.get("/")
def read_root():
    return {"message": "E-Commerce API is running"}

#uvicorn main:app --reload