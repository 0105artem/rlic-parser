# [Парсер Лицензий Образовательных Организаций](https://artemkornilov.ru/docs)
Добро пожаловать в Парсер Лицензий Образовательных Организаций (Rlic-Parser). Парсер забирает из [публичного реестра лицензий Рособрнадзора](https://islod.obrnadzor.gov.ru/rlic/) данные образовательных организаций с действующей лицензией. Данные сохраняются в базу данных PostgreSQL. Скачивайте и просматривайте свежие лицензии в считанные секунды с помощью API.
## API Usage Examples
- Get Licenses: Получить не более 1000 лицензий из базы данных.
    ```
    curl -XGET -L 'https://artemkornilov.ru/licenses/limit=2&offset=0'
    ```
- Get License: Найти лицензию по `license_id` равному `000033a4-72aa-a35c-6571-97347cf20a72`.
    ```
    curl -XGET -L 'https://artemkornilov.ru/licenses/000033a4-72aa-a35c-6571-97347cf20a72'
    ```
- Get CSV url: Получить ссылку на csv файл содержащий все активные лицензии. 
    ```
    curl -XGET -L 'https://artemkornilov.ru/licenses/csv'
    ```
- Get CSV file: Скачать csv файл под названием `active_licenses_06-03-2023_15.13.25.zip`
    ```
    curl -XGET -L 'https://artemkornilov.ru/files/csv/active_licenses_06-03-2023_15.13.25.zip'
    ```
 
## [API Documentation](https://artemkornilov.ru/docs)
- Перейдите по ссылке https://artemkornilov.ru/docs чтобы увидеть полный список доступных запросов.

## Setup
Следуйте шагам описанными ниже, чтобы поднять окружение на локальной машине.

#### Dependencies
- python 3.7+
- Docker/Docker-Compose (optional) 
- PostgreSQL (опционально если используете Docker) 
- Redis (опционально если используете Docker) 
- Все python зависимости содержатся в [`parser/requirements.txt`](https://github.com/0105artem/rlic-parser/blob/main/parser/requirements.txt) и [`API/requirements.txt`](https://github.com/0105artem/rlic-parser/blob/main/API/requirements.txt)
            
### Docker
Если у вас установлен docker и docker-compose, то данный способ установки рекомендуемый, в противном случае следуйте инструкция по установке без Docker.
#### Setting up the parser
1. В терминале откройте директорию `./parser`, содержащую `docker-compose.yml` file.
2. Создайте `.env` файл, скопировав в него содержимое файла `parser/.env.sample`. Измените следующие переменные:
   - `POSTGRES_PASSWORD` -- пароль к PostgreSQL пользователя postgres
   - `DB_USERNAME` -- имя нового пользователя PostgreSQL
   - `DB_USER_PASSWORD` -- пароль пользователя с ником `DB_USERNAME`
   - `REDIS_PASSWORD` -- пароль для Redis Server
3. Пропишите команду `docker-compose up --build -d` чтобы запустить сервис. Вы увидите как Docker построит и запустит контейнеры с парсером, Redis и PostgreSQL.

#### Setting up the API
1. После запуска Docker контейнеров с парсером, PostgreSQL и Redis откройте директорию `./API`.
2. Создайте `.env` файл, скопировав в него содержимое файла `API/.env.sample`. Измените переменные `POSTGRES_PASSWORD`, `DB_USERNAME`, `DB_USER_PASSWORD`, `REDIS_PASSWORD` в соответствии с `parser/.env` файлом.
3. Пропишите команду `docker-compose up --build -d` чтобы запустить сервер. Вы увидите как Docker построит и запустит контейнер с API.
4. Зайдите в браузер и перейдите по адресу `http://localhost:8000/`. Если вы увидите документацию к API, значит вы успешно запустили сервер и готовы к использованию API.

### Non-dockerized setting up
Для работы данной установки понадобятся PostgreSQL и Redis-Server, локально установленные на вашей системе.
#### Setting up the parser
1. В терминале откройте директорию `./parser`
2. Создайте `.env` файл, скопировав в него содержимое файла `parser/.env.sample`. Измените следующие переменные:
   - `POSTGRES_PASSWORD` -- пароль к PostgreSQL пользователя postgres
   - `DB_USERNAME` -- имя нового пользователя PostgreSQL
   - `DB_USER_PASSWORD` -- пароль пользователя с ником `DB_USERNAME`
   - `REDIS_PASSWORD` -- пароль для Redis Server
3. Создайте виртуальное окружение, используя следующую команду
    ```shell script
    $ python3 -m venv venv
    ```
4. Активируйте виртуальное окружение
    Linux:
    ```shell script
    $ source /venv/bin/active
    ```
    Windows:
    ```shell script
    > ./venv/bin/active
    ```
5. Убедитесь что ваше виртуальное окружение активно и установите все необходимые зависимости следующей командой:
    ```shell script
    $ pip install -r requirements.txt
    ```
6. Запустите парсер командой ниже:
    ```shell script
    $ python main.py
    ```

#### Setting up the API
1. В терминале откройте директорию `./API`.
2. Создайте `.env` файл, скопировав в него содержимое файла `API/.env.sample`. Измените переменные `POSTGRES_PASSWORD`, `DB_USERNAME`, `DB_USER_PASSWORD`, `REDIS_PASSWORD` в соответствии с `parser/.env` файлом.
3. Создайте виртуальное окружение, используя следующую команду
    ```shell script
    $ python3 -m venv venv
    ```
4. Активируйте виртуальное окружение
    Linux:
    ```shell script
    $ source /venv/bin/active
    ```
    Windows:
    ```shell script
    > ./venv/bin/active
    ```
5. Убедитесь что ваше виртуальное окружение активно и установите все необходимые зависимости следующей командой:
    ```shell script
    $ pip install -r requirements.txt
    ```
6. После успешной установки пакетов пропишите команду для запуска сервера:
    ```shell script
    $ uvicorn main:app --host 0.0.0.0 --port 8000
    ```
7. Зайдите в браузер и перейдите по адресу `http://localhost:8000/`. Если вы увидите документацию к API, значит вы успешно запустили сервер и готовы к использованию API.

### Обратная связь
- 0105artem@gmail.com
- https://t.me/artemk0rn1lov
