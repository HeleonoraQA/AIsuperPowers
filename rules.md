# Правила проекта

Жёсткие правила для агента и контрибьюторов. Дополняют `AGENTS.md`.
Стек: Python 3.11+ (только stdlib в рантайме), pytest и ruff — dev-инструменты.

## Доступ к файлам
- `.env`, `.env.*`, `*.key`, `*.pem` — **полный запрет** на чтение и изменение.
  Задаётся в `opencode.json` (`read`/`edit` → `deny`), обойти нельзя.
- Запрет на `secrets/` действует на любой вложенности (паттерн `*secrets/*`).
- Реализация (OpenCode V2): глоб-паттерны `*.env`, `*.env.*`, `*secrets/*`, `*.key`, `*.pem`
  в секции `permissions` + дублирующий слой `policies` (`tool.use` → `deny`);
  policy-запрет не перекрывается сохранёнными разрешениями «Allow always».
  В V2 `*` совпадает и с `/`, поэтому отдельный префикс `**/` не нужен.
- Не изменять файлы за пределами проекта.
- Никогда не коммитить секреты, ключи, `.venv/`, `__pycache__/`,
  `.pytest_cache/`, `.ruff_cache/` и артефакты сборки.

## Права shell
- Без подтверждения разрешены только: `pytest *`, `ruff check *`, `ruff format *`,
  `git *` (кроме `git push` — он всегда `ask`), `ls *`.
- `git push` и `git push <аргументы>` — всегда `ask`, даже при совпадении с `git *`.
- `pytest` и `ruff` разрешены в любом виде, включая `ruff check . --fix`.
- Любая другая команда требует подтверждения (`ask`).

## Изменения и проверки
- Правка файлов (`edit`/`write`/`patch`) требует подтверждения.
- Git в проекте пока не подключён (решение пользователя): husky-хуки
  pre-commit/pre-push неактуальны. Вместо них — обязательная проверка
  `pytest` и `ruff check .` перед завершением задачи.
- Когда git будет подключён: перед коммитом `ruff check . && pytest`,
  сообщения коммитов — Conventional Commits (`type(scope): summary`).

## Память Claude-Mem
- Память подключена: OpenCode-плагин `@ephemushroom/opencode-claude-mem`,
  в Cursor — MCP `plugin-claude-mem-mcp-search`, воркер `http://localhost:37777`,
  проект `AIsp`.
- Перед задачей и при поиске прошлых решений использовать память
  (search → timeline → get_observations). После решения — `save_memory` / `mem-save`.
- Подробности: `rules/claude-mem.md`.

## Документация
- Меняя правила, права или структуру проекта, обновлять `AGENTS.md`,
  `docs/architecture.md` и `docs/progress.md`.
  Долгоживущие решения дублировать в Claude-Mem, отдельного `docs/memory.md` нет.
