import random
from src.game_constants import SnipePriority, TowerType
from src.robot_controller import RobotController
from src.player import Player
from src.map import Map

import numpy as np
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt

class BotPlayer(Player):
    def __init__(self, map: Map):
        self.map = map
        self.gunners, gunners_dict = self.count_target_tiles_within_radius(map.height, map.width, map.path, np.sqrt(60))
        self.bombs, bombs_dict = self.count_target_tiles_within_radius(map.height, map.width, map.path, np.sqrt(10))
        self.farm_spots = sorted(gunners_dict, key=lambda x: gunners_dict[x])
        self.bomb_spots = sorted(gunners_dict, key=lambda x: -bombs_dict[x])
        self.toggle =False
    
    def play_turn(self, rc: RobotController):
        # if len(self.bomb_spots) > 0:
        #     bomb_spot = self.bomb_spots[0]
        #     if self.bombs[bomb_spot] >= 7 and rc.get_balance(rc.get_ally_team()) > 1750:
        #         if rc.can_build_tower(TowerType.GUNSHIP, bomb_spot[1], bomb_spot[0]):
        #             rc.build_tower(TowerType.GUNSHIP, bomb_spot[1], bomb_spot[0])
        #         self.bomb_spots.pop(0)
                
        # if len(rc.get_towers(rc.get_ally_team())) < 10:

        #     for k in self.farm_spots:
        #         if rc.can_build_tower(TowerType.SOLAR_FARM, k[1], k[0]):
        #             rc.build_tower(TowerType.SOLAR_FARM, k[1], k[0])
        #             self.farm_spots.pop()
        #             break
        
        if rc.get_balance(rc.get_ally_team()) > 12000:
            self.toggle = True
        if self.toggle and rc.get_balance(rc.get_ally_team()) > 253:
            rc.send_debris(2, 51)
        self.towers_attack(rc)

        return

    def count_target_tiles_within_radius(self, rows, cols, target_tiles, radius):

        result = np.zeros((rows, cols))
        r_dict = {}

        tree = cKDTree(target_tiles)

        for y in range(rows):
            for x in range(cols):

                # Query the KD-tree for points within the radius
                neighbors = tree.query_ball_point((x,y), radius)

                # Count the number of target tiles within the radius
                count = sum(1 for neighbor in neighbors)

                result[y,x] = count
                r_dict[(y,x)] = count





        return result, r_dict
    
    def towers_attack(self, rc: RobotController):
        towers = rc.get_towers(rc.get_ally_team())
        for tower in towers:
            if tower.type == TowerType.GUNSHIP:
                rc.auto_snipe(tower.id, SnipePriority.FIRST)
            elif tower.type == TowerType.BOMBER:
                rc.auto_bomb(tower.id)

     
