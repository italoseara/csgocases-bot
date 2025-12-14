import os
import psycopg2

from dotenv import load_dotenv


load_dotenv()


class PromocodeRepository:
    """Repository for managing promocode persistence in PostgreSQL."""

    def connect(self) -> psycopg2.extensions.connection:
        """Connect to the PostgreSQL database."""

        return psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
        )

    def create(self, code: str, post_url: str) -> None:
        """Store promocode in the database."""

        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    insert_query = """
                    INSERT INTO promocodes (code, post_url)
                    VALUES (%s, %s)
                    """

                    cursor.execute(insert_query, (code, post_url))
                    conn.commit()
            print("Promocode stored successfully.")
        except Exception as e:
            print(f"Database error: {e}")

    def exists_by_post_url(self, post_url: str) -> bool:
        """Check if a promocode exists by post URL."""

        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    select_query = """
                    SELECT EXISTS(
                        SELECT 1 FROM promocodes WHERE post_url = %s
                    )
                    """

                    cursor.execute(select_query, (post_url,))
                    exists = cursor.fetchone()[0]
            return exists
        except Exception as e:
            print(f"Database error: {e}")
            return False
