import pymysql
import matplotlib.pyplot as plt
try:
    from scripts import globals as g  # When script is used as module (eg. in main.py file)
except ModuleNotFoundError:
    import globals as g  # When scirpt is running alone

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

    def update_sensor_data(self, temperature, pressure, humidity, light_intensity):
        self.sensor_data["temperature"] = temperature
        self.sensor_data["pressure"] = pressure
        self.sensor_data["humidity"] = humidity
        self.sensor_data["light_intensity"] = light_intensity
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


# def plot_sensor_data(temperatures, pressures, humidities, light_intensities):
#     """
#     Rysuje wykresy dla temperatury, ciśnienia, wilgotności i natężenia światła
#     na podstawie przekazanych danych.
#     """
#     if not any([temperatures, pressures, humidities, light_intensities]):
#         print("Brak danych do wyświetlenia wykresów.")
#         return

#     # Indeksy pomiarów
#     indices = list(range(1, len(temperatures) + 1))

#     # Rysowanie wykresów
#     plt.figure(figsize=(12, 10))

#     if temperatures:
#         plt.subplot(2, 2, 1)
#         plt.plot(indices, temperatures, marker='o', label="Temperatura (°C)", color='red')
#         plt.title("Temperatura")
#         plt.xlabel("Pomiar")
#         plt.ylabel("Temperatura (°C)")
#         plt.grid(True)
#         plt.legend()

#     if pressures:
#         plt.subplot(2, 2, 2)
#         plt.plot(indices, pressures, marker='o', label="Ciśnienie (hPa)", color='blue')
#         plt.title("Ciśnienie")
#         plt.xlabel("Pomiar")
#         plt.ylabel("Ciśnienie (hPa)")
#         plt.grid(True)
#         plt.legend()

#     if humidities:
#         plt.subplot(2, 2, 3)
#         plt.plot(indices, humidities, marker='o', label="Wilgotność (%)", color='green')
#         plt.title("Wilgotność")
#         plt.xlabel("Pomiar")
#         plt.ylabel("Wilgotność (%)")
#         plt.grid(True)
#         plt.legend()

#     if light_intensities:
#         plt.subplot(2, 2, 4)
#         plt.plot(indices, light_intensities, marker='o', label="Natężenie światła (lux)", color='orange')
#         plt.title("Natężenie światła")
#         plt.xlabel("Pomiar")
#         plt.ylabel("Natężenie światła (lux)")
#         plt.grid(True)
#         plt.legend()

#     plt.tight_layout()
#     plt.show()



if __name__ == "__main__":
    sql = SensorDataHandler()
    # Aktualizacja danych w tablicy
    sql.update_sensor_data(20, 30, 40, 50)
    
    database_choice = 'test'

    sql.insert_sensor_data(database_choice)
    # Wysłanie danych do bazy danych
    # insert_sensor_data()