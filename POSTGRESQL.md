## Установка, настройка и развертывание PostgreSQL:

### Шаг 1: Установка PostgreSQL

1. **Установка PostgreSQL:**
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```

2. **Проверка статуса службы PostgreSQL:**
   ```bash
   sudo systemctl status postgresql
   ```

   Если служба не запущена, запустите её:
   ```bash
   sudo systemctl start postgresql
   ```

   Также можно включить автозапуск при загрузке системы:
   ```bash
   sudo systemctl enable postgresql
   ```

### Шаг 2: Настройка PostgreSQL

1. **Переключение на пользователя `postgres`:**
   ```bash
   sudo -i -u postgres
   ```

2. **Запуск psql (интерфейса командной строки PostgreSQL):**
   ```bash
   psql
   ```

3. **Создание нового пользователя (роли) в PostgreSQL:**
   ```sql
   CREATE USER @myuser WITH PASSWORD '@mypassword';
   ```

4. **Создание новой базы данных и предоставление доступа пользователю:**
   ```sql
   CREATE DATABASE @mydatabase;
   GRANT ALL PRIVILEGES ON DATABASE @mydatabase TO @myuser;
   ```

5. **Выход из psql и пользователя `postgres`:**
   ```bash
   \q
   exit
   ```

6. **Шаг 1: Предоставление прав на схему `public`:**

1. **Подключитесь к базе данных с правами суперпользователя:**
   ```bash
   sudo -u postgres psql -d @mydatabase
   ```

2. **Предоставьте права на создание объектов в схеме `public`:**
   ```sql
   GRANT ALL ON SCHEMA public TO @myuser;
   ```

   public - это уже созданная по умолчанию схема, можно создать свою собственную схему и использовать ее при запросах

3. **Выход из psql:**
   ```bash
   \q
   ```

Теперь у вас должно быть разрешение на создание объектов в схеме `public`, и ваш скрипт должен работать без ошибок.

### Шаг 3: Установка psycopg2

1. **Установка Python и pip (если они еще не установлены):**
   ```bash
   sudo apt install python3 python3-pip
   ```

2. **Установка psycopg2:**
   ```bash
   pip3 install psycopg2-binary
   ```

### Шаг 4: Подключение к PostgreSQL из Python

Теперь вы можете подключиться к PostgreSQL из Python и выполнять операции с базой данных. Вот пример кода:

```python
import psycopg2

# Подключение к базе данных
conn = psycopg2.connect(
    dbname="mydatabase",
    user="myuser",
    password="mypassword",
    host="localhost",
    port="5432"
)

# Создание курсора
cur = conn.cursor()

# Пример создания таблицы
cur.execute("""
    CREATE TABLE IF NOT EXISTS test_table (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL
    )
""")

# Пример вставки данных
cur.execute("INSERT INTO test_table (name) VALUES (%s)", ("Test Name",))

# Сохранение изменений
conn.commit()

# Закрытие курсора и соединения
cur.close()
conn.close()
```

Теперь у вас есть полностью настроенная среда для работы с PostgreSQL из Python с использованием `psycopg2`. Вы можете создавать таблицы, схемы и записывать данные в базу данных.

## Снести PostgresSQL из системы

1. Удаление PostgreSQL
Ubuntu/Debian:
```bash
# Остановка сервиса PostgreSQL
sudo systemctl stop postgresql

# Удаление пакетов PostgreSQL
sudo apt-get purge postgresql*

# Удаление конфигурационных файлов и данных
sudo rm -rf /etc/postgresql/ /var/lib/postgresql/ /var/log/postgresql/

# Удаление пользователя и группы PostgreSQL
sudo deluser --remove-home postgres
sudo delgroup postgres
```