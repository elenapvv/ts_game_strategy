## Команды для запуска

Чтобы поднять базу данных:

    > docker-compose down
    > docker-compose up --build

Чтобы заполнить базу данных:

    > python data_operations/data_preparation.py

(Данные собраны с 01/06/07 по 14/01/22 включительно десяти российских компаний).

Запускаем:

    > python data_operations/trader.py

Алгоритм Hedge реализован в algs/hedge.py, в переменной класса ETA можно задать параметр эта.
Смотрим результаты в папке /results (имя файла - "ETA=<параметр эта>, time=<время в формате %d.%m.%Y %H.%M.%S>.log")
