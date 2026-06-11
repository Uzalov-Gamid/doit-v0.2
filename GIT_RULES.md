# Правила работы с Git

После появления MVP проект ведется через отдельную рабочую ветку `develop`. Это помогает держать `main` стабильной, а текущую разработку вести без риска сломать уже готовую версию.

## Ветки

- `main` - стабильная ветка для готовых версий проекта;
- `develop` - рабочая ветка для объединения новых задач после MVP;
- `feature/*` - ветки для новых функций, создаются от `develop`;
- `fix/*` - ветки для исправлений, создаются от `develop`;
- `release/*` - ветки для подготовки версии, если проект станет больше.

Примеры:

```bash
git switch develop
git pull
git switch -c feature/task-tests
git switch -c fix/login-validation
```

## Основной процесс после MVP

1. Перейти на `develop`.
2. Обновить ветку.
3. Создать `feature/*` или `fix/*`.
4. Сделать изменения и тесты.
5. Закоммитить изменения.
6. Слить ветку обратно в `develop`.
7. Запушить `develop`.
8. После финальной проверки слить `develop` в `main`.

Команды:

```bash
git switch develop
git pull
git switch -c feature/example-task

# работа над задачей
git add .
git commit -m "feat: добавить пример функции"

git switch develop
git merge --no-ff feature/example-task -m "merge: добавить пример функции"
git push origin develop
```

Слияние в `main` делается только после проверки:

```bash
git switch main
git pull
git merge --no-ff develop -m "merge: обновить стабильную версию"
git push origin main
```

## Коммиты

Коммиты пишутся на русском языке. Сообщение должно кратко объяснять реальное изменение.

Формат:

```text
тип: что сделано
```

Основные типы:

- `docs` - документация;
- `feat` - новая функция;
- `fix` - исправление;
- `style` - стили интерфейса;
- `test` - тесты;
- `docker` - Docker и Docker Compose;
- `chore` - служебные изменения.

Примеры хороших коммитов:

```text
docs: добавить стартовую документацию
feat: добавить регистрацию пользователя
feat: добавить создание задач
fix: исправить фильтрацию задач по статусу
style: улучшить адаптивность личного кабинета
docker: добавить сервис PostgreSQL
test: расширить тесты задач
```

Исправления лучше делать отдельными небольшими коммитами с префиксом `fix`, если это действительно отдельное исправление.

## Что нельзя пушить

В репозиторий нельзя добавлять:

- `.env`;
- пароли;
- токены;
- секретные ключи;
- логи;
- временные файлы;
- локальные настройки IDE;
- дампы базы данных с реальными данными;
- локальные промты, черновики постановки задачи и личные заметки.

## Первый коммит

```bash
git init
git add README.md docs/technical-specification.md .gitignore .env.example LICENSE GIT_RULES.md
git commit -m "docs: добавить стартовую документацию"
```

## Создание feature-ветки

```bash
git switch develop
git pull
git checkout -b feature/tasks-crud
```

После завершения задачи изменения объединяются в `develop`. В `main` попадает только проверенная версия из `develop`.

## Создание fix-ветки

```bash
git switch develop
git pull
git switch -c fix/task-status-validation
```

Исправления коммитятся отдельными небольшими коммитами:

```text
fix: исправить валидацию статуса задачи
```

## Проверки перед merge

Перед слиянием feature/fix-ветки в `develop` нужно выполнить:

```bash
docker compose exec web python manage.py check
docker compose exec web python manage.py test accounts tasks activity
```

Если доступна старая форма Compose:

```bash
docker-compose exec web python manage.py check
docker-compose exec web python manage.py test accounts tasks activity
```

## GitHub Issues

Для MVP используются GitHub Issues. Каждая крупная задача должна быть оформлена отдельным issue.

Рекомендуемый порядок:

1. создать issue;
2. взять issue в работу;
3. выполнить задачу в отдельной ветке;
4. сделать понятные коммиты;
5. закрыть issue после проверки результата.
