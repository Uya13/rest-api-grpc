# Практика: REST API, микросервисы, авторизация и Nginx API Gateway

Проект состоит из двух Python-микросервисов и Nginx API Gateway.

- `auth-service` выдает JWT-токен по логину и паролю.
- `todo-service` проверяет JWT и возвращает список задач пользователя.
- `nginx` принимает внешние запросы на порту `8080` и перенаправляет их в нужный сервис.

## Структура проекта

```text
auth-service/
  app.py
  Dockerfile
todo-service/
  app.py
  Dockerfile
nginx/
  default.conf
docker-compose.yml
README.md
```

## Запуск

```bash
docker compose up --build
```

## Тестовые пользователи

| Логин | Пароль | Роль |
| --- | --- | --- |
| `student` | `student123` | `user` |
| `admin` | `admin123` | `admin` |

## Проверка сервисов напрямую

```bash
curl http://localhost:5000/health
curl http://localhost:5001/health
curl http://localhost:5001/todos
```

## Проверка через Nginx API Gateway

```bash
curl http://localhost:8080/health
```

Получить токен:

```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"student123"}'
```

Сохранить токен в переменную:

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"student123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['token'])")
```

Получить задачи:

```bash
curl http://localhost:8080/todos/ \
  -H "Authorization: Bearer $TOKEN"
```

Создать задачу:

```bash
curl -X POST http://localhost:8080/todos/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Сделать скриншоты для отчета"}'
```

## GitHub

Репозиторий: https://github.com/Uya13/rest-api-grpc
