from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    photo_url: str | None = None  # может быть необязательным
    category_id: int


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    photo_url: str | None = None
    category_id: int | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    photo_url: str | None
    category_id: int


class ProductWithCategory(ProductResponse):
    category_name: str


class CategoryCreate(BaseModel):
    category_name: int
    photo_url: str | None = None