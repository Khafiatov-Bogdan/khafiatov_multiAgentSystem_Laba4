import typing
import logging

from agent_base import AgentBase
from message import Message, MessageType
from point import Point
from order_entity import OrderEntity


class CourierAgent(AgentBase):

    def __init__(self):
        super().__init__()
        self.name = 'Агент курьера'
        self.subscribe(MessageType.PRICE_REQUEST, self.handle_price_request)
        self.subscribe(MessageType.PLANNING_REQUEST, self.handle_planning_request)

    def handle_price_request(self, message, sender):
        order: OrderEntity = message.msg_body
        variants = self.__get_params(order)

        logging.info('%s ← PRICE_REQUEST от заказа %s → вариантов %d',
                     self.name, order.name, len(variants))
        for v in variants:
            logging.info('  [%s] окно [%.2f; %.2f], цена %.2f',
                         v['variant_name'], v['time_from'], v['time_to'], v['price'])

        self.send(sender, Message(MessageType.PRICE_RESPONSE, variants))

    def __get_params(self, order: OrderEntity) -> typing.List[dict]:
        if order.weight > self.entity.max_mass:
            logging.info('%s: заказ %s слишком тяжёлый (%.2f > %.2f) — отказ',
                         self.name, order.name, order.weight, self.entity.max_mass)
            return []

        if order.volume > self.entity.max_volume:
            logging.info('%s: заказ %s слишком объёмный (%.2f > %.2f) — отказ',
                         self.name, order.name, order.volume, self.entity.max_volume)
            return []
        return self.entity.estimate_order(order)


    def handle_planning_request(self, message, sender):
        params = message.msg_body
        result = self.entity.add_order_to_schedule(
            params['order'],
            params['time_from'],
            params['time_to'],
            params['price'],
            params,
        )
        status = 'принято' if result else 'ОТКАЗ (конфликт)'
        logging.info('%s ← PLANNING_REQUEST заказа %s → %s',
                     self.name, params['order'].name, status)
        self.send(sender, Message(MessageType.PLANNING_RESPONSE, result))