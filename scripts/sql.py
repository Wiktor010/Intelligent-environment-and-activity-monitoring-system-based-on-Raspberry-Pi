import pymysql

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
        'host': '127.0.0.1',
        'user': 'raspberry',
        'password': 'testtest',
        'port': 3306,
        'database': 'test_database'
    }
}

# Tablica z danymi z czujników (na początek przykładowe wartości)
sensor_data = {
    "device_id": 1,
    "source_id": 101,
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

    except pymysql.MySQLError as e:
        # Obsługa błędów związanych z połączeniem lub zapytaniem SQL
        print(f"Błąd podczas połączenia lub zapisu do bazy danych: {e}")

    finally:
        # Zamknięcie połączenia z bazą danych
        if 'connection' in locals() and connection:
            connection.close()


if __name__ == "__main__":
    # Aktualizacja danych w tablicy
    update_sensor_data(temperature=22.5, pressure=1013, humidity=45, light_intensity=300)
    
    database_choice = 'test'

    insert_sensor_data(database_choice)
    # Wysłanie danych do bazy danych
    # insert_sensor_data()