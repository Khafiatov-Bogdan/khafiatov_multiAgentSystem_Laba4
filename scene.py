from collections import defaultdict
import typing


class Scene:
    def __init__(self):
        self.entities = defaultdict(list)

    def get_entities_by_type(self, entity_type) -> typing.List:
        return self.entities[entity_type]