import logging
class ReferenceBook:

    def __init__(self):
        self.agents_entities = {}

    def add_agent(self, entity, agent_address):
        self.agents_entities[entity] = agent_address

    def get_address(self, entity):
        if entity not in self.agents_entities:
            logging.error(f'Агент {entity} отсутствует в адресной книге')
            return None
        return self.agents_entities[entity]