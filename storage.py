
import re
from contextlib import contextmanager

from mysql.connector import Error, IntegrityError
from connect import connect_to_mysql


@contextmanager
def database():

    connection = connect_to_mysql()

    if connection is None:
        raise Exception("Could not connect to MySQL.")

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        yield connection, cursor

    except IntegrityError as error:
        connection.rollback()

        if error.errno == 1062:
            raise Exception("Email address already exists.")

        raise Exception(str(error))

    except Error as error:
        connection.rollback()
        raise Exception(str(error))

    finally:
        if cursor:
            cursor.close()

        connection.close()


def initialize():

    with database() as (connection, cursor):

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(250) NOT NULL UNIQUE,
                program ENUM('BSIT','BSAM','BSIS') NOT NULL,
                contribution_amount DECIMAL(10,2) NOT NULL
            )
        """)

        connection.commit()


def get_students():

    with database() as (connection, cursor):

        cursor.execute("""
            SELECT id, name, email, program, contribution_amount
            FROM students
            ORDER BY name
        """)

        return cursor.fetchall()


def save_student(data, student_id=None):

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    program = data.get("program")

    if not name:
        raise Exception("Student name is required.")

    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise Exception("Enter a valid email address.")

    if program not in ("BSIT", "BSAM", "BSIS"):
        raise Exception("Select a valid program.")

    try:
        amount = float(data.get("contribution_amount"))
    except (TypeError, ValueError):
        raise Exception("Enter a valid contribution amount.")

    if amount < 0 or amount > 99999999.99:
        raise Exception("Enter a valid contribution amount.")

    with database() as (connection, cursor):

        values = (name, email, program, amount)

        if student_id is None:

            cursor.execute("""
                INSERT INTO students
                (name, email, program, contribution_amount)
                VALUES (%s, %s, %s, %s)
            """, values)

        else:

            cursor.execute("""
                UPDATE students
                SET name=%s, email=%s, program=%s,
                    contribution_amount=%s
                WHERE id=%s
            """, values + (student_id,))

            if cursor.rowcount == 0:
                cursor.execute(
                    "SELECT id FROM students WHERE id=%s",
                    (student_id,)
                )

                if not cursor.fetchone():
                    raise Exception("Student record not found.")

        connection.commit()


def delete_student(student_id):

    with database() as (connection, cursor):

        cursor.execute(
            "DELETE FROM students WHERE id=%s",
            (student_id,)
        )

        if cursor.rowcount == 0:
            raise Exception("Student record not found.")

        connection.commit()


if __name__ == "__main__":
    initialize()
    print("StudentHub database initialized successfully.")