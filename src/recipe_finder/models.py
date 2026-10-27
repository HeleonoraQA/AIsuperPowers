"""Модели данных и строгая валидация схемы JSON."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

COOKING_METHODS: tuple[str, ...] = ("steam", "oven", "stove")

RECIPE_FIELDS = frozenset({"id", "name", "ingredients", "cooking_method"})
INGREDIENTS_FIELDS = frozenset({"ingredients", "updated_at"})

_ID_PATTERN = re.compile(r"[a-z0-9_]+")
_WHITESPACE = re.compile(r"\s+")


class ValidationError(ValueError):
    """Нарушение строгой схемы JSON."""


def normalize_ingredient(value: str) -> str:
    """Приводит ингредиент к каноническому виду: нижний регистр, один пробел."""
    if not isinstance(value, str):
        raise ValidationError(
            f"ингредиент должен быть строкой, получено: {type(value).__name__}"
        )
    return _WHITESPACE.sub(" ", value.strip().lower())


def _require_mapping(data: Any, fields: frozenset[str], what: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValidationError(f"{what}: ожидался объект JSON")
    keys = set(data)
    missing = fields - keys
    extra = keys - fields
    if missing:
        raise ValidationError(f"{what}: отсутствуют поля {sorted(missing)}")
    if extra:
        raise ValidationError(f"{what}: лишние поля {sorted(extra)}")
    return data


def _require_non_empty_str(data: dict[str, Any], field: str, what: str) -> str:
    value = data[field]
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{what}: поле {field} должно быть непустой строкой")
    return value.strip()


def _require_canonical_ingredients(raw: Any, what: str) -> tuple[str, ...]:
    if not isinstance(raw, list) or not raw:
        raise ValidationError(f"{what}: ingredients должен быть непустым списком")
    ingredients: list[str] = []
    for item in raw:
        normalized = normalize_ingredient(item)
        if normalized != item:
            raise ValidationError(
                f"{what}: ингредиент {item!r} должен быть каноническим {normalized!r}"
            )
        if normalized in ingredients:
            raise ValidationError(f"{what}: ингредиент {normalized!r} повторяется")
        ingredients.append(normalized)
    return tuple(ingredients)


@dataclass(frozen=True)
class Recipe:
    id: str
    name: str
    ingredients: tuple[str, ...]
    cooking_method: str

    @classmethod
    def from_dict(cls, data: Any) -> Recipe:
        payload = _require_mapping(data, RECIPE_FIELDS, "рецепт")
        recipe_id = _require_non_empty_str(payload, "id", "рецепт")
        if not _ID_PATTERN.fullmatch(recipe_id):
            raise ValidationError(
                "рецепт: id должен состоять из латиницы в нижнем регистре, "
                "цифр и подчёркиваний"
            )
        name = _require_non_empty_str(payload, "name", "рецепт")
        ingredients = _require_canonical_ingredients(payload["ingredients"], "рецепт")
        method = payload["cooking_method"]
        if method not in COOKING_METHODS:
            raise ValidationError(
                f"рецепт: cooking_method должен быть одним из {COOKING_METHODS}"
            )
        return cls(recipe_id, name, ingredients, method)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "ingredients": list(self.ingredients),
            "cooking_method": self.cooking_method,
        }


@dataclass(frozen=True)
class Ingredients:
    ingredients: tuple[str, ...]
    updated_at: str

    @classmethod
    def from_dict(cls, data: Any) -> Ingredients:
        what = "список ингредиентов"
        payload = _require_mapping(data, INGREDIENTS_FIELDS, what)
        ingredients = _require_canonical_ingredients(payload["ingredients"], what)
        updated_at = _require_non_empty_str(payload, "updated_at", what)
        try:
            datetime.fromisoformat(updated_at)
        except ValueError as exc:
            raise ValidationError(
                f"{what}: updated_at должен быть в формате ISO-8601"
            ) from exc
        return cls(ingredients, updated_at)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ingredients": list(self.ingredients),
            "updated_at": self.updated_at,
        }
