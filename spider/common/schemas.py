from typing import Optional, List
from pydantic import BaseModel, Field, model_validator


class ImagineModel(BaseModel):
    imagine: str


class ProductModel(BaseModel):
    id: int
    name: str = Field(alias='title')
    rating: float
    price: float
    old_price: Optional[float] = None
    images: List[ImagineModel]
    promo_price: Optional[float] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__delattr__('old_price')

    @model_validator(mode='before')
    def set_prices(cls, values):
        if values.get('old_price') is not None:
            values['promo_price'] = values['price']
            values['price'] = values['old_price']
        else:
            values['promo_price'] = None
        return values


class ProductsListCategory(BaseModel):
    count: int
    page_size: int
    total_pages: int
    products: List[ProductModel] = Field(alias='items')


class SubcategoryModel(BaseModel):
    id: int
    name: str


class CategoryModel(BaseModel):
    id: int
    name: str
    subcategories: List[SubcategoryModel] = Field(alias='children')


class CategoriesModel(BaseModel):
    name: str
    categories: List[CategoryModel] = Field(alias='children')
