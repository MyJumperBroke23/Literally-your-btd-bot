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
        self.send_first_52 = True
        self.turn = 0
        self.price = 10000 + (len(map.tiles)*90)

    def get_tile_to_place(self, map, rc):
        for x in range(map.width):
            for y in range(map.height):
                if rc.can_build_tower(TowerType.SOLAR_FARM, x, y):
                    return (x,y)

    def get_bum_rush_price(self, rc):
        towers = rc.get_towers(rc.get_enemy_team())
        if (len(towers) == 0 or (all([tower.type for tower in towers]) and towers[0].type == TowerType.SOLAR_FARM)):
            return 10535
        return self.price + (len(towers) * 100)
    
    def play_turn(self, rc: RobotController):
        self.turn += 1
        if rc.get_balance(rc.get_ally_team()) + (self.num_solar*1600) > self.get_bum_rush_price(rc):
            #print(self.turn)
            self.BUMRUSH= True
        if self.BUMRUSH:
            if self.send_first_52:
                if rc.can_send_debris(1,52):
                    rc.send_debris(1, 52)
                self.send_first_52 = False
            if rc.can_send_debris(1,51):
                rc.send_debris(1, 51)
            else:
                towers = rc.get_towers(rc.get_ally_team())
                if len(towers) == 0:
                    self.BUMRUSH = False
                else:
                    tower = towers[0]
                    rc.sell_tower(tower.id)
                    self.num_solar -=1
        else:
            if rc.get_balance(rc.get_ally_team()) + (self.num_solar*1600) < self.get_bum_rush_price(rc) - (200 * (10 + (2 * self.num_solar))):
                if rc.get_balance(rc.get_ally_team()) >= 2000:
                    tile_to_place = self.get_tile_to_place(self.map, rc)
                    rc.build_tower(TowerType.SOLAR_FARM, tile_to_place[0], tile_to_place[1])
                    self.num_solar += 1