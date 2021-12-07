
from infracity.read_images import get_object_id


class Vehicle():

    def __init__(self, name, vtype, common_base_name=None):
        self.name = name
        self.vtype = vtype
        self.common_base_name = common_base_name
        self.stops = []
        
    def add_stop(self, block_position):
        if block_position not in self.stops:
            self.stops.insert(0, block_position)

    @property
    def start_position(self):
        return {"x": self.stops[0]["x"], "y": self.stops[0]["y"]}

    def generate(self):
        pass
