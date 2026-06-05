"""Тесты Pydantic-схем: валидация запросов и сборка ответа."""

import pytest
from pydantic import ValidationError

from app.schemas import SearchRequest, SearchResponse, SimilarQuestion


def test_search_request_default_k():
    request = SearchRequest(query="hello")
    assert request.k == 5


def test_search_request_rejects_empty_query():
    with pytest.raises(ValidationError):
        SearchRequest(query="")


def test_search_request_rejects_out_of_range_k():
    with pytest.raises(ValidationError):
        SearchRequest(query="x", k=0)
    with pytest.raises(ValidationError):
        SearchRequest(query="x", k=1000)


def test_search_response_builds():
    response = SearchResponse(
        query="q",
        threshold=0.8,
        results=[SimilarQuestion(question="a", score=0.9, is_duplicate=True)],
    )
    assert response.results[0].is_duplicate is True
    assert response.threshold == 0.8
