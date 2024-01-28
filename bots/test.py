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
        self.turn = 0
        self.price = 8000
        self.enemyBuild = 0
        self.enemyLoon = 0

    
    def play_turn(self, rc: RobotController):
        self.turn += 1
        if len(rc.get_towers(rc.get_enemy_team())) > self.enemyBuild:
            self.price += 1000

        # if abs(len(rc.get_debris(rc.get_enemy_team())) - self.enemyLoon) > 0:
        #     self.price -= 100
        #     self.enemyLoon = len(rc.get_debris(rc.get_enemy_team()))

        if rc.get_balance(rc.get_ally_team()) > self.price:
            rc.send_debris(1, 51)

        

             

