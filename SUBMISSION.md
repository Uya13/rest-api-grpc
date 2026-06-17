# Формат сдачи работы

## 1. GitHub-репозиторий

Ссылка на репозиторий:

```text
https://github.com/Uya13/rest-api-grpc
```

В репозитории есть файлы:

- `docker-compose.yml`
- `auth-service/app.py`
- `auth-service/Dockerfile`
- `todo-service/app.py`
- `todo-service/Dockerfile`
- `nginx/default.conf`

## 2. Скриншоты работы микросервисов

Перед скриншотами запустить:

```bash
docker compose up --build
```

Команды для проверки сервисов напрямую:

```bash
curl http://localhost:5000/health
curl http://localhost:5001/health
curl http://localhost:5001/todos
```

Команда `curl http://localhost:5001/todos` должна вернуть `401`, потому что запрос выполняется без токена.

## 3. Скриншоты работы Nginx API Gateway

Проверка gateway:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/auth/health
```

Получение токена через gateway:

```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"student123"}'
```

Запрос к защищенному сервису через gateway:

```bash
curl http://localhost:8080/todos/ \
  -H "Authorization: Bearer <token>"
```

## Автоматическое сохранение вывода curl

После запуска контейнеров можно выполнить:

```bash
python scripts/capture_checks.py
```

Скрипт сохранит вывод запросов в:

```text
screenshots/nginx-gateway-curl-results.txt
```
