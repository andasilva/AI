import sys
from pygame.math import Vector2


def open_file(path):
    list_cities = None
    if path:
        list_cities = []
        with open(path, 'r') as file:
            for line in file:
                content = line.split()
                list_cities.append(City((int(content[1]), int(content[2])), content[0]))
    else:
        print("File doesn't exist")


def selection():
    pass


def mutate():
    pass


def evaluate():
    pass


def ga_solve(file=None, gui=True, maxtime=0):
    pass


class City(object):
    def __init__(self, pos, name=None):
        self.name = name
        self.pos = pos


if __name__ == '__main__':
    
    open_file("Ressources/data/pb005.txt")
    ga_solve()


