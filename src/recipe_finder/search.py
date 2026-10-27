"""Чистая логика подбора блюд, без ввода-вывода."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .models import COOKING_METHODS, Recipe, normalize_ingredient


@dataclass(frozen=True)
class RecipeMatch:
    recipe: Recipe
    matched: tuple[str, ...]
    missing: tuple[str, ...]
    ratio: float


def find_matching_recipes(
    available: Iterable[str],
    recipes: Iterable[Recipe],
    *,
    min_match_ratio: float = 1.0,
    method: str | None = None,
    limit: int = 3,
) -> list[RecipeMatch]:
    """Возвращает блюда, отсортированные по доле совпадений и названию."""
    if not 0.0 <= min_match_ratio <= 1.0:
        raise ValueError("min_match_ratio должен быть в диапазоне от 0 до 1")
    if method is not None and method not in COOKING_METHODS:
        raise ValueError(f"method должен быть одним из {COOKING_METHODS} или None")
    if limit < 0:
        raise ValueError("limit не может быть отрицательным")

    normalized = {normalize_ingredient(item) for item in available}
    normalized.discard("")
    if not normalized or limit == 0:
        return []

    matches: list[RecipeMatch] = []
    for recipe in recipes:
        if method is not None and recipe.cooking_method != method:
            continue
        matched = tuple(item for item in recipe.ingredients if item in normalized)
        missing = tuple(item for item in recipe.ingredients if item not in normalized)
        ratio = len(matched) / len(recipe.ingredients)
        if ratio + 1e-9 < min_match_ratio:
            continue
        matches.append(RecipeMatch(recipe, matched, missing, ratio))

    matches.sort(key=lambda match: (-match.ratio, match.recipe.name, match.recipe.id))
    return matches[:limit]
