from src.player import Player
from src.map import Map
from src.robot_controller import RobotController
from src.game_constants import TowerType, Team, Tile, GameConstants, SnipePriority, get_debris_schedule
from src.debris import Debris
from src.tower import Tower

class BotPlayer(Player):
    def __init__(self, map: Map):
        self.map = map
        self.num_solar = 0

        self.BUMRUSH = False
        self.turn = 0
        self.price = 14000

    def get_tile_to_place(self, map, rc):
        for x in range(map.width):
            for y in range(map.height):
                if rc.can_build_tower(TowerType.SOLAR_FARM, x, y):
                    return (x,y)

    
    def play_turn(self, rc: RobotController):
        self.turn += 1
        if rc.get_balance(rc.get_ally_team()) + (self.num_solar*1600) > self.price:
            print(self.turn)
            self.BUMRUSH= True
            towers = rc.get_towers(rc.get_ally_team())
            for tower in towers:
                rc.sell_tower(tower.id)
        if self.BUMRUSH:
            if rc.can_send_debris(1,51):
                rc.send_debris(1, 51)
        else:
            if rc.get_balance(rc.get_ally_team()) + (self.num_solar*1600) < self.price - (200 * (10 + (2 * self.num_solar))):
                if rc.get_balance(rc.get_ally_team()) >= 2000:
                    tile_to_place = self.get_tile_to_place(self.map, rc)
                    rc.build_tower(TowerType.SOLAR_FARM, tile_to_place[0], tile_to_place[1])
                    self.num_solar += 1