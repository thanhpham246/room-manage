from __future__ import annotations

from typing import Any

from sqlalchemy import func, literal
from sqlalchemy.sql.elements import ColumnElement


def build_search_text(*columns: ColumnElement[Any]) -> ColumnElement[str]:
    expression = func.coalesce(columns[0], "")
    for column in columns[1:]:
        expression = expression + literal(" ") + func.coalesce(column, "")
    return func.lower(expression)


def normalized_contains(search_text: ColumnElement[str], search: str) -> ColumnElement[bool] | None:
    term = normalize_search_term(search)
    if term is None:
        return None
    return search_text.like(f"%{escape_like(term)}%", escape="\\")


def normalize_search_term(search: str) -> str | None:
    term = " ".join(search.lower().split())
    return term or None


def escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
