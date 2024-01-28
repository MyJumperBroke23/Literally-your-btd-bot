from src.player import Player
from src.map import Map
from src.game import Game
from src.robot_controller import RobotController
from src.game_constants import TowerType, Team, Tile, GameConstants, SnipePriority, get_debris_schedule
from src.debris import Debris
from src.tower import Tower
import numpy as np
from scipy import ndimage

# Heuristic to see how much "Danger" a team is in
def senseDanger(team: Team, map: Map):
    path = map.path
    debrisList = RobotController.get_debris(team)
    return (max([debris.progress for debris in debrisList])/len(path)) - 0.5

# Calculates new distribution of resources given current state of game
def calculate_new_resource_distribution(map: Map):
    ally_team = RobotController.get_ally_team()
    enemy_team = RobotController.get_enemy_team()
    base_tower = 0.75
    base_farm = 0.25
    base_balloon = 0.05

    your_danger = senseDanger(ally_team, map)
    their_danger = senseDanger(enemy_team(), map)
    your_health = RobotController.get_health(ally_team)/2500
    your_health_normalized = (-your_health + 0.125) * 0.75
    their_health = RobotController.get_health(enemy_team)/2500
    their_health_normalized = (-their_health + 0.125) * 0.75

    new_tower = base_tower + your_health_normalized + your_danger
    new_balloon = base_balloon + their_health_normalized + their_danger

    total_sum = new_tower + new_balloon + base_farm

    return(new_tower/total_sum, base_farm/total_sum, new_balloon/base_farm)








# Given a map, create a dict that maps (row,col,range) -> all path squares if shooter, all non tile squares if intensifier
def createRangeDict(map: Map, radius = 4):
    rangeDict = dict()
    path = map.path

    dimension = 2 * np.ceil(np.sqrt(radius))+1

    height_coords = np.arange(dimension)
    width_coords = np.arange(dimension)

    

    center_h = np.ceil(np.sqrt(radius))
    center_w = np.ceil(np.sqrt(radius))

    dh = (height_coords - center_h)**2
    dw = ((width_coords - center_w)**2)
    d = dh[..., np.newaxis] + dw[np.newaxis, ...] 
    mask = (d <= radius).astype(int)
    path = [[1 if map.is_path(i,j) else 0 for j in range(map.width)] for i in range(map.height)]
    path = np.array(path)
    result = ndimage.convolve(path, mask, mode='constant', cval=0.0)



