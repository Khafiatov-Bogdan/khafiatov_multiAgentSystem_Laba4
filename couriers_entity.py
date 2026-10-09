import typing
from base_entity import BaseEntity
from point import Point
from shedule_item import ScheduleItem


class CourierEntity(BaseEntity):

    def __init__(self, onto_desc: dict, init_dict_data: dict, scene=None):
        super().__init__(onto_desc, scene)
        self.number = init_dict_data.get('Табельный номер')
        self.name = init_dict_data.get('ФИО')

        x = float(init_dict_data.get('Координата начала x'))
        y = float(init_dict_data.get('Координата начала y'))
        self.start_point = Point(x, y)

        raw_types = init_dict_data.get('Типы заказов') or ''
        self.types = [t.strip() for t in raw_types.split(';') if t.strip()]

        self.price_start = float(init_dict_data.get('Стоимость начала'))
        self.price_per_time = float(init_dict_data.get('Стоимость за время'))
        self.velocity = float(init_dict_data.get('Скорость'))
        self.max_volume = float(init_dict_data.get('Объем ранца'))
        self.max_mass = float(init_dict_data.get('Грузоподъемность'))

        self.schedule: typing.List[ScheduleItem] = []

        self.uri = 'Courier' + str(self.number)

    def get_type(self):
        return 'COURIER'


    def get_last_point(self) -> Point:
        if not self.schedule:
            return self.start_point
        return self.schedule[-1].point_to

    def get_last_time(self) -> float:
        if not self.schedule:
            return 0.0
        return self.schedule[-1].end_time

    def estimate_order(self, order) -> dict:

        last_point = self.get_last_point()
        last_time = self.get_last_time()

        p1 = order.point_from
        p2 = order.point_to

        d_to_order = last_point.get_distance_to_other(p1)
        d_with_order = p1.get_distance_to_other(p2)

        t_move = d_to_order / self.velocity
        t_deliv = d_with_order / self.velocity

        arrival_time = last_time + t_move
        wait_end = max(arrival_time, order.time_from)
        delivery_start = wait_end
        delivery_end = delivery_start + t_deliv

        price = (t_move + t_deliv) * self.price_per_time + self.price_start

        return {
            'courier': self,
            'order': order,
            'variant_name': 'asap',
            'time_from': last_time,
            'time_to': delivery_end,
            'move_from': last_time,
            'move_to': arrival_time,
            'move_point_from': last_point,
            'move_point_to': p1,
            'wait_from': arrival_time,
            'wait_to': wait_end,
            'delivery_from': delivery_start,
            'delivery_to': delivery_end,
            'price': price,
        }

    def add_order_to_schedule(self, order, time_from, time_to, price, params) -> bool:
        if self.get_conflicts(time_from, time_to):
            return False

        move_item = ScheduleItem(
            order=order, rec_type='MOVE_TO',
            start_time=params['move_from'], end_time=params['move_to'],
            point_from=params['move_point_from'], point_to=params['move_point_to'],
            cost=(params['move_to'] - params['move_from']) * self.price_per_time,
            all_params=params,
        )
        wait_item = ScheduleItem(
            order=order, rec_type='WAIT',
            start_time=params['wait_from'], end_time=params['wait_to'],
            point_from=order.point_from, point_to=order.point_from,
            cost=0.0, all_params=params,
        )
        delivery_item = ScheduleItem(
            order=order, rec_type='DELIVERY',
            start_time=params['delivery_from'], end_time=params['delivery_to'],
            point_from=order.point_from, point_to=order.point_to,
            cost=(params['delivery_to'] - params['delivery_from']) * self.price_per_time,
            all_params=params,
        )
        self.schedule.extend([move_item, wait_item, delivery_item])
        return True


    def get_conflicts(self, start_time, end_time) -> typing.List[ScheduleItem]:
        conflicts = []
        for item in self.schedule:
            if start_time < item.end_time and end_time > item.start_time:
                conflicts.append(item)
        return conflicts