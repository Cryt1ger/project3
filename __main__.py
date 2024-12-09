from flask import Flask, render_template, request
import requests

""" 
app = Flask(__name__)

@app.route('/')
def home():
    return "Flask работает!"

if __name__ == '__main__':
    app.run(debug=True)
"""

KEY = "uLkWh4fD91PdhPBotbeKdPbYWbE7nRAZ" #accuweather
API_KEY = "7ddc2f019ed6ac507bbf5075056a6183"#openweather. буду пользоваться им

def get_weather_openweather(lat, lon):
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        weather_info = {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "rain_probability": data.get("rain", {}).get("1h", 0) #если нет, верну ноль
        }
        return weather_info
    else:
        print(f"Ошибка {response.status_code}: {response.text}")
        return None

def get_weather_by_city(city):
    try:
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        response = requests.get("http://api.openweathermap.org/data/2.5/weather", params=params)
        response.raise_for_status()  # Проверка на статус 2xx

        data = response.json()

        # Проверка на наличие необходимых данных
        if "main" not in data or "temp" not in data["main"]:
            raise ValueError(f"Ошибка API: Не удаётся получить данные о температуре для города {city}")

        weather_info = {
            "temperature": data["main"]["temp"],
            "wind_speed": data["wind"]["speed"] * 3.6,  # м/с -> км/ч
            "rain_probability": data.get("rain", {}).get("1h", 0)
        }
        return weather_info
    except requests.exceptions.RequestException as e:
        # Обработка ошибок сетевого запроса
        return {"error": f"Ошибка соединения с API: {str(e)}"}
    except ValueError as e:
        # Обработка ошибок, связанных с неправильным городом или данными от API
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Неизвестная ошибка: {str(e)}"}




def check_bad_weather(temperature, wind_speed, rain_probability):

    # Определяем, являются ли погодные условия неблагоприятными.

    if temperature < 0 or temperature > 35:
        return "Плохие погодные условия: температура выходит за пределы"
    if wind_speed > 50:
        return "Плохие погодные условия: сильный ветер"
    if rain_probability > 70:
        return "Плохие погодные условия: высокая вероятность осадков"
    return "Хорошие погодные условия"



test_coordinates = [
    (55.7558, 37.6176),  # Москва
    (40.7128, -74.0060),  # Нью-Йорк
    (35.6895, 139.6917)   # Токио
]
for lat, lon in test_coordinates:
    print(get_weather_openweather(lat, lon))

# Тест критериев погоды
print(check_bad_weather(-10, 30, 50))  # Плохие погодные условия: температура выходит за пределы
print(check_bad_weather(40, 30, 50))  # Плохие погодные условия: температура выходит за пределы
print(check_bad_weather(20, 60, 50))  # Плохие погодные условия: сильный ветер
print(check_bad_weather(20, 30, 80))  # Плохие погодные условия: высокая вероятность осадков
print(check_bad_weather(20, 30, 50))  # Хорошие погодные условия

"""
Потенциальные улучшения логики:
Добавить учёт атмосферного давления..
Сделать пороговые значения разными для разных широт.
Сделать пороговые значения конфигурируемыми

"""









app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/check_weather', methods=['POST'])
def check_weather():
    start_city = request.form.get('start')
    end_city = request.form.get('end')

    if not start_city or not end_city:
        return "Обе точки маршрута должны быть указаны", 400

    start_weather = get_weather_by_city(start_city)
    end_weather = get_weather_by_city(end_city)

    if "error" in start_weather:
        return render_template("error.html", message=f"Ошибка: {start_weather['error']} для города {start_city}. Вероятно, его не существует.")

    if "error" in end_weather:
        return render_template("error.html", message=f"Ошибка: {end_weather['error']} для города. Скорее всего, такого города нет на Земле. {end_city}")

    start_evaluation = check_bad_weather(
        start_weather["temperature"],
        start_weather["wind_speed"],
        start_weather["rain_probability"]
    )
    end_evaluation = check_bad_weather(
        end_weather["temperature"],
        end_weather["wind_speed"],
        end_weather["rain_probability"]
    )

    result = f"""
    <h1>Результаты проверки погоды</h1>
    <h2>Начальная точка: {start_city}</h2>
    <ul>
        <li>Температура: {start_weather['temperature']}°C</li>
        <li>Скорость ветра: {start_weather['wind_speed']} км/ч</li>
        <li>Вероятность дождя: {start_weather['rain_probability']}%</li>
        <li>Оценка погоды: {start_evaluation}</li>
    </ul>
    <h2>Конечная точка: {end_city}</h2>
    <ul>
        <li>Температура: {end_weather['temperature']}°C</li>
        <li>Скорость ветра: {end_weather['wind_speed']} км/ч</li>
        <li>Вероятность дождя: {end_weather['rain_probability']}%</li>
        <li>Оценка погоды: {end_evaluation}</li>
    </ul>
    """
    return result


if __name__ == '__main__':
    app.run(debug=True)


"""
    
Веб-сервис проверен на различных сценариях ввода данных.

Все компоненты работают корректно и не выявлены ошибки.

"""