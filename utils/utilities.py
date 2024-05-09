import os
import requests
import sqlite3
from typing import List, Dict, Tuple
from sqlite3 import Connection, Cursor
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)


class ConversationalMemory:
    def __init__(self, messages: list = [dict]) -> None:
        self.messages = messages

    def append(self, message: dict, messages_list: list) -> None:
        messages_list.append(message)

    def agentGet(self, message: dict, messages_list: list) -> list:
        messages_list.append(message)
        return messages_list


class UsersDb:
    def __init__(self, db_path: str) -> None:
        # Getting db path
        self.db_path = db_path

        # Ensure that database tables are created
        self._create_tables()

    def _create_tables(self) -> None:
        table = """
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY,
                    Email TEXT NOT NULL,
                    Message TEXT NOT NULL,
                    Sender TEXT NOT NULL,
                    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
        """

        self._execute_query(table)

    @staticmethod
    def _get_cursor(conn: Connection) -> Cursor:
        # Creating cursor
        return conn.cursor()

    def _execute_query(self, query: str, *args) -> None:
        # Executing queries
        with sqlite3.connect(self.db_path) as conn:
            cur = self._get_cursor(conn)
            cur.execute(query, args)
            conn.commit()

    def checkUserExist(self, email: str) -> bool:
        # Checking user exist
        with sqlite3.connect(self.db_path) as conn:
            cur = self._get_cursor(conn)
            user = cur.execute("SELECT 1 FROM chat_history WHERE Email = ?", (email,))
            return user.fetchone() is not None

    def getUserChatHistory(self, email: str) -> List[Tuple]:
        # Get the latest messages for a user
        query = """
                SELECT Sender, Message 
                FROM chat_history 
                WHERE Email = ? 
                ORDER BY Timestamp DESC 
                LIMIT 10
        """
        with sqlite3.connect(self.db_path) as conn:
            cur = self._get_cursor(conn)
            user = cur.execute(query, (email,))
            data = user.fetchall()
            return data if data else None

    def createUser(self, email: str, init_message: str, sender: str) -> None:
        # Creating new user
        self.add_message(email, init_message, sender)

    def deleteUser(self, email: str) -> None:
        # Deleting user
        self._execute_query("DELETE FROM Users WHERE Email = ?", email)

    def add_message(self, email: str, message: str, sender: str) -> None:
        # Add a new message to chat history
        query = "INSERT INTO chat_history (Email, Message, Sender) VALUES (?, ?, ?)"
        self._execute_query(query, email, message, sender)


def get_weather(city: Dict):
    api_key = os.getenv("WEATHER_API_KEY")
    _city = city["city"]

    url = f"http://api.openweathermap.org/data/2.5/weather?q={_city}&appid={api_key}"

    response = requests.get(url)
    weather_data = response.json()

    weather_conditions = f"Weather condition: {weather_data['weather'][0]['description']}"
    environmental_conditions = {
        "temp": weather_data["main"]["temp"] - 273.15,
        "min_temp": weather_data["main"]["temp_min"] - 273.15,
        "max_temp": weather_data["main"]["temp_max"] - 273.15,
    }

    dict_string = ", ".join(
        [f"{key}: {value}" for key, value in environmental_conditions.items()]
    )

    final_return = weather_conditions + ", " + dict_string

    return final_return

def get_weather_by_coordinates(long: str, lat: str):
    api_key = os.getenv("WEATHER_API_KEY")
    latitude = lat
    longitude = long

    # Construct the URL with coordinates
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}"

    response = requests.get(url)
    weather_data = response.json()

    weather_conditions = f"Weather condition: {weather_data['weather'][0]['description']}"
    environmental_conditions = {
        "Temperature": f"{weather_data['main']['temp'] - 273.15:.2f}°C",
        "Min Temp": f"{weather_data['main']['temp_min'] - 273.15:.2f}°C",
        "Max Temp": f"{weather_data['main']['temp_max'] - 273.15:.2f}°C",
        "Humidity": f"{weather_data['main']['humidity']}%",
        "Wind Speed": f"{weather_data['wind']['speed']} m/s",
        "Pressure": f"{weather_data['main']['pressure']} hPa",
    }

    dict_string = ", ".join([f"{key}: {value}" for key, value in environmental_conditions.items()])


    final_return = weather_conditions + ", " + dict_string

    return final_return

