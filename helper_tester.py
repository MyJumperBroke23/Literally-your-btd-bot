from bots.helper import createRangeDict
from src.map import Map

def main():
    map_path = "maps/biki_bott.awap24m"
    map = Map(map_path)
    createRangeDict(map)

if __name__ == "__main__":
    main()