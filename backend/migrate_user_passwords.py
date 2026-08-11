import sqlite3

from app.services.password_service import hash_password, is_password_hash

DB_NAME = "omnilink_crm.db"


def migrate_passwords():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    rows = cursor.execute(
        "SELECT user_id, email, password FROM users"
    ).fetchall()

    migrated = 0
    already_hashed = 0

    try:
        for user_id, email, stored_password in rows:
            if is_password_hash(stored_password):
                already_hashed += 1
                continue

            cursor.execute(
                "UPDATE users SET password = ? WHERE user_id = ?",
                (hash_password(str(stored_password)), user_id),
            )
            migrated += 1

        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    print("Password migration completed.")
    print("Migrated plaintext passwords:", migrated)
    print("Already hashed passwords:", already_hashed)


if __name__ == "__main__":
    migrate_passwords()
