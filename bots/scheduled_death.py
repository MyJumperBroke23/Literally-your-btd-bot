from src.player import Player
from src.map import Map
from src.robot_controller import RobotController
from src.game_constants import TowerType, Team, Tile, GameConstants, SnipePriority, get_debris_schedule
from src.debris import Debris
from src.tower import Tower
import numpy as np

class BotPlayer(Player):
    def __init__(self, map: Map):
        self.map = map
        self.num_solar = 0

        self.BUMRUSH = False
        self.turn = 0
        self.trc = RobotController(None, None)

        self.path_length = len(map.path)
        self.death_time = self.chooose_goal(path_length=self.path_length)
        print("death time ", self.death_time)

    def get_best_200_debris_cost(self,speed):
        
        min_health = 45
        max_health = 190

        while min_health < max_health:
            mid_health = (min_health + max_health + 1) // 2 
            cost = self.trc.get_debris_cost(speed, mid_health)

            if cost <= 200:
                min_health = mid_health 
            else:
                max_health = mid_health - 1

        return min_health


    def attempt_kill(self,goal_turn,path_length,goal=3000):
        total_damage = 0
        turn = 0
        money = 1500
        while(total_damage < goal and turn < goal_turn):
            min_speed = np.ceil((goal_turn - turn) / path_length)
            max_200_damage = self.get_best_200_debris_cost(min_speed)
            if money >= 200:
                money -= 200
                total_damage += max_200_damage
            turn+=1
            money+=10
            if money < 200:
                skip_turns = np.ceil((200 - money) / 10)
                turn += skip_turns
                money += 10*skip_turns

        return total_damage >= goal

    
    def chooose_goal(self,path_length,goal=3000):
        min_goal_turn = 150
        max_goal_turn = 1200

        while max_goal_turn - min_goal_turn >= 10:
            mid_goal_turn = (min_goal_turn + max_goal_turn) // 2
            if self.attempt_kill(mid_goal_turn,path_length=path_length,goal=goal):
                max_goal_turn = mid_goal_turn
            else:
                min_goal_turn = mid_goal_turn

        return max_goal_turn 
        

    
    def play_turn(self, rc: RobotController):
        self.turn+=1
        if rc.get_balance(rc.get_ally_team()) >= 200:
            min_speed = np.ceil((self.death_time - self.turn) / self.path_length)
            max_200_damage = self.get_best_200_debris_cost(min_speed)
            if rc.can_send_debris(max_200_damage, min_speed):
                rc.send_debris(max_200_damage,min_speed)

        