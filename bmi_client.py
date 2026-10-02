"""Клиентское приложение для работы с историей расчётов BMI.
Подключается к PostgreSQL, сохраняет и читает записи.
"""

import psycopg2

# Параметры подключения (замените на свои, если нужно)
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "bmi_history"
DB_USER = "postgres"
DB_PASSWORD = "1"   # ← сюда впишите свой пароль от postgres

def get_connection():
    """Возвращает соединение с базой данных PostgreSQL."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )

def calculate_bmi(weight, height):
    """Вычисляет индекс массы тела.

    :param weight: масса тела в килограммах
    :param height: рост в метрах
    :return: значение BMI (float)
    """
    return weight / (height ** 2)

def get_category(bmi):
    """Возвращает текстовую категорию по значению BMI."""
    if bmi < 18.5:
        return "Недостаточная масса"
    if bmi < 25:
        return "Норма"
    if bmi < 30:
        return "Избыточная масса"
    return "Ожирение"

def save_bmi_record(weight, height, bmi, category):
    """Сохраняет результат расчёта в таблицу bmi_history."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO bmi_history
                    (weight, height, bmi, category)
                VALUES (%s, %s, %s, %s)
                """,
                (weight, height, bmi, category),
            )
            conn.commit()
            print("Запись успешно сохранена в базу данных.")
    finally:
        conn.close()

def show_history(limit=10):
    """Выводит последние записи из истории расчётов."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, weight, height, bmi, category,
                       created_at
                FROM bmi_history
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
            if not rows:
                print("История пуста.")
                return
            print("\n--- История расчётов BMI ---")
            for row in rows:
                print(
                    f"#{row[0]}: вес={row[1]}, рост={row[2]}, "
                    f"BMI={row[3]:.2f} ({row[4]}) — {row[5]}"
                )
    finally:
        conn.close()

def delete_record(record_id):
    """Удаляет запись из таблицы bmi_history по id."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM bmi_history WHERE id = %s",
                (record_id,),
            )
            if cur.rowcount > 0:
                conn.commit()
                print(f"Запись #{record_id} успешно удалена.")
            else:
                print(f"Запись с id={record_id} не найдена.")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Клиент BMI + PostgreSQL")
    print("1 — рассчитать и сохранить")
    print("2 — показать историю")
    print("3 — удалить запись по id")
    choice = input("Выбор: ").strip()

    if choice == "1":
        weight = float(input("Вес (кг): "))
        height = float(input("Рост (м): "))
        bmi = calculate_bmi(weight, height)
        category = get_category(bmi)
        print(f"BMI = {bmi:.2f} ({category})")
        save_bmi_record(weight, height, bmi, category)
    elif choice == "2":
        show_history()
    elif choice == "3":
        record_id = int(input("Введите id записи для удаления: "))
        delete_record(record_id)
    else:
        print("Неизвестный пункт меню.")
