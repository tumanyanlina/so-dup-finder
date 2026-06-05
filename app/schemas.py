"""Pydantic-схемы запросов и ответов API.

По этим схемам FastAPI валидирует входные данные и автоматически
строит документацию (Swagger UI на /docs).
"""

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Запрос на поиск похожих вопросов."""

    query: str = Field(..., min_length=1, description="Текст вопроса")
    k: int = Field(5, ge=1, le=50, description="Сколько похожих вопросов вернуть")


class SimilarQuestion(BaseModel):
    """Один найденный похожий вопрос."""

    question: str
    score: float = Field(..., description="Косинусная близость (0..1, больше = похожее)")


class SearchResponse(BaseModel):
    """Ответ: исходный запрос и список похожих вопросов."""

    query: str
    results: list[SimilarQuestion]
