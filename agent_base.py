from typing import Dict, Callable, Any
import logging
import traceback

from thespian.actors import Actor, ActorAddress
from message import MessageType, Message


class AgentBase(Actor):

    def __init__(self):
        super().__init__()
        self.name = 'Базовый агент'
        self.handlers: Dict[MessageType, Callable[[Any, ActorAddress], None]] = {}
        self.subscribe(MessageType.INITIALIZATION, self.handle_init_message)

    def subscribe(self, msg_type: MessageType, handler):
        if msg_type in self.handlers:
            logging.warning('Повторная подписка на %s', msg_type)
        self.handlers[msg_type] = handler

    def unsubscribe(self, msg_type: MessageType):
        if msg_type not in self.handlers:
            logging.warning('Такой подписки нет: %s', msg_type)
        else:
            del self.handlers[msg_type]

    def receiveMessage(self, msg, sender):
        logging.debug('%s получил сообщение: %s', self.name, msg)
        if isinstance(msg, Message):
            handler = self.handlers.get(msg.msg_type)
            if handler:
                try:
                    handler(msg, sender)
                except Exception as ex:
                    traceback.print_exc()
                    logging.exception(ex)
            else:
                logging.warning('%s: нет подписки на %s', self.name, msg.msg_type)

    def handle_init_message(self, message, sender):
        data = message.msg_body
        self.scene      = data.get('scene')
        self.dispatcher = data.get('dispatcher')
        self.entity     = data.get('entity')
        self.name = f'Агент {self.entity.name}'
        logging.info('%s проинициализирован', self.name)