from pydantic import BaseModel


class IngredientFamilyCount(BaseModel):
    family: str
    count: int


class IngredientFamiliesOut(BaseModel):
    families: list[IngredientFamilyCount]
    total: int
