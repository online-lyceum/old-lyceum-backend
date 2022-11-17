# Асинхронная версия API расписания для проекта Лицей в Цифре

### [Пользовательская документация на swagger](https://swagger.lava-land.ru/)

## Быстрая установка через Github 
### Данный вид установки не поддерживает изменение исходного кода.
### Необходимые пакеты
Установите в вашу систему python3, python3-pip, python3-venv и docker.

### Создание виртуального окружения
Клонировать репозиторий не надо.
```shell
python3 -m venv venv  # Создание окружения
source ./venv/bin/activate  # Активация окружения
# Установка кода из GitHub через pip
pip3 install "git+https://github.com/prostoLavr/async_lyceum_api.git"
```
### Запуск
```shell
# Запуск базы данных PostgreSQL
docker run --rm -it -e POSTGRES_PASSWORD="password" -d \
                 -p "5432:5432" --name "postgres" postgres:15.1
# Запуск проекта. Чтобы узнать больше, введите async_lyceum_api --help
async_lyceum_api --web-port 8080
```

## Установка из исходников в виртуальное окружение
### Самый удобный способ дла разботки API.
### Необходимые пакеты
Установите python3, python3-pip, python3-venv и docker. 
Вместо docker вы можете использовать нативно установленную postgres 15.1, 
но использование docker предпочтительнее.

### Клонировение исходного кода
```shell
git clone https://github.com/prostoLavr/async_lyceum_api.git
```
### Создание виртуального окружения
```shell
python3 -m venv venv
source ./venv/bin/activate
```
### Инициализация режима разработки
Режим разработки это установка python пакета, 
обновляющегося в реальном времени. Это полезно для разработки, так как
не нужно каждый раз пересобирать и переустанавливать пакет, но после
установки собранного whl пакета этот режим деактивируется. 
```shell
pip3 install -e .  # <- Точка в конце обязательна!
```

### Запуск в режеме для разрабоки
```shell
# Запуск postgresql в docker
docker run --rm -it -e POSTGRES_PASSWORD="password" -d \
                 -p "5432:5432" --name "postgres" postgres:15.1

# Запустите "async_lyceum_api --help" чтобы узнать больше доступных аргументов.
async_lyceum_api --web-port 8080
```

## Установка в docker образ

### Необходимые пакеты
Установите в вашу систему docker и docker-compose.

### Клонирование исходного кода
```shell
git clone https://github.com/prostoLavr/async_lyceum_api.git
```
Скорее всего вы хотите проверить работу API через свой браузер. Для этого 

### Сборка пакета и запуск проекта
Использование `-f docker-compose-dev.yml` открывать порт 8080
```shell
docker build -t async-lyceum-api .  # <- Точка в конце обязательна!
docker-compose up -d -f docker-compose-dev.yml
```
