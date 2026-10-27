# Архитектура Recipe Finder (AIsuperPower)

## Назначение

CLI-приложение: пользователь вводит имеющиеся продукты, приложение сохраняет их
в локальный JSON и предлагает 1–3 блюда с фильтром по способу приготовления.

## Слои

| Модуль | Ответственность | Зависит от |
| --- | --- | --- |
| `src/recipe_finder/models.py` | dataclasses `Recipe`, `Ingredients`, строгая валидация, нормализация, `ValidationError` | stdlib |
| `src/recipe_finder/storage.py` | чтение/запись JSON, атомарная запись, `StorageError` | `models` |
| `src/recipe_finder/search.py` | чистая функция подбора, `RecipeMatch` | `models` |
| `src/recipe_finder/cli.py` | argparse, ввод, вывод, коды возврата | `models`, `storage`, `search` |
| `src/recipe_finder/__main__.py` | запуск `python -m recipe_finder` | `cli` |

Правило: `search` не знает о файлах и консоли, `storage` не знает о CLI.
Поиск тестируется на фиксированных рецептах в памяти, без файлов и `random`.

Поток выполнения: CLI → `load_recipes` → `save_ingredients` →
`find_matching_recipes` → вывод меню.

## Формат данных

### `data/recipes.json`

Массив объектов, у каждого ровно четыре поля (лишние и отсутствующие — ошибка):

| Поле | Тип | Правило |
| --- | --- | --- |
| `id` | string | уникальный, латиница в нижнем регистре, цифры, `_` |
| `name` | string | непустое название блюда по-русски |
| `ingredients` | string[] | непустой список канонических значений без дублей |
| `cooking_method` | string | `steam`, `oven` или `stove` |

### `data/ingredients.json` (создаётся при запуске)

Объект ровно с двумя полями:

| Поле | Тип | Правило |
| --- | --- | --- |
| `ingredients` | string[] | непустой список канонических значений без дублей |
| `updated_at` | string | ISO-8601, UTC, без микросекунд |

### Канонизация ингредиентов

Нижний регистр, обрезка пробелов по краям, схлопывание внутренних пробелов.
Значения в файлах уже канонические; загрузчик отвергает неканонические,
чтобы не было двух представлений одного продукта.

## Алгоритм поиска

- Входной список нормализуется в множество; пустые значения игнорируются.
- Для каждого рецепта: `matched` (в порядке рецепта), `missing`,
  `ratio = len(matched) / len(ingredients)`.
- Фильтры: `method` (если задан) и `ratio >= min_match_ratio`.
- Сортировка детерминированная: `ratio` по убыванию, затем `name`, затем `id`.
- `limit` по умолчанию 3; `limit == 0` или пустой ввод → пустой результат.
- Полное совпадение — режим по умолчанию (`min_match_ratio = 1.0`).
  Частичное доступно явно: `--min-match-ratio` в CLI.

## CLI

| Флаг | Назначение |
| --- | --- |
| `--ingredients` | список через запятую; без флага — интерактивный ввод |
| `--method` | фильтр: `steam` / `oven` / `stove` |
| `--limit` | сколько блюд показать (по умолчанию 3) |
| `--min-match-ratio` | порог совпадения от 0 до 1 (по умолчанию 1.0) |
| `--recipes` | путь к базе рецептов |
| `--store` | путь к файлу введённых ингредиентов |

Коды возврата: `0` — успех, `1` — пустой ввод, `2` — ошибка файла/схемы/аргументов.
Формат строки меню: `N. Название — способ (совпадение X%)`; при частичном
совпадении добавляется `; не хватает: ...`.

## Решения и условия пересмотра

| # | Решение | Статус | Пересмотреть, если |
| --- | --- | --- | --- |
| D1 | Python 3.11+ (проверено на 3.13), только stdlib; pytest и ruff — dev-инструменты | принято | понадобится веб-интерфейс, упаковка в exe или строгая схема в рантайме |
| D2 | Ключи JSON английские; названия блюд и ингредиенты — по-русски | принято | появится локализация или англоязычные пользователи |
| D3 | Строгая схема: лишние и отсутствующие поля — ошибка | принято | Этап 5 (`cooking_time`): потребуется опциональное поле или миграция `data/recipes.json` |
| D4 | Полное совпадение по умолчанию; частичное — явным флагом | принято | UAT покажет, что частичные предложения нужны по умолчанию |
| D5 | Линейный перебор рецептов | принято | база вырастет настолько, что перебор станет заметным (сейчас 10 рецептов) |
| D6 | Конфигурация OpenCode V2: `plugins` одним массивом, правила через `instructions`, навык в `.opencode/skills/` | принято | V2 начнёт понимать path-scoped `.mdc`-правила или изменит discovery навыков |
| D7 | Память Claude-Mem подключена и обязательна для поиска прошлых решений; правила — `rules/claude-mem.md`, навык `mem-search` | принято | воркер `http://localhost:37777` перестанет отвечать или память заменят другим хранилищем |

## Конфигурация OpenCode

| Путь | Роль |
| --- | --- |
| `opencode.json` | `instructions` (`rules.md`, `rules/python.md`, `rules/claude-mem.md`), `permissions` + `policies`, один массив `plugins` |
| `rules.md` | жёсткие правила проекта: доступ к файлам, права shell |
| `rules/python.md` | короткие соглашения по Python (без Cursor-фронтматтера `globs`) |
| `rules/claude-mem.md` | память: что подключено, порядок `search` → `timeline` → `get_observations`, что сохранять |
| `.opencode/skills/checkpoint/SKILL.md` | навык `checkpoint`; единственный путь, который V2 обнаруживает автоматически |
| `.opencode/skills/mem-search/SKILL.md` | навык `mem-search`: поиск по памяти перед задачей и запись решений |

Важно: в V2 поле плагинов — `plugins` (массив), ключ `plugin` устарел; навыки ищутся
только в `.opencode/skills/` (или `.claude/skills`, `.agents/skills`), корневой `skills/` не сканируется.

## Память (Claude-Mem)

Память проекта подключена и доступна агенту в OpenCode: плагин
`@ephemushroom/opencode-claude-mem` в `plugins`, локальный
`~/.config/opencode/plugins/claude-mem.js`, MCP `claude-mem`, воркер и viewer
`http://localhost:37777`, проект `AIsp`. В Cursor — MCP
`plugin-claude-mem-mcp-search`.

| Что | Где |
| --- | --- |
| Правила работы с памятью | `rules/claude-mem.md` (подключены через `instructions`) |
| Навык поиска | `.opencode/skills/mem-search/SKILL.md` |
| Поиск | `search` → `timeline` → `get_observations` |
| Запись решения | `save_memory` (`project: "AIsp"`) |

Границы: память — вторичный источник. Источник истины для поведения — код и тесты,
для решений — `docs/architecture.md`, для истории — `docs/progress.md`.
Секреты в память не пишутся.

## Запуск и проверки

```bash
python -m pytest -q
python -m ruff check . --fix
python -m ruff format .

# Windows PowerShell
$env:PYTHONPATH='src'; $env:PYTHONUTF8='1'
python -m recipe_finder --ingredients "картофель, масло, соль"
```

Установка как пакета (`pip install -e .`) и console script `recipe-finder`
пока не проверялись — запуск идёт через `python -m recipe_finder`.
