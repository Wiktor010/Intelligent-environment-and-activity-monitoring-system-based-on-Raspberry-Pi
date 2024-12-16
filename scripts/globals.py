# globals.py
class Globals:
    _instance = None  # Pojedyncza instancja klasy

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Globals, cls).__new__(cls, *args, **kwargs)
            # Inicjalizacja zmiennych w singletonie
            cls._instance.sensor_temperature = None
            cls._instance.sensor_humidity = None
            cls._instance.sensor_pressure = None
            cls._instance.sensor_light_intensity = None
            cls._instance.db_temperature = None
            cls._instance.db_humidity = None
            cls._instance.db_pressure = None
            cls._instance.db_light_intensity = None
        return cls._instance