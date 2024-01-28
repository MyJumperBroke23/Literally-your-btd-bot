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
        self.goal = 4000
        self.trc = RobotController(None, None)
        self.max_overall_cool = 2

        self.path_length = len(map.path)-1
        self.schedule = {}
        self.send_amounts = {}
        self.damage_amounts = {}
        self.death_time = self.chooose_goal(path_length=self.path_length,goal=self.goal)
        self.schedule = {}
        self.send_amounts = {}
        self.damage_amounts = {}

        

        self.damage_scheduled = 0
        

        self.attempt_kill(goal_turn=self.death_time,path_length=self.path_length,goal=self.goal)
        # print(self.schedule)
        # print(self.send_amounts)
        # print(self.damage_amounts)

        

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


    def attempt_kill(self,goal_turn,path_length,goal):
        total_damage = 0
        turn = 0
        money = 1500
        while(total_damage < goal and turn + path_length < goal_turn):
            min_speed = min(self.max_overall_cool,max(1,np.floor((goal_turn - turn) / path_length)))
            max_200_damage = self.get_best_200_debris_cost(min_speed)
            self.damage_amounts[min_speed]=max_200_damage
            if money >= 200:
                self.schedule[min_speed] = goal_turn - min_speed * self.path_length
                if min_speed in self.send_amounts:
                    self.send_amounts[min_speed] += 1
                else:
                    self.send_amounts[min_speed]= 1
                
                money -= 200
                total_damage += max_200_damage
            turn+=1
            money+=10
            if money < 200:
                skip_turns = np.ceil((200 - money) / 10)
                turn += skip_turns
                money += 10*skip_turns


        return total_damage >= goal

    
    def chooose_goal(self,path_length,goal):
        min_goal_turn = 150
        max_goal_turn = 1200

        while max_goal_turn - min_goal_turn > 1:
            mid_goal_turn = (min_goal_turn + max_goal_turn) // 2
            if self.attempt_kill(mid_goal_turn,path_length=path_length,goal=goal):
                max_goal_turn = mid_goal_turn
            else:
                min_goal_turn = mid_goal_turn
                

        return max_goal_turn 
        

    
    def play_turn(self, rc: RobotController):

        towers = rc.get_towers(rc.get_enemy_team())
        if self.turn < 3:
            pass
        if self.turn%50 == 3:
            self.schedule = {}
            self.send_amounts = {}
            self.damage_amounts = {}
            if (len(towers) == 0 or (all([tower.type for tower in towers]) and towers[0].type == TowerType.SOLAR_FARM)):       
                self.goal = 3200
                self.max_overall_cool = 8
            else:    
                self.goal = 5800
                self.max_overall_cool = 2


            self.death_time = self.chooose_goal(path_length=self.path_length,goal=self.goal)
            self.schedule = {}
            self.send_amounts = {}
            self.damage_amounts = {}
            self.attempt_kill(goal_turn=self.death_time,path_length=self.path_length,goal=self.goal)


        # print("hello we are calling")

        self.turn+=1
        if rc.get_balance(rc.get_ally_team()) >= 200:
            if self.turn>self.death_time:
                if rc.can_send_debris(1,51):
                    rc.send_debris(1, 51)
            else:
                min_speed = min(self.max_overall_cool,max(1,np.floor((self.death_time - self.turn) / self.path_length)))
                
                max_200_damage = self.get_best_200_debris_cost(min_speed)
                min_speed = int(min_speed)                
                if self.schedule[min_speed] < self.turn + self.send_amounts[min_speed] + 1 and rc.can_send_debris(min_speed,max_200_damage ):
                    # print(self.schedule[min_speed],self.turn ,self.send_amounts[min_speed])
                    # print(f"current time {self.turn} sending at cooldown {min_speed} for {max_200_damage} impact at time ", self.turn + min_speed * self.path_length)
                    self.damage_scheduled+=max_200_damage
                    # print(f"total scheduled death {self.damage_scheduled}")
                    rc.send_debris(min_speed,max_200_damage)

        