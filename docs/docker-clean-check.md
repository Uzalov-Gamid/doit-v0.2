# Проверка Docker-запуска на чистом окружении

Эта проверка запускает проект в отдельном Docker Compose project, чтобы не трогать текущие контейнеры и локальную базу.

## Команды

Остановить и удалить временные ресурсы, если они остались от прошлой проверки:

```bash
docker-compose -p doit_clean_check down -v --remove-orphans
```

Собрать образ:

```bash
docker-compose -p doit_clean_check build
```

Применить миграции на чистой базе:

```bash
docker-compose -p doit_clean_check run --rm web python manage.py migrate
```

Проверить настройки Django:

```bash
docker-compose -p doit_clean_check run --rm web python manage.py check
```

Запустить тесты:

```bash
docker-compose -p doit_clean_check run --rm web python manage.py test accounts tasks activity
```

Проверить demo-данные:

```bash
docker-compose -p doit_clean_check run --rm web python manage.py seed_demo_data
```

Удалить временные контейнеры и volume:

```bash
docker-compose -p doit_clean_check down -v --remove-orphans
```

## Ожидаемый результат

- образ `web` собирается без ошибок;
- PostgreSQL стартует и становится healthy;
- миграции применяются на пустой базе;
- Django `check` проходит без ошибок;
- тесты завершаются с `OK`;
- demo-данные создаются командой `seed_demo_data`.
