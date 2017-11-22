import pygame
from pygame.locals import KEYDOWN, QUIT, MOUSEBUTTONDOWN, K_RETURN, K_ESCAPE
import sys
from collections import namedtuple

mutationRate = 0.1;
crossOverRate = 0.6;

list_cities = []


def open_file(path):
    if path:
        with open(path, 'r') as file:
            for line in file:
                content = line.split()
                list_cities.append(City((int(content[1]), int(content[2])), content[0]))
    else:
        print("File doesn't exist")

def launch_gui():
    screen_x = 500
    screen_y = 500

    city_color = [10, 10, 200]  # blue
    city_radius = 3

    font_color = [255, 255, 255]  # white

    pygame.init()
    window = pygame.display.set_mode((screen_x, screen_y))
    pygame.display.set_caption('Exemple')
    screen = pygame.display.get_surface()
    font = pygame.font.Font(None, 30)

    def draw(positions):
        screen.fill(0)
        for pos in positions:
            pygame.draw.circle(screen, city_color, pos, city_radius)
        text = font.render("Nombre: %i" % len(positions), True, font_color)
        textRect = text.get_rect()
        screen.blit(text, textRect)
        pygame.display.flip()

    cities = []
    draw(cities)

    collecting = True

    while collecting:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN and event.key == K_RETURN:
                collecting = False
            elif event.type == MOUSEBUTTONDOWN:
                cities.append(pygame.mouse.get_pos())
                list_cities.append(City("bidon",pygame.mouse.get_pos()))
                draw(cities)

    screen.fill(0)
    pygame.draw.lines(screen, city_color, True, cities)
    text = font.render("Un chemin, pas le meilleur!", True, font_color)
    textRect = text.get_rect()
    screen.blit(text, textRect)
    pygame.display.flip()

    while True:
        event = pygame.event.wait()
        if event.type == KEYDOWN: break

def selection():
    pass


def mutate():
    pass


def evaluate():
    pass


def ga_solve(file=None, gui=True, maxtime=0):
    if gui:
        launch_gui()
    else:
        open_file(sys.argv[1])


class City(object):
    def __init__(self, pos, name=None):
        self.name = name
        self.pos = pos


if __name__ == '__main__':
    
    open_file("Ressources/data/pb005.txt")
    ga_solve(gui=False)

