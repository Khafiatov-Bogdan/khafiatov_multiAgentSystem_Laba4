import logging
import time

from excel_utils import get_excel_data
from scene import Scene
from order_entity import OrderEntity
from couriers_entity import CourierEntity
from agents_dispatcher import AgentsDispatcher

def load_weights(filename):
    rows = get_excel_data(filename, 'Веса')
    weights = {}
    for row in rows:
        criterion = row['Критерий']
        weight = float(row['Вес'])
        weights[criterion] = weight

    total = sum(weights.values())
    if abs(total - 1.0) > 0.001:
        logging.warning('Сумма весов = %.3f, должна быть 1.0', total)
    return weights

def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s')

    filename = 'Исходные данные.xlsx'
    weights = load_weights(filename)
    scene = Scene()
    dispatcher = AgentsDispatcher(scene, weights)



    couriers_raw = get_excel_data(filename, 'Курьеры')
    for row in couriers_raw:
        courier = CourierEntity({}, row, scene)
        dispatcher.add_entity(courier)

    orders_raw = get_excel_data(filename, 'Заказы')
    for row in orders_raw:
        order = OrderEntity({}, row, scene)
        dispatcher.add_entity(order)
    time.sleep(5)

    for courier in scene.get_entities_by_type('COURIER'):
        print(f'\n=== Курьер {courier.name} ===')
        for item in courier.schedule:
            print(f'  {item.rec_type}: {item.start_time:.2f} → {item.end_time:.2f}, '
                  f'{item.point_from} → {item.point_to}, цена {item.cost:.2f}')


if __name__ == '__main__':
    main()