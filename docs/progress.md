# Текущее состояние

## Цель

Discovery и Этап 1 из `docs/plan.md`: выбрать стек, настроить структуру папок,
создать базовый JSON с рецептами. В рамках TDD дополнительно реализованы
Этапы 2–4: ввод и сохранение ингредиентов, поиск блюд, вывод меню.

## Сделано

- Claude-Mem подключён для агента: плагин `@ephemushroom/opencode-claude-mem`
  в `plugins`, локальный `~/.config/opencode/plugins/claude-mem.js`, MCP `claude-mem`,
  воркер и viewer `http://localhost:37777`, проект `AIsp`. В Cursor тот же воркер
  доступен через MCP `plugin-claude-mem-mcp-search`. В памяти есть записи
  (минимум `#1 AIsp Recipe Finder memory bootstrap`).
  Инструкции: `AGENTS.md` §2, `rules.md`, `rules/claude-mem.md` подключён через
  `opencode.json` `instructions`, навык `.opencode/skills/mem-search/SKILL.md`;
  Cursor-правила `.cursor/rules/claude-mem.mdc` нет и не создавалось.
  Решение D7 в `docs/architecture.md`.
- Superpowers brainstorm-project: результаты записаны в корневой `DISCOVERY.md`
  (intent, подходы по 4 вопросам из `docs/plan.md` §4, выбранное направление,
  D1–D6, открытый вопрос D3/`cooking_time`). Код не менялся.
- Стек: Python 3.13.3 (`requires-python >=3.11`), только stdlib; dev — pytest 9.1.1, ruff 0.17.1.
- Пакет `src/recipe_finder/`: `models`, `storage`, `search`, `cli`, `__main__`.
- `data/recipes.json`: 10 рецептов, покрыты все три способа приготовления.
- `tests/`: 49 тестов — модели, хранилище, поиск, CLI, валидация сид-данных.
- `docs/architecture.md`: слои, схема JSON, алгоритм, решения D1–D7.
- `docs/plan.md`: Этапы 1–4 отмечены выполненными.
- `opencode.json`: исправлена висячая запятая (JSON был невалиден и не загружался бы);
  allowlist приведён к стеку проекта (`pytest *`, `ruff check *`, `ruff format *`),
  правила npm-test/npm-run-lint удалены.
- `rules.md`: переписана под Python (раньше описывала npm/husky из Node-шаблона);
  husky-раздел заменён проверками `pytest` + `ruff check .`, ссылка на `docs/memory.md`
  заменена на существующие файлы памяти.
- `AGENTS.md`: раздел 1 обновлён (стек определён), правило про `mem-search` заменено
  на читаемую альтернативу, добавлен раздел 7 со ссылкой на `rules.md` вместо
  дублированного npm-блока.
- `opencode.json`: два дублирующихся ключа `plugin` (JSON молча оставлял последний,
  и `superpowers` не загружался) заменены одним массивом `plugins` — имя поля V2.
  `instructions` дополнен `rules/python.md`.
- `skills/SKILL.md` → `.opencode/skills/checkpoint/SKILL.md`: корневой `skills/`
  OpenCode V2 не сканирует. `rules/python.mdc` → `rules/python.md` без Cursor-фронтматтера
  (`globs`/`alwaysApply` в V2 не поддерживаются), файл подключён через `instructions`.
- `docs/architecture.md`: добавлен раздел «Конфигурация OpenCode» и решение D6.
- `mem-search` больше не помечен недоступным: `AGENTS.md` §2 переписан — память
  Claude-Mem подключена, порядок `search` → `timeline` → `get_observations`,
  значимые решения — через `save_memory`.
- Созданы уже упоминавшиеся в документации, но отсутствовавшие файлы:
  `rules/claude-mem.md` (что подключено, как искать, что сохранять, ограничения)
  и `.opencode/skills/mem-search/SKILL.md`; правило добавлено в `opencode.json`
  `instructions`.
- `docs/architecture.md`: раздел «Память (Claude-Mem)» и решение D7.
- `docs/progress.md`: убрано ложное утверждение о `.cursor/rules/claude-mem.mdc`
  и о пустой памяти — в ней есть записи.

## Проверки

- Claude-Mem MCP `session_start_context` (проект `AIsp`, platform `cursor`) →
  воркер отвечает; «This project has no memory yet»; viewer `http://localhost:37777`.
- Claude-Mem `search` по AIsp → нет записей (ожидаемо до первого `save_memory`).
- `opencode.json` + `python -m json.tool` / `json.load` → JSON валиден (0 ошибок).
- `opencode.json` через `json.load` → JSON валиден (был невалиден: висячая запятая, строка 22).
- `python -m pytest -q` → `49 passed`.
- `python -m ruff check .` → `All checks passed!`
- `python -m ruff format .` → `16 files left unchanged`.
- `opencode.json` после правки: `json.load` → валиден, ключ `plugin` отсутствует,
  `plugins` — массив из двух элементов.
- Навык и правило на новых путях: `.opencode/skills/checkpoint/SKILL.md`,
  `rules/python.md`; старые `skills/SKILL.md` и `rules/python.mdc` удалены.
- Память: `claude_mem_search("recipe finder AIsuperPower решения")` →
  найдена запись `#1 AIsp Recipe Finder memory bootstrap` (память не пустая).
- `rules/claude-mem.md` и `.opencode/skills/mem-search/SKILL.md` существуют;
  `opencode.json` `instructions` → `rules.md`, `rules/python.md`, `rules/claude-mem.md`.
- Поиск устаревших формулировок по `AGENTS.md`, `rules.md`, `docs/*.md`,
  `rules/*.md`, `.opencode/skills/*/SKILL.md`: слова «недоступен» нет; упоминания
  `.cursor/rules/claude-mem.mdc` остались только как констатация, что файла нет.
- Ручной запуск (полное совпадение): `--ingredients "картофель, масло, соль"`
  → `1. Картофель в духовке — в духовке (совпадение 100%)`.
- Ручной запуск (фильтр): `--ingredients "яйцо, молоко, масло, соль" --method stove`
  → `1. Омлет — на плите (совпадение 100%)`.
- Ручной запуск (частичное совпадение): `--ingredients "картофель, масло" --min-match-ratio 0.5`
  → два блюда: `Картофель в духовке` (67%, не хватает соль) и `Овощи в духовке` (50%).
- Интерактивный ввод через pipe (`брокколи, соль`) → `Брокколи на пару`, код 0.
- `data/ingredients.json` прочитан программно как UTF-8: значения совпадают с введёнными.

## Не проверено

- `pip install -e .` и console script `recipe-finder` — запуск только через `python -m recipe_finder`.
- Реальный интерактивный ввод в терминале: путь покрыт тестом с подменой `input_fn` и pipe-проверкой.
- PowerShell 5.1 без `$OutputEncoding = UTF8` искажает кириллицу при передаче через pipe —
  ограничение консоли, не приложения; файлы пишутся в UTF-8 без BOM.
- Этап 5 (`cooking_time`) — не начат.

## Проблемы

- Нет.

## Следующий шаг

- Приёмка CLI пользователем.
- Этап 5 по плану; перед добавлением `cooking_time` выбрать стратегию
  обратной совместимости схемы (опциональное поле или миграция всех рецептов) — см. D3 и `DISCOVERY.md` §8.

## Нужные файлы

- `DISCOVERY.md`, `docs/plan.md`, `docs/architecture.md`, `AGENTS.md`, `rules/claude-mem.md`
- `src/recipe_finder/`, `tests/`
- `data/recipes.json`, `data/ingredients.json` (создаётся при запуске)
