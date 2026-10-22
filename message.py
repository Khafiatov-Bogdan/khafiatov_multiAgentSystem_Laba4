from enum import Enum
from dataclasses import dataclass, field
from typing import Any
import time


class MessageType(Enum):
    INITIALIZATION = 'Инициализация'
    CREATE_ACTOR = 'Создание актора'
    HELLO_WORLD = 'Приветствие'
    SET_OPERATION = 'Операция'
    PRICE_REQUEST = 'Запрос цены'
    PRICE_RESPONSE = 'Ответ с ценой'
    PLANNING_REQUEST = 'Запрос плана'
    PLANNING_RESPONSE = 'Ответ плана'


@dataclass
class Message:
    msg_type: MessageType
    msg_body: Any
    msg_time: float = field(default_factory=time.time)