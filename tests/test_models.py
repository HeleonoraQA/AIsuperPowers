from dataclasses import FrozenInstanceError

import pytest

from recipe_finder.models import Recipe, ValidationError, normalize_ingredient


def valid_payload() -> dict:
    return {
        "id": "oatmeal",
        "name": "Овсянка",
        "ingredients": ["овсянка", "молоко"],
        "cooking_method": "stove",
    }


def test_normalize_ingredient_strips_and_lowercases():
    assert normalize_ingredient("  Картофель  ") == "картофель"


def test_normalize_ingredient_collapses_spaces():
    assert normalize_ingredient("перец   чёрный") == "перец чёрный"


def test_recipe_from_dict_builds_immutable_recipe():
    recipe = Recipe.from_dict(valid_payload())

    assert recipe.id == "oatmeal"
    assert recipe.name == "Овсянка"
    assert recipe.ingredients == ("овсянка", "молоко")
    assert recipe.cooking_method == "stove"

    with pytest.raises(FrozenInstanceError):
        recipe.name = "другое"  # type: ignore[misc]


def test_recipe_to_dict_roundtrip():
    recipe = Recipe.from_dict(valid_payload())

    assert recipe.to_dict() == valid_payload()


@pytest.mark.parametrize("field", ["id", "name", "ingredients", "cooking_method"])
def test_recipe_rejects_missing_field(field):
    payload = valid_payload()
    payload.pop(field)

    with pytest.raises(ValidationError):
        Recipe.from_dict(payload)


def test_recipe_rejects_extra_field():
    payload = valid_payload()
    payload["extra"] = 1

    with pytest.raises(ValidationError):
        Recipe.from_dict(payload)


@pytest.mark.parametrize("method", ["grill", "", "Oven"])
def test_recipe_rejects_unknown_cooking_method(method):
    payload = valid_payload()
    payload["cooking_method"] = method

    with pytest.raises(ValidationError):
        Recipe.from_dict(payload)


def test_recipe_rejects_empty_ingredients():
    payload = valid_payload()
    payload["ingredients"] = []

    with pytest.raises(ValidationError):
        Recipe.from_dict(payload)


def test_recipe_rejects_non_canonical_ingredient():
    payload = valid_payload()
    payload["ingredients"] = ["Молоко"]

    with pytest.raises(ValidationError):
        Recipe.from_dict(payload)


def test_recipe_rejects_duplicate_ingredients():
    payload = valid_payload()
    payload["ingredients"] = ["молоко", "молоко"]

    with pytest.raises(ValidationError):
        Recipe.from_dict(payload)


def test_recipe_rejects_bad_id():
    payload = valid_payload()
    payload["id"] = "Плохой id"

    with pytest.raises(ValidationError):
        Recipe.from_dict(payload)
