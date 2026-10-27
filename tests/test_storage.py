import json
from datetime import datetime

import pytest

from recipe_finder.models import ValidationError
from recipe_finder.storage import (
    StorageError,
    load_ingredients,
    load_recipes,
    save_ingredients,
)

RECIPES = [
    {
        "id": "oatmeal",
        "name": "Овсянка",
        "ingredients": ["овсянка", "молоко"],
        "cooking_method": "stove",
    },
    {
        "id": "steam_rice",
        "name": "Рис на пару",
        "ingredients": ["рис", "вода"],
        "cooking_method": "steam",
    },
]


def write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def test_load_recipes_returns_recipes(tmp_path):
    path = write_json(tmp_path / "recipes.json", RECIPES)

    recipes = load_recipes(path)

    assert [recipe.id for recipe in recipes] == ["oatmeal", "steam_rice"]


def test_load_recipes_missing_file_raises_storage_error(tmp_path):
    with pytest.raises(StorageError):
        load_recipes(tmp_path / "missing.json")


def test_load_recipes_malformed_json_raises_storage_error(tmp_path):
    path = tmp_path / "recipes.json"
    path.write_text("{не json", encoding="utf-8")

    with pytest.raises(StorageError):
        load_recipes(path)


def test_load_recipes_rejects_non_list(tmp_path):
    path = write_json(tmp_path / "recipes.json", {"recipes": RECIPES})

    with pytest.raises(ValidationError):
        load_recipes(path)


def test_load_recipes_rejects_duplicate_ids(tmp_path):
    path = write_json(tmp_path / "recipes.json", [RECIPES[0], RECIPES[0]])

    with pytest.raises(ValidationError):
        load_recipes(path)


def test_save_ingredients_writes_canonical_json(tmp_path):
    path = tmp_path / "ingredients.json"

    saved = save_ingredients(path, [" Картофель", "Лук", "картофель"])

    assert saved.ingredients == ("картофель", "лук")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["ingredients"] == ["картофель", "лук"]
    assert datetime.fromisoformat(payload["updated_at"])
    assert "картофель" in path.read_text(encoding="utf-8")


def test_save_ingredients_keeps_strict_schema(tmp_path):
    path = tmp_path / "ingredients.json"

    save_ingredients(path, ["лук"])

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert set(payload) == {"ingredients", "updated_at"}


def test_save_ingredients_rejects_empty_list(tmp_path):
    with pytest.raises(ValidationError):
        save_ingredients(tmp_path / "ingredients.json", [])


def test_load_ingredients_roundtrip(tmp_path):
    path = tmp_path / "ingredients.json"

    save_ingredients(path, ["лук", "морковь"])
    loaded = load_ingredients(path)

    assert loaded.ingredients == ("лук", "морковь")


def test_load_ingredients_rejects_extra_field(tmp_path):
    path = write_json(
        tmp_path / "ingredients.json",
        {
            "ingredients": ["лук"],
            "updated_at": "2026-01-01T00:00:00+00:00",
            "extra": 1,
        },
    )

    with pytest.raises(ValidationError):
        load_ingredients(path)


def test_load_ingredients_rejects_bad_timestamp(tmp_path):
    path = write_json(
        tmp_path / "ingredients.json",
        {"ingredients": ["лук"], "updated_at": "вчера"},
    )

    with pytest.raises(ValidationError):
        load_ingredients(path)
