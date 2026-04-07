# Как запустить:
## 1. Зайдите в командную строку и введите:

wsl -d Ubuntu

cd /mnt/c/l_a_b

python3 -m venv venv

source venv/bin/activate

## 2. Активируйте WSL интеграцию в Docker Desktop

## 3. Запустите проект в командной строке (в WSL):

./memory_limits.sh

./run.sh

## Чтобы запустить приложение заново, введите команды:

docker stop $(docker ps -aq) 2>/dev/null

docker rm $(docker ps -aq) 2>/dev/null

docker network prune -f

docker volume prune -f

# Задача лабораторной работы:

Разработать и протестировать Spark приложение для анализа больших данных, работающее поверх распределенной файловой системы Hadoop HDFS, с оценкой производительности в различных конфигурациях кластера и применением оптимизаций.

# Решение, реализованное в работе:

## 1. Подготовка данных

Сгенерирован CSV файл с 150,000 строк и 8 признаками:

- Числовые: user_id, age, purchases

- Вещественные: salary, rating

- Категориальные: city (6 городов), is_active (бинарный)

- Дата/время: registration_date

## 2. Развертывание Hadoop кластера

Использованы Docker контейнеры с образами bde2020/hadoop-namenode и bde2020/hadoop-datanode.

Размер блока HDFS: 128 MB
 
Ограничение памяти с помощью скрипта memory_limits.sh:

- Docker контейнеры: 1.5-2 GB

- Spark executor/driver: 1 GB

## 3. Spark Application

Разработано Spark приложение (spark_app.py), выполняющее:

### Аналитические задачи:

1. Статистика по городам - группировка пользователей по городам с подсчетом среднего дохода и рейтинга

<img width="661" height="245" alt="image" src="https://github.com/user-attachments/assets/f19d8cc9-be92-4735-bead-9af9ba031012" />

2. Анализ активных пользователей - фильтрация и агрегация по полю is_active

<img width="435" height="48" alt="image" src="https://github.com/user-attachments/assets/0d6d7eaa-f187-4daa-a119-a7f71397a40a" />

3. Категоризация трат - разделение пользователей на категории Low/Medium/High по количеству покупок

<img width="399" height="173" alt="image" src="https://github.com/user-attachments/assets/e2a1af4d-f123-45da-ae5b-4ada435ee69e" />


### Замер производительности:

<img width="677" height="62" alt="image" src="https://github.com/user-attachments/assets/a9d7f6ce-7582-482a-a463-94190b277618" />

<img width="679" height="251" alt="image" src="https://github.com/user-attachments/assets/c70e7b94-4595-469e-8ad2-2308ae487031" />

### Логирование результатов:

Логи отражены в папке result/logs

## 4. Spark Application с Hadoop, 1 NameNode, 3+ DataNode:

Были созданы 3 контейнера DataNode и на них выполнено приложение Spark

## 5. Эксперименты:

Реализован автоматизированный скрипт запуска run_wsl.sh:

<img width="640" height="332" alt="image" src="https://github.com/user-attachments/assets/7934fcbf-a616-4ed8-b914-47613be1e359" />

## 6. Оптимизация Spark Application:

Реализованы следующие оптимизации:

1. Адаптивное количество партиций:

...
if use_optimization:
        spark_builder = spark_builder \
            .config("spark.sql.shuffle.partitions", "8") \
            .config("spark.default.parallelism", "8") \
            ...

2. Кэширование данных:

...
df = df.persist(StorageLevel.MEMORY_AND_DISK)
df.count()
...

3. Включение адаптивных запросов:

...
.config("spark.sql.adaptive.enabled", "true") \
.config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
...
.config("spark.sql.adaptive.skewJoin.enabled", "true")
...

## 7. Сравнение результатов и визуализация:

Создан скрипт auto_plot_results.py для автоматического построения графиков:

### Создаваемые графики:
1. execution_time.png - сравнение времени выполнения

<img width="1782" height="884" alt="image" src="https://github.com/user-attachments/assets/f2b4897f-e257-43de-a168-e546fcd514d3" />

2. nodes_comparison.png - сравнение 1 DN vs 3 DN

<img width="1482" height="881" alt="image" src="https://github.com/user-attachments/assets/acd4846d-a5da-4b43-9234-d7a8a5b400ac" />

3. memory_usage.png - использование RAM

<img width="1782" height="879" alt="image" src="https://github.com/user-attachments/assets/efe38b6d-a93b-4665-b5d1-35e1660e2a85" />

4. time_vs_memory.png - компромисс время-память

<img width="1477" height="1180" alt="image" src="https://github.com/user-attachments/assets/0cf3538a-7fd3-4363-b275-0526a83fe877" />

5. trend.png - тренд производительности

<img width="1482" height="884" alt="image" src="https://github.com/user-attachments/assets/7e095398-742b-4873-9f2a-52ed979f2e81" />

6. speedup.png - ускорение от оптимизации

<img width="1182" height="883" alt="image" src="https://github.com/user-attachments/assets/5a143ef6-eb13-4c52-a5af-c15385ecc7e7" />

7. time_breakdown.png - разбивка времени выполнения

<img width="1781" height="883" alt="image" src="https://github.com/user-attachments/assets/4355b514-69fa-44a7-a66c-ca87109fab3e" />

### HTML отчет:

Сгенерирован интерактивный HTML отчет с таблицами, графиками и выводами.

# Выводы:

- Лучшее время: 5.95 секунд в конфигурации 3DN_Optimized

- Лучшее использование RAM: 38 MB в конфигурации 1DN_Optimized

- Оптимизация на 1 DataNode дала ускорение в 1.15x

- Масштабирование до 3 DataNodes дало ускорение в 1.24x






