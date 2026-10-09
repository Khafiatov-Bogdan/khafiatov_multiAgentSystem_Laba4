from base_entity import BaseEntity
from point import Point


class OrderEntity(BaseEntity):

    def __init__(self, onto_desc: dict, init_dict_data: dict, scene=None):
        super().__init__(onto_desc, scene)
        self.number = init_dict_data.get('Номер')
        self.name = init_dict_data.get('Наименование')
        self.weight = float(init_dict_data.get('Масса'))
        self.volume = float(init_dict_data.get('Объем'))
        self.price = float(init_dict_data.get('Стоимость'))

        x1 = float(init_dict_data.get('Координата получения x'))
        y1 = float(init_dict_data.get('Координата получения y'))
        self.point_from = Point(x1, y1)

        x2 = float(init_dict_data.get('Координата доставки x'))
        y2 = float(init_dict_data.get('Координата доставки y'))
        self.point_to = Point(x2, y2)

        self.time_from = float(init_dict_data.get('Время получения заказа'))
        self.time_to = float(init_dict_data.get('Время доставки заказа'))
        self.order_type = init_dict_data.get('Тип заказа')

        self.uri = 'Order' + str(self.number)

    def get_type(self):
        return 'ORDER'