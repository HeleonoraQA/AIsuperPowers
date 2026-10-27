from pathlib import Path

from recipe_finder.models import COOKING_METHODS, normalize_ingredient
from recipe_finder.storage import load_recipes

DATA = Path(__file__).resolve().parents[1] / "data" / "recipes.json"


def test_seed_recipes_are_valid():
    recipes = load_recipes(DATA)

    assert 5 <= len(recipes) <= 20
    assert {recipe.cooking_method for recipe in recipes} == set(COOKING_METHODS)


def test_seed_ingredients_are_canonical():
    recipes = load_recipes(DATA)

    for recipe in recipes:
        for ingredient in recipe.ingredients:
            assert normalize_ingredient(ingredient) == ingredient
