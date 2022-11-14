# Асинхронная версия API расписания для проекта Лицей в Цифре
## Назначение
Данное API предназначено для получения и создания уроков в системе 
"Лицей в цифре". Он позволяет ученикам и учителям смотреть своё расписание, 
учителя также имеют возможность создавать и редактировать расписание. 


## Подключение API
### Домены:
У API есть две версии stable и dev, стабильная и нестабильная соответственно.
Если ваше приложение находится на стадии разработки, рекомендуется использовать
dev версию API.

Stable: https://async-api.lava-land.ru
Dev: https://test-async-api.lava-land.ru

### Как написать запрос
Чтобы получить данные из API, необходимо послать GET запрос,
состоящий из двух частей: домен и URL-путь. Запись URL-пути всегда начинается
с символа `/`. Также у нас принято не писать `/` в конце запроса.
Например, https://test-async-api.lava-land.ru/school 
вернёт список всех школ. В данном примере URL-путь это `/school`. Далее для
обозначения запроса вместо https://test-async-api.lava-land.ru/school будет 
использоваться `/school`. А также под терминами URL и адрес будет 
подразумеваться URL-путь.

Названия URL запросов выбираются на основе REST-API. 
Знать что это такое необязательно. Детальнее почитать об этом можно 
[тут](https://habr.com/ru/post/483202/"). Говоря коротко, это способ именования
запросов, в котором используется следующая схема. `/объект` - чтобы получить 
список таких объектов. И `/объект/уникальный_номер_объекта` - чтобы получить 
объект с заданным в URL уникальным номером. В нашей системе принято завершать
запрос объектом, а не уникальным номером. Например, 
вот корректный запрос `/school/1/class` - это список классов в школе,
а вот некорректный `/school/1`, он работать не будет. Обратите внимание, что
для сокращения вместо `{уникальный_номер_объекта}` в документации 
используется `1`. 


### Как получить информацию из запроса
Данные в теле запроса (в разных системах встречаются названия body, data 
или text) передаются в формате JSON. ВСЕГДА любой запрос это словарь, внутри
этого словаря могут быть списки, строки, числа, булевы значения, 
но тело запроса должно быть словарём.

Ответ от сервера на запрос получения списка объектов (например `/school`) - это 
словарь с параметрами запроса и результатами поиска. Например, для `/school`
ответом будет следующий JSON `{"schools": [...]}`. А для `/school/1/class` 
`{"class_id": 1, "classes": [...]}`. 

`[...]` - это список объектов, содержимое
таких списков будет приведено далее.

Ответ от сервера на запрос получения объекта - это JSON с атрибутами 
(свойствами, параметрами) объекта. Например, `/teacher/1/info` вернёт
`{"teacher_id": 1, "name": "Иванов Иван Иванович"}`

### Список доступных URL:
Запрос `/school`
Ответ 
```json
{
    "schools": [
        {
            "school_id": 1,
            "name": "Лицей №2",
            "address": "Иркутск, ул. ... д. ..."
        },
        {
            "school_id": 2,
            "name": "Иркутский Гос.Университет",
            "address": "Иркутск"
        }
    ]
}
```
ПРОДОЛЖЕНИЕ СЛЕДУЕТ
Запрос `/school/1/class`
```json

```

Запрос `/school/1/lesson`
```json
```

Запрос `/class/1/lesson`
```json
```

## Установить серверную часть API с GitHub (Не подходит дла разработки)
### Зависимости
Установите в вашу систему python3-pip и python3-venv. Если вы используете 
Windows OS, то при установке python3 необходимо выбрать пункт "Add python to PATH" 


### Созадание виртуального окружения и установка API 
```shell
python3 -m venv venv  # Создаёт виртуальное окружение
source ./venv/bin/activate  # Активирует виртуальное окружение
pip3 install "git+https://github.com/prostoLavr/
              async_lyceum_api.git"  # Устанавливает код из GitHub (не из вашего каталога)
```
### Запуск
```shell
# Запуск PostgreSQL через Docker
docker run --rm -it -e POSTGRES_PASSWORD="password" -d \
                 -p "5432:5432" --name "postgres" postgres:15.1 

# Раскомментируйте следующую строку, чтобы очистить базу данных. 
# psql -h 0.0.0.0 -p 5432 -U postgres -c "DROP DATABASE db" 
# Создание базы данных внутри Docker контейнера
psql -h 0.0.0.0 -p 5432 -U postgres -c "CREATE DATABASE db"

# Запуск API. Введите "async_lyceum_api --help" чтобы посмотреть остальные аргументы.
async_lyceum_api --web-port 8080
```

## Установка из исходников с помощью виртуального окружения
ПРОДОЛЖЕНИЕ СЛЕДУЕТ
### Install packages
Install python3, python3-pip, python3-venv and docker. 
Instead docker you can install postgres 15.1 but docker is recommended.

### Clone source code
```shell
git clone https://github.com/prostoLavr/async_lyceum_api.git
```
### Initialize new virtual environment
```shell
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```
### Initialize development mode
Development mode is installing real-time updating python package.
It's useful to developers because you don't need building and
installing python package after edits.
```shell
pip3 install -e .  # <- This point in the end is important!
```

### Run native development mode
```shell
# Setup postgresql
docker run --rm -it -e POSTGRES_PASSWORD="password" -d \
                 -p "5432:5432" --name "postgres" postgres:15.1

# Uncomment ot recreate db if it exists
# psql -h 0.0.0.0 -p 5432 -U postgres -c "DROP DATABASE db" 
psql -h 0.0.0.0 -p 5432 -U postgres -c "CREATE DATABASE db"

# See "async_lyceum_api --help" for more arguments
async_lyceum_api --web-port 8080
```

## Setup from source code in Docker

### Install packages
Install python3-pip python3-venv, docker and docker-compose packages.

### Clone source code
```shell
git clone https://github.com/prostoLavr/async_lyceum_api.git
```
### Initialize new virtual environment
```shell
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

### Build python wheel package
This command will create python wheel file in dist directory.
```shell
python3 setup.py sdist bdist_wheel
```

### Build Docker image and up docker-compose services
```shell
docker build -t async-lyceum-api .  # <- This point in the end is important!
docker-compose up -d
```
