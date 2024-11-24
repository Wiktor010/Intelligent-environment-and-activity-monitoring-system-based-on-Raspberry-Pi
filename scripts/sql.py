import pymysql
import matplotlib.pyplot as plt

# Zmienne globalne do przechowywania ostatnich danych z bazy
last_temperature = None
last_pressure = None
last_humidity = None
last_light_intensity = None


# Definicje połączeń dla różnych baz danych
databases = {
    'production': {
        'host': 'LAPTOP-809K11E',
        'user': 'Wiktor',
        'password': 'Wiktor123123',
        'port': 3306,
        'database': 'data'
    },
    'test': {
        'host': 'localhost',
        'user': 'raspberry',
        'password': 'testtest',
        'port': 3306,
        'database': 'test_database'
    }
}

# Tablica z danymi z czujników (na początek przykładowe wartości)
sensor_data = {
    "device_id": 1,
    "source_id": 1,
    "temperature": None,
    "pressure": None,
    "humidity": None,
    "light_intensity": None,
}

def update_sensor_data(temperature, pressure, humidity, light_intensity):
    sensor_data["temperature"] = temperature
    sensor_data["pressure"] = pressure
    sensor_data["humidity"] = humidity
    sensor_data["light_intensity"] = light_intensity
    print(f"Dane w tablicy zostały zaktualizowane:")
    for key, value in sensor_data.items():
        print(f"{key}: {value:.2f}")
    print("-" * 30)

def insert_sensor_data(database_choice):
    
    # Pobranie konfiguracji połączenia z odpowiedniego słownika
    db_config = databases.get(database_choice)
    if db_config is None:
        print(f"Błąd: Brak konfiguracji dla bazy o nazwie '{database_choice}'")
        return
    
    try:
         # Połączenie z bazą danych przy użyciu danych z słownika
        connection = pymysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            db=db_config['database'],
            port=db_config['port']
        )

        # Przygotowanie kursora do wykonywania zapytań
        cursor = connection.cursor()

        # Zapytanie SQL do wstawienia danych
        sql_query = (
            "INSERT INTO sensor_data "
            "(device_id, source_id, temperature, pressure, humidity, light_intensity) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )

        # Wstawianie danych z tablicy sensor_data
        cursor.execute(sql_query, (
            sensor_data["device_id"],
            sensor_data["source_id"],
            sensor_data["temperature"],
            sensor_data["pressure"],
            sensor_data["humidity"],
            sensor_data["light_intensity"]
        ))

        # Zatwierdzenie zmian
        connection.commit()
        print("Dane zostały pomyślnie przesłane do bazy danych.")
        print("-" * 30)

    except pymysql.MySQLError as e:
        # Obsługa błędów związanych z połączeniem lub zapytaniem SQL
        print(f"Błąd podczas połączenia lub zapisu do bazy danych: {e}")

    finally:
        # Zamknięcie połączenia z bazą danych
        if 'connection' in locals() and connection:
            connection.close()



def fetch_latest_sensor_data(database_choice):
    """
    Pobiera najnowszy wiersz z tabeli `sensor_data` w wybranej bazie danych 
    i zapisuje dane do zmiennych globalnych.
    """
    global last_temperature, last_pressure, last_humidity, last_light_intensity

    db_config = databases.get(database_choice)
    if db_config is None:
        print(f"Błąd: Brak konfiguracji dla bazy o nazwie '{database_choice}'")
        return None

    try:
        connection = pymysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            db=db_config['database'],
            port=db_config['port']
        )

        cursor = connection.cursor()

        # Pobranie najnowszego wiersza
        sql_query = "SELECT temperature, pressure, humidity, light_intensity FROM sensor_data ORDER BY id DESC LIMIT 1"
        cursor.execute(sql_query)

        latest_row = cursor.fetchone()
        if latest_row:
            # Przypisanie wartości do zmiennych globalnych
            last_temperature = latest_row[0]
            last_pressure = latest_row[1]
            last_humidity = latest_row[2]
            last_light_intensity = latest_row[3]

            print("Najnowsze dane z bazy zostały zapisane w zmiennych:")
            print(f"Temperatura: {last_temperature:.2f} °C")
            print(f"Ciśnienie: {last_pressure:.2f} hPa")
            print(f"Wilgotność: {last_humidity:.2f} %")
            print(f"Natężenie światła: {last_light_intensity:.2f} lux")
        else:
            print("Brak danych w tabeli.")

    except pymysql.MySQLError as e:
        print(f"Błąd podczas pobierania danych z bazy: {e}")

    finally:
        if 'connection' in locals() and connection:
            connection.close()


