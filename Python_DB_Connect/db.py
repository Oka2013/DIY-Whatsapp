import psycopg2

class DataBaseAgent:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def execute_on_db(self, command: str) -> list:
        try:
            connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )

            connection.autocommit = True
            cursor = connection.cursor()

            cursor.execute(command)

            data = cursor.fetchall()

            desc = [desc[0] for desc in cursor.description]
            return [dict(zip(desc, row)) for row in data]

        except Exception as e:
            print("Error while connecting to DB! ", e)

        finally:
            if connection:
                cursor.close()
                connection.close()
            print("DB connection closed!")

    def is_in_db(self, db_name: str, where : str):
        data = self.execute_on_db(f"select id from {db_name} where {where}")
        return len(data) != 0