import re
import psycopg2


class PromocodeRepository:
    """Repository for managing promocode persistence in PostgreSQL."""

    def __init__(self, url: str) -> None:
        self.url = url

    def connect(self) -> psycopg2.extensions.connection:
        """Connect to the PostgreSQL database."""

        # Parse URL robustly even if the password contains '@' by splitting at the last '@'
        try:
            scheme_sep = "://"
            if scheme_sep not in self.url:
                raise ValueError("Invalid database URL format")
            body = self.url.split(scheme_sep, 1)[1]

            # Split credentials and host at the last '@' so passwords with '@' are preserved
            if "@" not in body:
                raise ValueError("Invalid database URL format")
            creds, host_part = body.rsplit("@", 1)

            if ":" in creds:
                user, password = creds.split(":", 1)
            else:
                user = creds
                password = ""

            # host_part should be host[:port]/dbname
            if "/" not in host_part:
                raise ValueError("Invalid database URL format")
            host_port, dbname = host_part.split("/", 1)

            if ":" in host_port:
                host, port = host_port.split(":", 1)
            else:
                host = host_port
                port = "5432"
        except Exception:
            raise ValueError("Invalid database URL format")

        print(f"Connecting to DB at {host}:{port} as {user} to DB {dbname}")

        return psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)

    def create(self, code: str, post_url: str) -> None:
        """Store promocode in the database."""

        with self.connect() as conn:
            with conn.cursor() as cursor:
                insert_query = """
                INSERT INTO promocodes (code, post_url)
                VALUES (%s, %s)
                """

                cursor.execute(insert_query, (code, post_url))
                conn.commit()

    def exists_by_post_url(self, post_url: str) -> bool:
        """Check if a promocode exists by post URL."""

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
