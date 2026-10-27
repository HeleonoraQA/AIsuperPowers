"""Чтение и запись локальных JSON-файлов."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import Ingredients, Recipe, ValidationError, normalize_ingredient


class StorageError(Exception):
    """Ошибка чтения или записи локального JSON."""


def _read_json(path: str | Path) -> Any:
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise StorageError(f"файл не найден: {path}") from exc
    except OSError as exc:
        raise StorageError(f"не удалось прочитать {path}: {exc}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise StorageError(f"некорректный JSON в {path}: {exc}") from exc


def load_recipes(path: str | Path) -> list[Recipe]:
    data = _read_json(path)
    if not isinstance(data, list):
        raise ValidationError("recipes.json: ожидался массив рецептов")
    recipes = [Recipe.from_dict(item) for item in data]
    ids = [recipe.id for recipe in recipes]
    if len(ids) != len(set(ids)):
        raise ValidationError("recipes.json: id рецептов должны быть уникальны")
    return recipes


def load_ingredients(path: str | Path) -> Ingredients:
    return Ingredients.from_dict(_read_json(path))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    handle = tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
        suffix=".tmp",
    )
    try:
        with handle:
            handle.write(text)
        os.replace(handle.name, path)
    except OSError as exc:
        Path(handle.name).unlink(missing_ok=True)
        raise StorageError(f"не удалось записать {path}: {exc}") from exc


def save_ingredients(
    path: str | Path,
    items: Iterable[str],
    *,
    now: datetime | None = None,
) -> Ingredients:
    path = Path(path)
    canonical: list[str] = []
    for item in items:
        normalized = normalize_ingredient(item)
        if not normalized:
            raise ValidationError("список ингредиентов: пустое значение")
        if normalized not in canonical:
            canonical.append(normalized)
    if not canonical:
        raise ValidationError("список ингредиентов: нужен хотя бы один ингредиент")
    timestamp = (now or datetime.now(UTC)).replace(microsecond=0)
    payload = Ingredients(tuple(canonical), timestamp.isoformat())
    _write_json(path, payload.to_dict())
    return payload