def fetch_all_sensor_data(database_choice):
    """
    Pobiera wszystkie dane z tabeli `sensor_data` w wybranej bazie danych.
    Zwraca listy dla poszczególnych parametrów: temperatury, ciśnienia, wilgotności i natężenia światła.
    """
    db_config = databases.get(database_choice)
    if db_config is None:
        print(f"Błąd: Brak konfiguracji dla bazy o nazwie '{database_choice}'")
        return None, None, None, None

    try:
        connection = pymysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            db=db_config['database'],
            port=db_config['port']
        )

        cursor = connection.cursor()

        # Pobranie wszystkich danych
        sql_query = "SELECT temperature, pressure, humidity, light_intensity FROM sensor_data"
        cursor.execute(sql_query)
        rows = cursor.fetchall()

        if rows:
            # Przygotowanie list do zwrócenia
            temperatures = [row[0] for row in rows]
            pressures = [row[1] for row in rows]
            humidities = [row[2] for row in rows]
            light_intensities = [row[3] for row in rows]

            print("Dane zostały pomyślnie pobrane z bazy danych.")
            return temperatures, pressures, humidities, light_intensities
        else:
            print("Brak danych w tabeli.")
            return None, None, None, None

    except pymysql.MySQLError as e:
        print(f"Błąd podczas pobierania danych z bazy: {e}")
        return None, None, None, None

    finally:
        if 'connection' in locals() and connection:
            connection.close()


def plot_sensor_data(temperatures, pressures, humidities, light_intensities):
    """
    Rysuje wykresy dla temperatury, ciśnienia, wilgotności i natężenia światła
    na podstawie przekazanych danych.
    """
    if not any([temperatures, pressures, humidities, light_intensities]):
        print("Brak danych do wyświetlenia wykresów.")
        return

    # Indeksy pomiarów
    indices = list(range(1, len(temperatures) + 1))

    # Rysowanie wykresów
    plt.figure(figsize=(12, 10))

    if temperatures:
        plt.subplot(2, 2, 1)
        plt.plot(indices, temperatures, marker='o', label="Temperatura (°C)", color='red')
        plt.title("Temperatura")
        plt.xlabel("Pomiar")
        plt.ylabel("Temperatura (°C)")
        plt.grid(True)
        plt.legend()

    if pressures:
        plt.subplot(2, 2, 2)
        plt.plot(indices, pressures, marker='o', label="Ciśnienie (hPa)", color='blue')
        plt.title("Ciśnienie")
        plt.xlabel("Pomiar")
        plt.ylabel("Ciśnienie (hPa)")
        plt.grid(True)
        plt.legend()

    if humidities:
        plt.subplot(2, 2, 3)
        plt.plot(indices, humidities, marker='o', label="Wilgotność (%)", color='green')
        plt.title("Wilgotność")
        plt.xlabel("Pomiar")
        plt.ylabel("Wilgotność (%)")
        plt.grid(True)
        plt.legend()

    if light_intensities:
        plt.subplot(2, 2, 4)
        plt.plot(indices, light_intensities, marker='o', label="Natężenie światła (lux)", color='orange')
        plt.title("Natężenie światła")
        plt.xlabel("Pomiar")
        plt.ylabel("Natężenie światła (lux)")
        plt.grid(True)
        plt.legend()

    plt.tight_layout()
    plt.show()



if __name__ == "__main__":
    # Aktualizacja danych w tablicy
    update_sensor_data(temperature=22.5, pressure=1013, humidity=45, light_intensity=300)
    
    database_choice = 'test'

    insert_sensor_data(database_choice)
    # Wysłanie danych do bazy danych
    # insert_sensor_data()