
import mysql.connector
from typing import Any


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="YOUR_MYSQL_PASSWORD",
        database="order_db"
    )


def get_order(username: str) -> list[dict[str, Any]]:
    conn = get_connection()
    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT order_id, description
            FROM orders
            WHERE username = %s
            ORDER BY order_id
            """,
            (username,)
        )

        rows: list[dict[str, Any]] = cursor.fetchall()

        return [
            {
                "order_id": str(row["order_id"]),
                "description": row["description"]
            }
            for row in rows
        ]

    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def create_order(username: str, order_des: str) -> str:
    conn = get_connection()
    cursor = None

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO orders (username, description)
            VALUES (%s, %s)
            """,
            (username, order_des)
        )

        conn.commit()

        return str(cursor.lastrowid)

    except Exception:
        conn.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def delete_order(username: str, order_id: str) -> bool:
    conn = get_connection()
    cursor = None

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM orders
            WHERE username = %s AND order_id = %s
            """,
            (username, order_id)
        )

        deleted = cursor.rowcount > 0
        conn.commit()

        return deleted

    except Exception:
        conn.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        conn.close()
