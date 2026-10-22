import logging
from thespian.actors import ActorSystem

from reference_book import ReferenceBook
from base_entity import BaseEntity
from message import Message, MessageType
from order_agent import OrderAgent
from courier_agent import CourierAgent


TYPES_AGENTS = {
    'ORDER':   OrderAgent,
    'COURIER': CourierAgent,
}


class AgentsDispatcher:

    def __init__(self, scene, weights):
        self.actor_system = ActorSystem()
        self.reference_book = ReferenceBook()
        self.scene = scene
        self.weights = weights or {
            'finish': 0.25, 'start': 0.05, 'price': 0.40, 'wait': 0.30,
        }

    def add_entity(self, entity: BaseEntity) -> bool:
        entity_type = entity.get_type()
        agent_class = TYPES_AGENTS.get(entity_type)
        if not agent_class:
            logging.warning('Для типа %s не указан агент', entity_type)
            return False

        self.scene.entities[entity_type].append(entity)
        self.create_agent(agent_class, entity)
        return True

    def create_agent(self, agent_class, entity):
        agent = self.actor_system.createActor(agent_class)
        self.reference_book.add_agent(entity=entity, agent_address=agent)

        init_data = {
            'dispatcher': self,
            'scene': self.scene,
            'entity': entity,
            'weights': self.weights
        }
        self.actor_system.tell(agent, Message(MessageType.INITIALIZATION, init_data))