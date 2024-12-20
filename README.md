# Docker Lab
Для запуска:
```
docker-compose up
```
## Задание
Цель лабораторной работы: собрать из исходного кода и запустить в Docker рабочее приложение с базой данных (любое open-source на выбор: Java, Python/Django/Flask, Golang).

### Требования:
1. Образ должен быть **легковесным**.
2. Использовать базовые **легковесные образы** (например, Alpine).
3. Вся конфигурация приложения должна быть реализована через **переменные окружения**.
4. **Статика** (зависимости) должна быть вынесена в **внешний том** (`volume`).
5. Создать файл `docker-compose.yml` для **сборки** и **запуска** приложения.
6. В `docker-compose.yml` необходимо использовать базу данных (например, PostgreSQL, MySQL, MongoDB и т.д.).
7. При старте приложения должны быть учтены **автоматические миграции**.
8. Контейнер должен запускаться от **непривилегированного пользователя**.
9. После установки всех необходимых утилит, должен **очищаться кеш**.

---

### Описание работы

Это мини-приложение для управления списком пользоваетелей:

- Редактирование списка пользователей в базе данных.
- Просмотр полного списка пользователей, сохранённого в базе данных PostgreSQL.


Пример интерфейса:  
![Интерфейс приложения](/images/example-site.png)

### Dockerfile
Контейнер будет основываться на базовом образе Python 3.12. Для минимизации объема использованной памяти выбрана версия на основе Alpine.
```Docker
FROM python:3.12-alpine
```
Далее создается рабочая директория `/app`, где будут находиться все файлы приложения.
```Docker
WORKDIR /app
```

Отдельным слоем копируется файл с необходимыми библиотеками, так как библиотеки не так часто обновляются, и данный слой будет закеширован.
```Docker
COPY requirements.txt ./requirements.txt
```
Удаляется весь кеш и устанавливаются зависимости.
```Docker
RUN pip install -r requirements.txt --no-cache && \
    rm -rf /var/cache/apk/* && \
    rm -rf /root/.cache/pip
```
Копируется остальное содержимое текущей директории.
```Docker
COPY . .
```
Задаются права доступа для рабочей директории.
```Docker
RUN chmod -R 777 /app
```
Задается порт, по которому будет работать приложение.
```Docker
EXPOSE 3000
```
Создается новый **непривилегированный** пользователь, от имени которого будет запускаться программа.
```Docker
RUN adduser --disabled-password appuser
USER appuser
```
Запускается файл с командами миграции и запуска приложения.
```Docker
ENTRYPOINT [ "./entrypoints.sh" ]
```
Содержимое `entrypoints.sh`
```Sh
#!/bin/sh
python3 -m flask db init
python3 -m flask db migrate
python3 -m flask db upgrade
python3 main.py
```

### Docker-compose
```yml
version: '3'

services:
  database:
    image: postgres:11-alpine
    ports:
      - "5432:5432"
    container_name: postgres
    environment:
      POSTGRES_PASSWORD: "12345678"
      POSTGRES_USER: "postgres"
      POSTGRES_DB: "USER_MANAGEMENT"
      LC_ALL: en_US.UTF-8
    volumes:
      - pg_data:/var/lib/postgresql/data
    networks:
      - docker_network
  app:
    image: app
    build: .
    environment:
      POSTGRES_HOST: "postgres"
      POSTGRES_PASSWORD: "12345678"
      POSTGRES_USER: "postgres"
      POSTGRES_DB: "USER_MANAGEMENT"
      POSTGRES_PORT: "5432"
      APP_PORT: "5000"
      FLASK_APP : "./src/__init__.py"
    depends_on:
      - database
    ports:
      - "5000:5000"
    volumes:
      - static:/app/src/templates
    networks:
      - docker_network

volumes:
  pg_data:
    driver: local
  static:
    driver: local  

networks:
  docker_network:
    driver: bridge
```
### Описание:

1. **Сервис `database`**:
   - В качестве образа используется **легковесный** образ `postgres:11-alpine`.
   - Указываются **переменные окружения**, необходимые для работы базы данных: `POSTGRES_DB`, `POSTGRES_USER` и `POSTGRES_PASSWORD`.
   - Порты **5432** пробрасываются для подключения к базе данных.
   - В **volumes** монтируется том `pg_data`, который сохраняет данные базы между перезапусками контейнера.
   - Устанавливается подсеть `docker_network`  

2. **Сервис `app`**:
   - Для приложения используется собственный образ.
   - Приложение подключается к базе данных с помощью переменных окружения, таких как `POSTGRES_HOST`, `POSTGRES_PASSWORD`, `POSTGRES_USER`, `POSTGRES_DB` и др.
   - Порт **5000** пробрасываются для взаимодействия с приложением.
   - Монтируется **внешний том** для статики приложения: `static`.
   - Устанавливается подсеть `docker_network`.
   
В проекте вынесены тома для хранения данных и статики отдельно, что позволяет использовать их для взаимодействия между контейнерами. 

![Пример запуска](/images/example-terminal.png)

