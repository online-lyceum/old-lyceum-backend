# Асинхронная версия API расписания для проекта Лицей в Цифре
### [Пользовательская документация на Swagger (test)](https://dev.lava-land.ru/api/docs)
### [Пользовательская документация на ReDoc (test)](https://dev.lava-land.ru/api/redoc)

## Установка из исходников в виртуальное окружение
### Самый удобный способ дла разработки API.
### Необходимые пакеты
Установите python3, python3-pip, python3-venv и docker. 
Вместо docker вы можете использовать нативно установленную postgres 15.1, 
но использование docker предпочтительнее.

### Клонирование исходного кода
```shell
git clone https://github.com/online-lyceum/lyceum-backend.git
```
### Создание виртуального окружения
```shell
#На Linux
python3 -m venv venv
source ./venv/bin/activate
```
```shell
#На Windows
python -m venv venv
venv/Scripts/activate.bat
```
### Инициализация режима разработки
Режим разработки это установка python пакета, 
обновляющегося в реальном времени. Это полезно для разработки, так как
не нужно каждый раз пересобирать и переустанавливать пакет, но после
установки собранного whl пакета этот режим деактивируется. 
```shell
pip3 install -e .  # <- Точка в конце обязательна!
```

### Запуск в режиме для разработки
```shell
#На Linux

# Запуск postgresql в docker
docker run --rm -it -e POSTGRES_PASSWORD="password" -d -p "5432:5432" --name "postgres" postgres:15.1
# Инициализация создания базы данных (вызывается скрипт из этого проекта)
init_db
# Инициализация создания таблиц (вызывается скрипт из этого проекта)
init_models
# Запуск gunicorn с uvicorn worker'ом. по адресу 127.0.0.1:8080
gunicorn time_api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8080 
```
```shell
#На Windows

docker run --rm -it -e POSTGRES_PASSWORD="password" -d -p "5432:5432" --name "postgres" postgres:15.1
init_db
init_models
uvicorn time_api.main:app
```

## Установка в docker образ

### Необходимые пакеты
Установите в вашу систему docker и docker-compose.

### Клонирование исходного кода
```shell
git clone https://github.com/online-lyceum/lyceum-backend.git
```
Скорее всего вы хотите проверить работу API через свой браузер. Для этого 
После изменений таблиц базы данных необходимо заново инициализировать создание
таблиц в базе данных.
Обратите внимание, что если в вашей системе доступен docker compose (без тире)
лучше использовать его. docker-compose считается устаревшим:w
### Сборка пакета и запуск проекта
```shell
# Сборка docker образа
docker build -t time_api .  # <- Точка в конце обязательна!
# Запуск проекта на порту 8080
docker-compose up -d -f docker-compose-dev.yml
# Инициализация таблиц в базе данных
docker-compose exec -d api init_models
```
