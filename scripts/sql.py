import pymysql
import matplotlib.pyplot as plt
try:
    from scripts.globals import Globals  # When script is used as module (eg. in main.py file)
except ModuleNotFoundError:
    from globals import Globals  # When scirpt is running alone

# Dictionary with defined databases to work with
databases = {
    'test': {
        'host': 'localhost',
        'user': 'raspberry',
        'password': 'testtest',
        'port': 3306,
        'database': 'test_database'
    }
}

class SensorDataHandler:
    def __init__(self, device_id=1, source_id=1):
        # Initialize sensor data
        self.sensor_data = {
            "device_id": device_id,
            "source_id": source_id,
            "temperature": None,
            "pressure": None,
            "humidity": None,
            "light_intensity": None,
        }
        self.global_instance = Globals()

    def update_sensor_data(self):
        self.sensor_data["temperature"] = self.global_instance.sensor_temperature
        self.sensor_data["pressure"] = self.global_instance.sensor_pressure
        self.sensor_data["humidity"] = self.global_instance.sensor_humidity
        self.sensor_data["light_intensity"] = self.global_instance.sensor_light_intensity
        print(f"Dane w tablicy zostały zaktualizowane:")
        for key, value in self.sensor_data.items():
            if value is not None:
                print(f"{key}: {value}")
        print("-" * 30)

    def insert_sensor_data(self, database_choice):
        global databases
        # Get database configuration
        self.db_config = databases.get(database_choice)
        if self.db_config is None:
            print(f"Błąd: Brak konfiguracji dla bazy o nazwie '{database_choice}'")
            return

        try:
            self.update_sensor_data()
            # Connect to the database
            connection = pymysql.connect(
                host = self.db_config['host'],
                user = self.db_config['user'],
                password = self.db_config['password'],
                db = self.db_config['database'],
                port = self.db_config['port']
            )

            # Prepare cursor and execute SQL query
            cursor = connection.cursor()
            sql_query = (
                "INSERT INTO sensor_data "
                "(device_id, source_id, temperature, pressure, humidity, light_intensity) "
                "VALUES (%s, %s, %s, %s, %s, %s)"
            )
            cursor.execute(sql_query, (
                self.sensor_data["device_id"],
                self.sensor_data["source_id"],
                self.sensor_data["temperature"],
                self.sensor_data["pressure"],
                self.sensor_data["humidity"],
                self.sensor_data["light_intensity"]
            ))

            # Commit changes
            connection.commit()
            print("Dane zostały pomyślnie przesłane do bazy danych.")
            print("-" * 30)

        except pymysql.MySQLError as e:
            print(f"Błąd podczas połączenia lub zapisu do bazy danych: {e}")

        finally:
            if 'connection' in locals() and connection:
                connection.close()

    def fetch_latest_sensor_data(self, database_choice):
        global databases
        self.db_config = databases.get(database_choice)
        if self.db_config is None:
            print(f"Błąd: Brak konfiguracji dla bazy o nazwie '{database_choice}'")
            return None

        try:
            connection = pymysql.connect(
                host = self.db_config['host'],
                user = self.db_config['user'],
                password = self.db_config['password'],
                db = self.db_config['database'],
                port = self.db_config['port']
            )

            cursor = connection.cursor()
            sql_query = "SELECT temperature, pressure, humidity, light_intensity FROM sensor_data ORDER BY id DESC LIMIT 1"
            cursor.execute(sql_query)
            latest_row = cursor.fetchone()

            if latest_row:
                self.sensor_data["temperature"] = latest_row[0]

                self.sensor_data["pressure"] = latest_row[1]
                self.sensor_data["humidity"] = latest_row[2]
                self.sensor_data["light_intensity"] = latest_row[3]
                print("Najnowsze dane z bazy zostały zapisane w obiekcie:")
                for key, value in self.sensor_data.items():
                    if value is not None:
                        print(f"{key}: {value}")

            else:
                print("Brak danych w tabeli.")

        except pymysql.MySQLError as e:
            print(f"Błąd podczas pobierania danych z bazy: {e}")

        finally:
            if 'connection' in locals() and connection:
                connection.close()

    def fetch_all_sensor_data(self, database_choice):
        global databases
        self.db_config = databases.get(database_choice)
        if self.db_config is None:
            print(f"Błąd: Brak konfiguracji dla bazy o nazwie '{database_choice}'")
            return None, None, None, None, None

        try:
            connection = pymysql.connect(
                host = self.db_config['host'],
                user = self.db_config['user'],
                password = self.db_config['password'],
                db = self.db_config['database'],
                port = self.db_config['port']
            )

            cursor = connection.cursor()
            sql_query = "SELECT temperature, pressure, humidity, light_intensity, timestamp FROM sensor_data"
            cursor.execute(sql_query)
            rows = cursor.fetchall()

            if rows:
                temperatures = [row[0] for row in rows]
                pressures = [row[1] for row in rows]
                humidities = [row[2] for row in rows]
                light_intensities = [row[3] for row in rows]
                timestamps = [row[4] for row in rows]

                print("Dane zostały pomyślnie pobrane z bazy danych.")
                return temperatures, pressures, humidities, light_intensities, timestamps

            else:
                print("Brak danych w tabeli.")
                return None, None, None, None, None

        except pymysql.MySQLError as e:
            print(f"Błąd podczas pobierania danych z bazy: {e}")
            return None, None, None, None, None

        finally:
            if 'connection' in locals() and connection:
                connection.close()
                
    def fetch_sensor_data_by_date(self, database_choice, start_date, end_date):
        global databases
        self.db_config = databases.get(database_choice)
        if self.db_config is None:
            print(f"Błąd: Brak konfiguracji dla bazy o nazwie '{database_choice}'")
            return None, None, None, None, None

        try:
            connection = pymysql.connect(
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                db=self.db_config['database'],
                port=self.db_config['port']
            )

            cursor = connection.cursor()
            sql_query = (
                "SELECT temperature, pressure, humidity, light_intensity, timestamp "
                "FROM sensor_data "
                "WHERE timestamp BETWEEN %s AND %s"
            )
            cursor.execute(sql_query, (start_date, end_date))
            rows = cursor.fetchall()

            if rows:
                temperatures = [row[0] for row in rows]
                pressures = [row[1] for row in rows]
                humidities = [row[2] for row in rows]
                light_intensities = [row[3] for row in rows]
                timestamps = [row[4] for row in rows]

                print("Dane zostały pomyślnie pobrane z bazy danych.")
                return temperatures, pressures, humidities, light_intensities, timestamps

            else:
                print("Brak danych w podanym zakresie dat.")
                return None, None, None, None, None

        except pymysql.MySQLError as e:
            print(f"Błąd podczas pobierania danych z bazy: {e}")
            return None, None, None, None, None

        finally:
            if 'connection' in locals() and connection:
                connection.close()

if __name__ == "__main__":
    sql = SensorDataHandler()
    globalsss = Globals()
    
    database_choice = 'test'
    sql.fetch_latest_sensor_data(database_choice)
    sql.insert_sensor_data(database_choice)

    sql.fetch_latest_sensor_data(database_choice)
    globalsss.sensor_light_intensity = sql.sensor_data["light_intensity"]
    print(f"{globalsss.sensor_light_intensity}")

    # Wysłanie danych do bazy danych
    # insert_sensor_data()