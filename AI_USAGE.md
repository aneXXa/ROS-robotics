# Декларация использования ИИ

## PR03

- Использован ИИ: да
- Модель / среда: Cursor Agent, Cursor IDE
- Компоненты: пакет `patrol`, `evidence/pr03/*`, README, CI
- Характер помощи: каркас ноды, чистая функция, тесты, demo, CI под kit v1-w03
- Проверка: pytest, colcon build, topic info без/с remap, topic hz ≈ 10 Hz

## PR04

- Использован ИИ: да
- Модель / среда: Cursor Agent, Cursor IDE
- Компоненты: параметры и валидация в `patrol`, `evidence/pr04/*`, CI под kit v1-w04
- Характер помощи: `declare_parameter` + callback, recreate таймера, тесты 0/neg/NaN/10→5, parameters.md
- Проверка: pytest 8 passed; `param set` 5.0 → hz≈5; `param set` 0.0 отклонён; `/clear`; `action list` → `rotate_absolute`
