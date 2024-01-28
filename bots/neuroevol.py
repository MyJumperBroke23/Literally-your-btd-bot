import random
from src.game_constants import SnipePriority, TowerType
from src.robot_controller import RobotController
from src.player import Player
from src.map import Map
from scipy.spatial import cKDTree
import numpy as np


class BotPlayer(Player):
    def __init__(self, map: Map):
        self.map = map
        self.amt = {}
        self.notower = set()
        self.addtower = set()
        self.turns = 0
        self.bombs = 0
        self.snipes = 0
        self.farm = True
        _, self.bombtiles = self.count_target_tiles_within_radius(map.width, map.height, map.path, 2)
        result, self.sniptiles = self.count_target_tiles_within_radius(map.width, map.height, map.path, 10)

        rem = []
        for i in self.sniptiles:
            # self.sniptiles[i] -= self.bombtiles[i]
            if self.bombtiles[i] > 0:
                rem.append(i)

        for i in rem:
            del self.sniptiles[i]

        # print(set().difference(set()))
        # print(len(self.sniptiles.keys()), len(self.bombtiles.keys()))
        # diff = set(self.sniptiles.keys()).difference(set(self.bombtiles.keys()))
        # print(diff)
        # for i in self.sniptiles:
        #     if i not in diff:
                # print('not')
        #         del self.sniptiles[i]



        # self.bestiles = sorted(self.bombtiles, key=lambda x: x[1], reverse=True)
        # plt.imshow(np.flipud(result))
        # plt.show()
        self.bestiles = sorted(self.bombtiles.items(), key=lambda item: item[1], reverse=True)
        self.bestsnipes = sorted(self.sniptiles.items(), key=lambda item: item[1], reverse=True)
        



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

    def play_turn(self, rc: RobotController):
        self.build_towers(rc)
        self.towers_attack(rc)
        self.turns += 1
        # if (self.turns % 10 == 0){
        # self.remove_least_fit(rc)
            # print("here")
            # self.remove_least_fit(rc)
        # }

        # self.least_fit(rc)

    # def remove_least_fit(self, rc: RobotController):
    #     towers = rc.get_towers(rc.get_ally_team())
    #         for tower in towers:
    #             loc = (tower.x, tower.y)
    #             if self.amt[loc] < 2 * self.turns:
    #                 self.notower.add(loc)
    #                 self.addtower.remove(loc)
    #                 print("deleted")

            
    # def least_fit(self, rc):
    #     if self.turns % 100 == 0:
    #         towers = rc.get_towers(rc.get_ally_team())
    #         for tower in towers:
    #             loc = (tower.x, tower.y)
    #             if self.amt[loc] < self.turns/100:
    #                 self.notower.add(loc)
    #                 self.addtower.remove(loc)
    #                 rc.sell_tower(tower.id)


    def build_towers(self, rc: RobotController):
        # x = random.randint(0, self.map.width-1)
        # y = random.randint(0, self.map.height-1)
        tower = random.randint(1, 3) # randomly select a tower
        # print(self.bestiles[0])
        # print(rc.can_build_tower(TowerType.BOMBER, 0,29))
        
        # print(self.snipes > self.bombs*3)

        # if self.farm:
        #     # for i in range(len(self.bestsnipes)):
        #         # (y,x) = self.bestsnipes[-1][0]
        #     if rc.can_build_tower(TowerType.SOLAR_FARM, 0,0):
        #         rc.build_tower(TowerType.SOLAR_FARM, 0,0)
        #         self.farm = False
        #     return

        if self.snipes > self.bombs*3 or tower == 1:
            for (y,x), _ in self.bestiles:
                if rc.can_build_tower(TowerType.BOMBER, x,y):
                    rc.build_tower(TowerType.BOMBER, x,y)
                    self.bombs += 1

        else:
            for (y,x), _ in self.bestiles:
                # px = random.randint(-3, 3)
                # py = random.randint(-3, 3)
                if rc.can_build_tower(TowerType.GUNSHIP, x,y):
                    rc.build_tower(TowerType.GUNSHIP, x,y)
                    self.snipes += 1

        # else:
        #     if rc.get_balance(rc.get_ally_team()) > 57:
        #         rc.send_debris(1, 26)
            
            # print(x,y)
            # if (rc.can_build_tower(TowerType.GUNSHIP, x, y) and 
            #     rc.can_build_tower(TowerType.BOMBER, x, y) and
            #     rc.can_build_tower(TowerType.SOLAR_FARM, x, y) and
            #     rc.can_build_tower(TowerType.REINFORCER, x, y)
            # ):

            # if rc.can_build_tower(TowerType.BOMBER, x,y):
                # if (x,y) not in self.notower:
                # self.addtower.add((x,y))
                # self.amt[(x,y)] = 0
                    # if tower == 1:
                # rc.build_tower(TowerType.BOMBER, x,y)
                # print(x,y)
                    # elif tower == 2:
                    #     rc.build_tower(TowerType.GUNSHIP, x, y)
                    # elif tower == 3:
                    #     rc.build_tower(TowerType.SOLAR_FARM, x, y)
                    # elif tower == 4:
                    #     rc.build_tower(TowerType.REINFORCER, x, y)
        
    def towers_attack(self, rc: RobotController):
        towers = rc.get_towers(rc.get_ally_team())
        for tower in towers:
            num_debri = len(rc.sense_debris_in_range_of_tower(rc.get_ally_team(), tower.id))
            if num_debri > 0 and tower.current_cooldown == 0:
                if tower.type == TowerType.GUNSHIP:
                #     self.amt[(tower.x, tower.y)] += 25

                    rc.auto_snipe(tower.id, SnipePriority.WEAK)
                    
                elif tower.type == TowerType.BOMBER:
                    # self.amt[(tower.x, tower.y)] += 6*num_debri
                    rc.auto_bomb(tower.id)
