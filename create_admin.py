import uuid
import getpass

from werkzeug.security import generate_password_hash
from database.db import get_db_connection


def create_admin():
    print("================================")
    print("   SIH PORTAL - CREATE ADMIN")
    print("================================")

    name = input("Enter admin name: ").strip()
    email = input("Enter admin email: ").strip()

    password = getpass.getpass("Enter admin password: ")
    confirm_password = getpass.getpass("Confirm admin password: ")

    if not name or not email or not password:
        print("Error: All fields are required.")
        return

    if password != confirm_password:
        print("Error: Passwords do not match.")
        return

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check whether email already exists
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            print("Error: A user with this email already exists.")
            return

        # Generate UUID
        user_id = str(uuid.uuid4())

        # Hash password
        password_hash = generate_password_hash(password)

        # Insert admin
        query = """
            INSERT INTO users
            (id, name, email, password, role, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            user_id,
            name,
            email,
            password_hash,
            "ADMIN",
            "ACTIVE"
        )

        cursor.execute(query, values)
        connection.commit()

        print("\nAdmin created successfully!")
        print("Admin ID:", user_id)
        print("Name:", name)
        print("Email:", email)
        print("Role: ADMIN")
        print("Status: ACTIVE")

    except Exception as error:
        print("Error while creating admin:", error)

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


if __name__ == "__main__":
    create_admin()