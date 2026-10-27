import json

import pytest

from recipe_finder.cli import main

RECIPES = [
    {
        "id": "potato",
        "name": "Картофель в духовке",
        "ingredients": ["картофель", "масло", "соль"],
        "cooking_method": "oven",
    },
    {
        "id": "omelette",
        "name": "Омлет",
        "ingredients": ["яйцо", "молоко", "соль"],
        "cooking_method": "stove",
    },
]


def prepare(tmp_path):
    recipes = tmp_path / "recipes.json"
    recipes.write_text(json.dumps(RECIPES, ensure_ascii=False), encoding="utf-8")
    return recipes, tmp_path / "ingredients.json"


def test_cli_prints_menu_and_saves_ingredients(tmp_path):
    recipes, store = prepare(tmp_path)
    output = []

    code = main(
        [
            "--ingredients",
            "картофель, масло, соль",
            "--recipes",
            str(recipes),
            "--store",
            str(store),
        ],
        output_fn=output.append,
    )

    assert code == 0
    assert any("Картофель в духовке" in line for line in output)
    payload = json.loads(store.read_text(encoding="utf-8"))
    assert payload["ingredients"] == ["картофель", "масло", "соль"]


def test_cli_reports_no_matches(tmp_path):
    recipes, store = prepare(tmp_path)
    output = []

    code = main(
        [
            "--ingredients",
            "ананас",
            "--recipes",
            str(recipes),
            "--store",
            str(store),
        ],
        output_fn=output.append,
    )

    assert code == 0
    assert any("не найдено" in line for line in output)


def test_cli_method_filter(tmp_path):
    recipes, store = prepare(tmp_path)
    output = []

    code = main(
        [
            "--ingredients",
            "яйцо, молоко, соль",
            "--method",
            "stove",
            "--recipes",
            str(recipes),
            "--store",
            str(store),
        ],
        output_fn=output.append,
    )

    assert code == 0
    text = "\n".join(output)
    assert "Омлет" in text
    assert "Картофель" not in text


def test_cli_empty_input_returns_error(tmp_path):
    recipes, store = prepare(tmp_path)

    code = main(
        [
            "--ingredients",
            " , ",
            "--recipes",
            str(recipes),
            "--store",
            str(store),
        ],
        output_fn=lambda _line: None,
    )

    assert code == 1


def test_cli_missing_recipes_file_returns_error(tmp_path):
    code = main(
        [
            "--ingredients",
            "соль",
            "--recipes",
            str(tmp_path / "missing.json"),
            "--store",
            str(tmp_path / "ingredients.json"),
        ],
        output_fn=lambda _line: None,
    )

    assert code == 2


def test_cli_prompts_when_ingredients_are_not_passed(tmp_path):
    recipes, store = prepare(tmp_path)
    output = []
    prompts = []

    def fake_input(prompt):
        prompts.append(prompt)
        return "картофель, масло, соль"

    code = main(
        ["--recipes", str(recipes), "--store", str(store)],
        input_fn=fake_input,
        output_fn=output.append,
    )

    assert code == 0
    assert prompts
    assert any("Картофель в духовке" in line for line in output)


def test_cli_partial_match_with_threshold(tmp_path):
    recipes, store = prepare(tmp_path)
    output = []

    code = main(
        [
            "--ingredients",
            "картофель, масло",
            "--min-match-ratio",
            "0.5",
            "--recipes",
            str(recipes),
            "--store",
            str(store),
        ],
        output_fn=output.append,
    )

    assert code == 0
    text = "\n".join(output)
    assert "Картофель в духовке" in text
    assert "не хватает: соль" in text


def test_cli_rejects_invalid_ratio(tmp_path):
    recipes, store = prepare(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        main(
            [
                "--ingredients",
                "соль",
                "--min-match-ratio",
                "2",
                "--recipes",
                str(recipes),
                "--store",
                str(store),
            ],
            output_fn=lambda _line: None,
        )

    assert exc_info.value.code == 2
