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
        self.finish_weight = 0
        self.start_weight = 0
        self.price_weight = 0
        self.wait_weight = 0

        self.subscribe(MessageType.PRICE_RESPONSE, self.handle_price_response)
        self.subscribe(MessageType.PLANNING_RESPONSE, self.handle_planning_response)


    def handle_init_message(self, message, sender):
        super().handle_init_message(message, sender)
        data = message.msg_body
        weights = data.get('weights')
        if weights:
            self.finish_weight = weights.get('finish', self.finish_weight)
            self.start_weight = weights.get('start', self.start_weight)
            self.price_weight = weights.get('price', self.price_weight)
            self.wait_weight = weights.get('wait', self.wait_weight)
        self.__send_params_request()

    def __send_params_request(self):
        all_couriers = self.scene.get_entities_by_type('COURIER')
        logging.info('%s — список курьеров: %s',
                     self.name, [c.name for c in all_couriers])

        order_type = self.entity.order_type
        order_point = self.entity.point_from
        K = 2

        good_courier = []
        for courier in all_couriers:
            if order_type not in courier.types:
                logging.info('%s: типы грузов %s %s не включают %s — пропускаем',
                             self.name, courier.name, courier.types, order_type)
                continue

            distance = courier.get_last_point().get_distance_to_other(order_point)
            good_courier.append((distance, courier))

        good_courier.sort(key=lambda pair: pair[0])
        good_courier = good_courier[:K]

        logging.info('%s — опрашиваем ближайших: %s',
                     self.name, [f'{c.name} ({d:.2f})' for d, c in good_courier])

        for _, courier in good_courier:
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
            logging.warning('%s: нет возможных вариантов для планирования', self.name)
            return

        self.__evaluate_variants()

        sorted_vars = sorted(self.possible_variants,
                             key=lambda x: x['total_efficiency'],
                             reverse=True)
        best = sorted_vars[0]
        self.possible_variants.remove(best)

        courier = best['courier']
        address = self.dispatcher.reference_book.get_address(courier)

        for v in sorted_vars:
            logging.info(
                '%s: [%s] от %s | start=%.2f finish=%.2f price=%.2f wait=%.2f → total=%.3f',
                self.name, v['variant_name'], v['courier'].name,
                v['start_efficiency'], v['finish_efficiency'],
                v['price_efficiency'], v['wait_efficiency'],
                v['total_efficiency'],
            )

        logging.info('%s выбрал [%s] от %s по свёртке: total=%.3f',
                     self.name, best['variant_name'], courier.name,
                     best['total_efficiency'])
        logging.info('%s → PLANNING_REQUEST курьеру %s', self.name, courier.name)

        self.send(address, Message(MessageType.PLANNING_REQUEST, best))

    def handle_planning_response(self, message, sender):
        success = message.msg_body
        if success:
            logging.info('Заказ успешно запланирован')
        else:
            logging.warning('Отказал, вариант невыполним')

    def __evaluate_variants(self):
        if not self.possible_variants:
            return


        all_start_times = [v['time_from'] for v in self.possible_variants]
        all_finish_times = [v['time_to'] for v in self.possible_variants]
        all_prices = [v['price'] for v in self.possible_variants]
        all_waits = [v['wait_to'] - v['wait_from'] for v in self.possible_variants]

        min_start, max_start = min(all_start_times), max(all_start_times)
        min_finish, max_finish = min(all_finish_times), max(all_finish_times)
        min_price, max_price = min(all_prices), max(all_prices)
        min_wait, max_wait = min(all_waits), max(all_waits)

        for v in self.possible_variants:
            v['start_efficiency'] = self.get_decreasing_kpi_value(
                v['time_from'], min_start, max_start)
            v['finish_efficiency'] = self.get_decreasing_kpi_value(
                v['time_to'], min_finish, max_finish)
            v['price_efficiency'] = self.get_decreasing_kpi_value(
                v['price'], min_price, max_price)
            v['wait_efficiency'] = self.get_decreasing_kpi_value(
                v['wait_to'] - v['wait_from'], min_wait, max_wait)

            v['total_efficiency'] = (
                    self.finish_weight * v['finish_efficiency']
                    + self.start_weight * v['start_efficiency']
                    + self.price_weight * v['price_efficiency']
                    + self.wait_weight * v['wait_efficiency']
            )