"""Submódulos de la capa de dominio."""

from smart_api_search.domain.result import SearchResult, compose_result, get_by_spec_ref
from smart_api_search.domain.retrieval import search

__all__ = ["SearchResult", "compose_result", "get_by_spec_ref", "search"]
