import pytest

from recipe_finder.models import Recipe
from recipe_finder.search import find_matching_recipes


def make_recipe(recipe_id, name, ingredients, method="stove"):
    return Recipe(
        id=recipe_id,
        name=name,
        ingredients=tuple(ingredients),
        cooking_method=method,
    )


RECIPES = [
    make_recipe(
        "potato",
        "Картофель в духовке",
        ["картофель", "масло", "соль"],
        "oven",
    ),
    make_recipe("omelette", "Омлет", ["яйцо", "молоко", "соль"], "stove"),
    make_recipe("rice", "Рис на пару", ["рис", "соль"], "steam"),
    make_recipe("soup", "Овощной суп", ["картофель", "морковь", "лук", "вода"]),
]


def test_full_match_only_by_default():
    matches = find_matching_recipes(["картофель", "масло", "соль"], RECIPES)

    assert [match.recipe.id for match in matches] == ["potato"]
    assert matches[0].ratio == 1.0
    assert matches[0].missing == ()


def test_partial_match_returns_missing_ingredients():
    matches = find_matching_recipes(
        ["картофель", "масло"], RECIPES, min_match_ratio=0.5
    )

    potato = next(match for match in matches if match.recipe.id == "potato")
    assert potato.missing == ("соль",)
    assert potato.ratio == pytest.approx(2 / 3)


def test_method_filter():
    matches = find_matching_recipes(
        ["соль"], RECIPES, min_match_ratio=0.0, method="steam"
    )

    assert [match.recipe.id for match in matches] == ["rice"]


def test_results_sorted_by_ratio_then_name():
    recipes = [
        make_recipe("b_partial", "Блюдо Б", ["картофель", "соль", "перец"]),
        make_recipe("a_full", "Блюдо А", ["картофель"]),
        make_recipe("c_full", "Блюдо В", ["соль"]),
    ]

    matches = find_matching_recipes(["картофель", "соль"], recipes, min_match_ratio=0.5)

    assert [match.recipe.id for match in matches] == [
        "a_full",
        "c_full",
        "b_partial",
    ]


def test_limit_zero_returns_empty():
    assert find_matching_recipes(["соль"], RECIPES, limit=0) == []


def test_limit_caps_results():
    matches = find_matching_recipes(["соль"], RECIPES, min_match_ratio=0.0, limit=1)

    assert len(matches) == 1


def test_available_ingredients_are_normalized():
    matches = find_matching_recipes([" Картофель ", "МАСЛО", "соль"], RECIPES)

    assert [match.recipe.id for match in matches] == ["potato"]


def test_empty_available_returns_nothing():
    assert find_matching_recipes([], RECIPES, min_match_ratio=0.0) == []


@pytest.mark.parametrize("ratio", [-0.1, 1.1])
def test_invalid_ratio_raises(ratio):
    with pytest.raises(ValueError):
        find_matching_recipes(["соль"], RECIPES, min_match_ratio=ratio)


def test_invalid_method_raises():
    with pytest.raises(ValueError):
        find_matching_recipes(["соль"], RECIPES, method="grill")


def test_negative_limit_raises():
    with pytest.raises(ValueError):
        find_matching_recipes(["соль"], RECIPES, limit=-1)
