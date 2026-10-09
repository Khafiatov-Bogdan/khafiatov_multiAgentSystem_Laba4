import typing
import logging

from agent_base import AgentBase
from message import Message, MessageType


class OrderAgent(AgentBase):

    def __init__(self):
        super().__init__()
        self.name = 'Агент заказа'
        self.possible_variants = []
        self.unchecked_couriers = []

        self.subscribe(MessageType.PRICE_RESPONSE, self.handle_price_response)
        self.subscribe(MessageType.PLANNING_RESPONSE, self.handle_planning_response)


    def handle_init_message(self, message, sender):
        super().handle_init_message(message, sender)
        self.__send_params_request()


    def __send_params_request(self):
        all_couriers = self.scene.get_entities_by_type('COURIER')
        logging.info('%s — список курьеров: %s',self.name, [c.name for c in all_couriers])
        good_courier = []
        for courier in all_couriers:
            point = courier.get_last_point()
            point1=self.entity.point_from
            distance = point.get_distance_to_other(point1)

            good_courier.append((distance, courier))
        good_courier.sort(key=lambda pair: pair[0])
        good_courier = good_courier[:2]
        logging.info('%s — опрашиваем ближайших: %s',self.name, [f'{c.name} ({d:.2f})' for d, c in good_courier])
        for distance, courier in good_courier:
            address = self.dispatcher.reference_book.get_address(courier)
            if address is None:
                continue

            logging.info('%s → PRICE_REQUEST курьеру %s', self.name, courier.name)
            self.send(address, Message(MessageType.PRICE_REQUEST, self.entity))
            self.unchecked_couriers.append(address)


    def handle_price_response(self, message, sender):
        variants = message.msg_body
        self.possible_variants.extend(variants)

        if variants:
            v = variants[0]
            logging.info('%s ← PRICE_RESPONSE от %s: цена %.2f, окно [%.2f; %.2f]',
                         self.name, v['courier'].name, v['price'],
                         v['time_from'], v['time_to'])

        if sender in self.unchecked_couriers:
            self.unchecked_couriers.remove(sender)

        if not self.unchecked_couriers:
            logging.info('%s: все курьеры ответили, выбираю вариант', self.name)
            self.__run_planning()

    def __run_planning(self):
        if not self.possible_variants:
            logging.warning('%s: нет доступных вариантов', self)
            return

        best = min(self.possible_variants, key=lambda v: v['price'])
        self.possible_variants.clear()

        courier = best['courier']
        address = self.dispatcher.reference_book.get_address(courier)

        logging.info('%s выбрал вариант от %s, цена %.2f',
                     self.name, courier.name, best['price'])
        logging.info('%s → PLANNING_REQUEST курьеру %s', self.name, courier.name)

        self.send(address, Message(MessageType.PLANNING_REQUEST, best))

    def handle_planning_response(self, message, sender):
        success = message.msg_body
        if success:
            logging.info('Заказ успешно запланирован')
        else:
            logging.warning('Отказал, вариант невыполним')