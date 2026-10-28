
import mysql.connector
from mysql.connector import IntegrityError
from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="YOUR_MYSQL_PASSWORD",
        database="order_db"
    )


def create_user(username: str, password: str) -> str:
    hashed_password = password_hash.hash(password)
    conn = get_connection()
    cursor = None

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (username, password)
            VALUES (%s, %s)
            """,
            (username, hashed_password)
        )
        conn.commit()
        return username

    except IntegrityError as exc:
        conn.rollback()
        raise ValueError("Username already exists") from exc

    except Exception:
        conn.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def change_password(
    username: str,
    current_password: str,
    new_password: str
) -> bool:
    conn = get_connection()
    cursor = None

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT password FROM users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()

        if user is None:
            return False

        stored_hash = user["password"]

        if not password_hash.verify(current_password, stored_hash):
            return False

        new_hash = password_hash.hash(new_password)

        cursor.execute(
            "UPDATE users SET password = %s WHERE username = %s",
            (new_hash, username)
        )
        conn.commit()

        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        conn.close()
