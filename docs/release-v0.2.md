# Релиз MVP v0.2

**Дата:** 11.06.2026

**Тег:** `v0.2-mvp`

**Статус:** стабильная MVP-версия для демонстрации и сдачи.

## Что вошло

- регистрация, вход и выход пользователя через стандартную Django auth;
- личный кабинет пользователя;
- создание, редактирование, удаление задач;
- смена статуса задачи;
- поиск, фильтрация и пагинация списка задач;
- статистика задач по статусам;
- журнал действий пользователей;
- отдельная страница журнала для администратора;
- Django admin;
- адаптивный frontend на Django templates;
- Docker-запуск с PostgreSQL;
- demo-данные через команду `seed_demo_data`;
- GitHub Actions для автоматического запуска проверок.

## Проверки

Перед релизом выполнены:

```bash
docker-compose -p release_check run --rm web python manage.py check
docker-compose -p release_check run --rm web python manage.py test accounts tasks activity
```

Результат:

- Django system check завершился без замечаний;
- найдено 73 теста;
- все тесты завершились с `OK`;
- GitHub Actions на ветке `develop` завершился успешно.

## Быстрый запуск

```bash
cp .env.example .env
docker compose up --build
```

Если доступна только старая форма Compose:

```bash
docker-compose up --build
```

Приложение открывается по адресу:

```text
http://localhost:8000
```

## Демо-данные

```bash
docker-compose exec web python manage.py seed_demo_data
```

По умолчанию создаются:

- `demo_user`;
- `demo_admin`;
- задачи разных статусов;
- записи журнала действий.
