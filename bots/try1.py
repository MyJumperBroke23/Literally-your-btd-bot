import random
from src.game_constants import SnipePriority, TowerType
from src.robot_controller import RobotController
from src.player import Player
from src.map import Map

import numpy as np
from scipy.spatial import cKDTree

class BotPlayer(Player):
    def __init__(self, map: Map):
        self.map = map
        self.gunners, gunners_dict = self.count_target_tiles_within_radius(map.height, map.width, map.path, np.sqrt(60))
        self.bombs, bombs_dict = self.count_target_tiles_within_radius(map.height, map.width, map.path, np.sqrt(10))
        self.bomb_spots = list(filter(lambda x: map.is_space(x[1], x[0]), sorted(gunners_dict, key=lambda x: -bombs_dict[x])))
        self.gun_spots = list(filter(lambda x: map.is_space(x[1], x[0]), sorted(gunners_dict, key=lambda x: -gunners_dict[x])))
        self.bomb_pointer = 0
        self.farm_pointer = len(self.gun_spots)-1
        self.gun_pointer = 0
        self.tower_ids = np.empty((map.height, map.width))
        
    
    def play_turn(self, rc: RobotController):
        debris = rc.get_debris(rc.get_ally_team())
        self.expected_shots(rc)
        badness = 0
        for d in debris:
            badness += d.health * (21-d.total_cooldown)
            if d.total_cooldown > 20:
                print(d.total_cooldown)
        
        for i in range(self.farm_pointer, -1, -1):
            k = self.gun_spots[i]
            if rc.can_build_tower(TowerType.SOLAR_FARM, k[1], k[0]):
                rc.build_tower(TowerType.SOLAR_FARM, k[1], k[0])
                self.farm_pointer -= 1
            else:
                break

        print(badness / len(self.map.path), self.expected_shots(rc))
        if badness / len(self.map.path) > self.expected_shots(rc):
            
            # if rc.get_balance(rc.get_ally_team()) < 1000:
            #     break
            if self.gun_pointer > 3 * self.bomb_pointer+1:
                if self.bomb_pointer < len(self.bomb_spots):
                    bomb_spot = self.bomb_spots[self.bomb_pointer]
                    if self.bombs[bomb_spot] >= 7 and rc.get_balance(rc.get_ally_team()) > 1750:
                        if rc.can_build_tower(TowerType.BOMBER, bomb_spot[1], bomb_spot[0]):
                            rc.build_tower(TowerType.BOMBER, bomb_spot[1], bomb_spot[0])
                            self.bomb_pointer += 1
            else:
                if self.gun_pointer < len(self.gun_spots):
                    gun_spot = self.gun_spots[self.gun_pointer]
                    if self.gunners[gun_spot] >= 15 and rc.get_balance(rc.get_ally_team()) > 1000:
                        if rc.can_build_tower(TowerType.GUNSHIP, gun_spot[1], gun_spot[0]):
                            rc.build_tower(TowerType.GUNSHIP, gun_spot[1], gun_spot[0])
                            self.gun_pointer += 1

        if badness / len(self.map.path) > min(rc.get_health(rc.get_ally_team())/2 + self.expected_shots(rc), 2 * self.expected_shots(rc)):
            self.sell_farms(rc)
            # while badness / len(self.map.path) > self.expected_shots(rc) and rc.get_balance(rc.get_ally_team()) > 1000:

        

        
        self.towers_attack(rc)
        # if rc.get_balance(rc.get_ally_team()) > 250:
        #     rc.send_debris(1,51)

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

     
    def expected_shots(self, rc: RobotController):
        expected_snipes = 0
        expected_bombs = 0
        for k in rc.get_towers(rc.get_ally_team()):
            if k.type == TowerType.BOMBER:
                expected_bombs += self.bombs[k.y, k.x]/15
            elif k.type == TowerType.GUNSHIP:
                expected_snipes += self.gunners[k.y, k.x]/20
        return expected_snipes * 25 + expected_bombs * 6
    
    def sell_farms(self, rc: RobotController):
        self.farm_pointer = len(self.gun_spots) - 1
        for k in rc.get_towers(rc.get_ally_team()):
            if k.type == TowerType.SOLAR_FARM:
                rc.sell_tower(k.id)