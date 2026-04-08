"""Initialize MySQL database schema and default settings."""

from __future__ import annotations

from db.mysql import get_connection
from db.schema import create_database_if_not_exists, initialize_schema


def main() -> None:
    root_connection = get_connection(include_database=False)
    try:
        create_database_if_not_exists(root_connection)
    finally:
        root_connection.close()

    app_connection = get_connection(include_database=True)
    try:
        initialize_schema(app_connection)
    finally:
        app_connection.close()

    print("Database initialization complete.")
    print("- Database ensured")
    print("- Tables and indexes created")
    print("- Default system settings seeded")


if __name__ == "__main__":
    main()
