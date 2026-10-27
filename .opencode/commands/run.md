---
description: Запуск Recipe Finder CLI
---

# Run - Запуск приложения

Запускает CLI приложение Recipe Finder:
```bash
python -m recipe_finder
```

**Использование:** `/run`

Можно передавать аргументы напрямую:
```bash
python -m recipe_finder --ingredients "картофель, масло, соль"
python -m recipe_finder --method oven --min-match-ratio 0.5
```

Список доступных флагов см. в `docs/architecture.md` раздел CLI.
