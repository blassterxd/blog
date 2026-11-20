# Блог (blog)

Django-блог (Django 5.2, Bootstrap 4 через django-bootstrap4). Все читают публикации,
создавать и редактировать их могут только зарегистрированные авторы, и только свои.

## Возможности

- главная со всеми публикациями (новые первыми);
- регистрация, вход и выход (выход только методом POST);
- создание и редактирование публикаций;
- чужую публикацию изменить нельзя (ответ 404);
- настроенная админка: автор, дата, поиск, фильтры.

## Локальный запуск (Python 3.12)

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows:     .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Тесты: `python manage.py test`

## Развёртывание на сервере (Docker Compose)

1. `ssh student@192.168.1.11`, затем `newproject ФАМИЛИЯ-blog`.
   Команда создаст каталог и файл `.env` с портами (`PORT1`).
2. Загрузка кода:
   ```bash
   cd ~/projects/ФАМИЛИЯ-blog
   git init -q
   git remote add origin https://github.com/ЛОГИН/blog.git
   git pull origin main
   ```
3. Допишите в `.env` переменные из таблицы ниже (образец в `.env.example`).
4. `docker compose up -d --build`, затем `docker compose ps` (статус `Up (healthy)`).
5. Администратор: `docker compose exec web python manage.py createsuperuser`.
6. Откройте `http://192.168.1.11:PORT1/`.

Обновление: `git pull origin main`, затем `docker compose up -d --build`.

## Переменные окружения (файл `.env`, в репозиторий не входит)

| Переменная | Назначение | Пример |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | секретный ключ Django | длинная случайная строка |
| `DJANGO_DEBUG` | режим отладки | `False` |
| `DJANGO_ALLOWED_HOSTS` | допустимые адреса через запятую | `192.168.1.11,localhost,127.0.0.1` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | адрес сайта с портом | `http://192.168.1.11:20010` |
| `DJANGO_USE_HTTPS` | защищённые cookie (при HTTPS) | `False` |
| `SQLITE_PATH` | путь к базе внутри контейнера | `/app/data/db.sqlite3` |
| `PORT1` | внешний порт (выдаёт `newproject`) | `20010` |

База хранится в томе Docker и не теряется при пересборке.