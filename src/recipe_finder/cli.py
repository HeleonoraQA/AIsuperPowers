"""CLI: ввод ингредиентов, сохранение и вывод меню."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from .models import COOKING_METHODS, ValidationError
from .search import RecipeMatch, find_matching_recipes
from .storage import StorageError, load_recipes, save_ingredients

METHOD_LABELS = {
    "steam": "на пару",
    "oven": "в духовке",
    "stove": "на плите",
}

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RECIPES = _PROJECT_ROOT / "data" / "recipes.json"
DEFAULT_STORE = _PROJECT_ROOT / "data" / "ingredients.json"


def _ratio(value: str) -> float:
    try:
        ratio = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("ожидалось число от 0 до 1") from exc
    if not 0.0 <= ratio <= 1.0:
        raise argparse.ArgumentTypeError("порог должен быть в диапазоне от 0 до 1")
    return ratio


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="recipe-finder",
        description="Подбор блюд из имеющихся продуктов.",
    )
    parser.add_argument(
        "--ingredients",
        help="Ингредиенты через запятую; без флага будет запрошен ввод",
    )
    parser.add_argument(
        "--method",
        choices=COOKING_METHODS,
        help="Способ приготовления",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Сколько блюд показать (по умолчанию 3)",
    )
    parser.add_argument(
        "--min-match-ratio",
        type=_ratio,
        default=1.0,
        help="Минимальная доля совпавших ингредиентов, от 0 до 1 (по умолчанию 1.0)",
    )
    parser.add_argument(
        "--recipes",
        type=Path,
        default=DEFAULT_RECIPES,
        help="Путь к базе рецептов",
    )
    parser.add_argument(
        "--store",
        type=Path,
        default=DEFAULT_STORE,
        help="Куда сохранить введённые ингредиенты",
    )
    return parser


def _read_ingredients(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def _format_match(index: int, match: RecipeMatch) -> str:
    percent = round(match.ratio * 100)
    label = METHOD_LABELS[match.recipe.cooking_method]
    line = f"{index}. {match.recipe.name} — {label} (совпадение {percent}%)"
    if match.missing:
        line += f"; не хватает: {', '.join(match.missing)}"
    return line


def main(
    argv: Sequence[str] | None = None,
    *,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> int:
    args = build_parser().parse_args(argv)

    raw = args.ingredients
    if raw is None:
        raw = input_fn("Введите ингредиенты через запятую: ")
    ingredients = _read_ingredients(raw)
    if not ingredients:
        output_fn("Список ингредиентов пуст.")
        return 1

    try:
        recipes = load_recipes(args.recipes)
        save_ingredients(args.store, ingredients)
        matches = find_matching_recipes(
            ingredients,
            recipes,
            min_match_ratio=args.min_match_ratio,
            method=args.method,
            limit=args.limit,
        )
    except (StorageError, ValidationError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 2

    if not matches:
        output_fn("Подходящих блюд не найдено.")
        return 0

    output_fn("Предлагаемое меню:")
    for index, match in enumerate(matches, start=1):
        output_fn(_format_match(index, match))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
