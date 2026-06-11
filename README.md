# DoIt v0.2

Учебное веб-приложение для учета личных и рабочих задач пользователей.

Проект выполняется в рамках индивидуальной дистанционной практики.

**Сроки:** 09.06.2026 - 27.06.2026

## Цель проекта

Разработать простую систему управления задачами, в которой пользователь может зарегистрироваться, войти в личный кабинет, создавать задачи, менять их статус, искать и фильтровать список задач, а также видеть базовую статистику.

## Основные функции MVP

- регистрация пользователя;
- вход и выход из системы;
- роли `user` и `admin`;
- личный кабинет пользователя;
- создание, редактирование и удаление задач;
- изменение статуса задачи;
- статусы задач: `Новая`, `В работе`, `Выполнена`;
- поиск и фильтрация задач;
- статистика задач;
- журналирование действий пользователей;
- адаптивный интерфейс.

## Стек

- Frontend: HTML, CSS, JavaScript;
- Backend: Python, Django;
- Database: PostgreSQL;
- Containerization: Docker, Docker Compose;
- Version control: Git, GitHub.

## Структура проекта

```text
.
├── app/                         # Django-проект и приложения
│   ├── accounts/                # Регистрация, вход, профиль
│   ├── activity/                # Журнал действий
│   ├── config/                  # Настройки Django
│   ├── static/                  # CSS и JavaScript
│   ├── tasks/                   # Задачи и личный кабинет
│   └── templates/               # Django templates
├── docs/                        # Документация проекта
├── .env.example                 # Пример переменных окружения
├── .gitignore                   # Исключения для Git
├── docker-compose.yml           # Локальный запуск сервисов
├── Dockerfile                   # Сборка Django-приложения
├── GIT_RULES.md                 # Правила работы с Git
├── LICENSE                      # Лицензия проекта
├── README.md                    # Описание проекта
└── requirements.txt             # Python-зависимости
```

## Запуск через Docker

1. Создать локальный `.env` на основе примера:

```bash
cp .env.example .env
```

2. Запустить проект:

```bash
docker compose up --build
```

Если в системе доступна только старая форма команды, можно использовать:

```bash
docker-compose up --build
```

3. Открыть приложение:

```text
http://localhost:8000
```

Сервисы:

- `web` - Django-приложение;
- `database` - PostgreSQL.

Миграции Django выполняются автоматически при старте контейнера `web`.

## Быстрый запуск для новичка

Если Docker уже установлен:

```bash
cp .env.example .env
docker compose up --build
```

После запуска открыть:

```text
http://localhost:8000
```

Если команда `docker compose` недоступна, использовать вариант с дефисом:

```bash
docker-compose up --build
```

Остановить проект:

```bash
docker compose down
```

или:

```bash
docker-compose down
```

## Git-процесс после MVP

После появления MVP используется ветка `develop`:

- `main` - стабильная версия;
- `develop` - рабочая ветка;
- `feature/*` - новые задачи от `develop`;
- `fix/*` - исправления от `develop`.

Обычный порядок работы:

```bash
git switch develop
git pull
git switch -c feature/example-task
```

После выполнения задачи:

```bash
git add .
git commit -m "feat: добавить пример функции"
git switch develop
git merge --no-ff feature/example-task -m "merge: добавить пример функции"
git push origin develop
```

## Основные страницы

- `http://localhost:8000/accounts/register/` - регистрация;
- `http://localhost:8000/accounts/login/` - вход;
- `http://localhost:8000/` - личный кабинет и задачи;
- `http://localhost:8000/admin/` - Django admin.

## Создание администратора

После запуска контейнеров можно создать администратора:

```bash
docker compose exec web python manage.py createsuperuser
```

Если используется старая форма команды:

```bash
docker-compose exec web python manage.py createsuperuser
```

## Проверка проекта

Запуск Django system check:

```bash
docker compose exec web python manage.py check
```

Запуск тестов:

```bash
docker compose exec web python manage.py test accounts tasks activity
```

Для окружений со старой формой Compose:

```bash
docker-compose exec web python manage.py check
docker-compose exec web python manage.py test accounts tasks activity
```

## Журналирование

В журнал действий записываются:

- регистрация;
- вход;
- выход;
- создание задачи;
- редактирование задачи;
- удаление задачи;
- изменение статуса задачи.

Записи доступны в Django admin в разделе `Журнал действий`.

## Итоговые материалы для сдачи

- исходный код проекта;
- README с инструкцией запуска;
- техническое задание;
- GitHub-репозиторий с историей коммитов;
- список задач в GitHub Issues;
- демонстрация работы MVP.
