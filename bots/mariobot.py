import random
from src.game_constants import SnipePriority, TowerType
from src.robot_controller import RobotController
from src.player import Player
from src.map import Map
from scipy.spatial import cKDTree
import numpy as np
import matplotlib.pyplot as plt
from bots.helper import createRangeDict


class BotPlayer(Player):
    def __init__(self, map: Map):
        self.map = map
        self.amt = {}
        self.notower = set()
        self.addtower = set()
        self.turns = 0
        self.bombs = 0
        self.snipes = 0
        self.farms = 0

        self.path = createRangeDict(map,radius=0)
        self.bombers = createRangeDict(map,radius=10)
        self.snipers = createRangeDict(map,radius=60) - self.bombers

    def play_turn(self, rc: RobotController):
        self.build_towers(rc)
        self.towers_attack(rc)
        self.turns += 1

    def least_fit(self, rc):
        if self.turns % 100 == 0:
            towers = rc.get_towers(rc.get_ally_team())
            for tower in towers:
                loc = (tower.x, tower.y)
                if self.amt[loc] < self.turns/100:
                    self.notower.add(loc)
                    self.addtower.remove(loc)
                    rc.sell_tower(tower.id)


    def build_towers(self, rc: RobotController):
        tower = random.randint(1, 2) # randomly select a tower
        
        print(self.snipes > self.bombs*3)
        if self.snipes > self.bombs*3 or tower == 1:
            for (y,x), _ in self.bestiles:
                if rc.can_build_tower(TowerType.BOMBER, x,y):
                    rc.build_tower(TowerType.BOMBER, x,y)
                    self.bombs += 1

        else:
            for (y,x), _ in self.bestiles:
                px = random.randint(-3, 3)
                py = random.randint(-3, 3)

                if rc.can_build_tower(TowerType.GUNSHIP, px+x, py+y):
                    rc.build_tower(TowerType.GUNSHIP, px+x, py+y)
                    self.snipes += 1
        
    def towers_attack(self, rc: RobotController):
        towers = rc.get_towers(rc.get_ally_team())
        for tower in towers:
            num_debri = len(rc.sense_debris_in_range_of_tower(rc.get_ally_team(), tower.id))
            if num_debri > 0 and tower.current_cooldown == 0:
                if tower.type == TowerType.GUNSHIP:
                #     self.amt[(tower.x, tower.y)] += 25

                    rc.auto_snipe(tower.id, SnipePriority.STRONG)
                    
                elif tower.type == TowerType.BOMBER:
                    # self.amt[(tower.x, tower.y)] += 6*num_debri
                    rc.auto_bomb(tower.id)
