import pygame
from pygame.locals import KEYDOWN, QUIT, MOUSEBUTTONDOWN, K_RETURN, K_ESCAPE
from math import hypot, sqrt
import sys
import datetime
import random
import argparse
from copy import deepcopy

end = None
max_time_if_algorithm_stagnant = 5
time_specified = False

mutation_rate = 0.4
cross_over_rate = 0.1
population_size = 20
number_of_survivors = int(population_size / 2)

# Contient la population
populations = []

# Villes récupéré depuis le fichier/gui
list_cities = []

# Best fitness reached
best_chromosome = None

# Résultat à dessiner
cities_to_draw = []

# has all the distance between two cities
distances = []

# Survivors after selections
survivors = []

# Pygame attributs
font = None
screen = None
city_color = [10, 10, 200]  # blue
city_radius = 3
font_color = [255, 255, 255]  # white


def draw_path(city_path):
    screen.fill(0)
    pygame.draw.lines(screen, city_color, True, city_path)
    pygame.display.flip()


def init_pygame():
    """
    Init Pygame GUI
    """
    global screen, font

    screen_x = 500
    screen_y = 500

    pygame.init()
    pygame.display.set_mode((screen_x, screen_y))
    pygame.display.set_caption('Le voyageur de commerce')
    screen = pygame.display.get_surface()
    font = pygame.font.Font(None, 30)


def collect_data():
    def draw(positions):
        """
        Draw the connections between cities position
        """
        global screen, font
        screen.fill(0)
        for pos in positions:
            pygame.draw.circle(screen, city_color, pos, city_radius)
        text = font.render("Nombre: %i" % len(positions), True, font_color)
        text_rect = text.get_rect()
        screen.blit(text, text_rect)
        pygame.display.flip()

    collecting = True

    counter = 0
    while collecting:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN and event.key == K_RETURN:
                collecting = False
            elif event.type == MOUSEBUTTONDOWN:
                cities_to_draw.append(pygame.mouse.get_pos())
                list_cities.append(City(pygame.mouse.get_pos(), "v{}".format(counter)))
                draw(cities_to_draw)
                counter += 1


def display_result():
    draw_path(cities_to_draw)

    text = font.render("Un chemin, pas le meilleur!", True, font_color)
    text_rect = text.get_rect()
    screen.blit(text, text_rect)
    pygame.display.flip()

    while True:
        event = pygame.event.wait()
        if event.type == KEYDOWN:
            break


def open_file(path):
    if path:
        with open(path, 'r') as file:
            for line in file:
                content = line.split()
                list_cities.append(City((int(content[1]), int(content[2])), content[0]))
    else:
        print("File doesn't exist")


def populate(size):
    """ Create an initial population """

    for i in range(size):
        first_city = random.choice(list_cities)
        best_order = []
        best_length = float('inf')

        length = 0
        order = [first_city]
        next_c, dist = get_closest(first_city, list_cities, order)
        length += dist
        order.append(next_c)
        while len(order) < len(list_cities):
            next_c, dist = get_closest(next_c, list_cities, order)
            length += dist
            order.append(next_c)

            if length < best_length:
                best_length = length
                best_order = order

        populations.append(Chromosome(best_order))


def get_closest(city, cities, visited):
    best_distance = float('inf')

    for c in cities:

        if c not in visited:
            distance = dist_squared(city, c)

            if distance < best_distance:
                closest_city = c
                best_distance = distance

    return closest_city, best_distance


def dist_squared(c1, c2):
    t1 = c2.pos[0] - c1.pos[0]
    t2 = c2.pos[1] - c1.pos[1]

    return t1**2 + t2**2


def calculate_all_distance():
    for i in range(len(list_cities)):
        distances.append([])
        for j in range(len(list_cities)):
            if i == j:
                distances[i].append(0)
            else:
                city1 = list_cities[i]
                city2 = list_cities[j % len(list_cities)]
                x1 = city1.pos[0]
                x2 = city2.pos[0]
                y1 = city1.pos[1]
                y2 = city2.pos[1]
                distance = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                distances[i].append(distance)


def processing():
    while datetime.datetime.now() < end:
        evaluate()
        selection()
        crossing()
        mutate()

    print(best_chromosome.fitness, end=" ")
    for city in best_chromosome.list_cities:
        print(city.name, end=" ")


def evaluate():
    """ Evaluate the population """
    for i in range(len(populations)):
        chromosome = populations[i]
        total_distance = 0
        cities = chromosome.list_cities

        for i in range(len(cities)):
            city1 = cities[i]
            city2 = cities[(i + 1) % len(cities)]
            index_city1 = next(i for i, item in enumerate(list_cities) if item.name == city1.name)
            index_city2 = next(i for i, item in enumerate(list_cities) if item.name == city2.name)
            total_distance += distances[index_city1][index_city2]

        chromosome.fitness = total_distance


def selection():
    """Sélectionner une sous-partie de la population qui servira de base à la population suivante"""
    global cities_to_draw, best_chromosome, survivors, end

    populations.sort(key=lambda x: x.fitness)

    """
    Met à jour le meilleur chromosome trouvé pour garder une trace du meilleure chromosome
    """
    if best_chromosome is None:
        if not time_specified:
            end = datetime.datetime.now() + datetime.timedelta(seconds=max_time_if_algorithm_stagnant)
        best_chromosome = deepcopy(populations[0])
        cities_to_draw = [city.pos for city in best_chromosome.list_cities]
        if args.nogui is False:
            draw_path(cities_to_draw)
    else:
        if populations[0].fitness < best_chromosome.fitness:
            if not time_specified:
                end = datetime.datetime.now() + datetime.timedelta(seconds=max_time_if_algorithm_stagnant)
            best_chromosome = deepcopy(populations[0])
            cities_to_draw = [city.pos for city in best_chromosome.list_cities]
            if args.nogui is False:
                draw_path(cities_to_draw)
            print(best_chromosome.fitness)

    """
    Créer la prochaine population
    """
    survivors = populations[:number_of_survivors]


def crossing():
    global populations
    cutting_point = int(len(list_cities) * cross_over_rate)
    populations[:] = []
    survivors.append(best_chromosome)

    # Feel populations with new chromosomes
    for i in range(population_size):
        choice = random.sample(range(len(survivors) - 1), 2)
        first_slice_1 = survivors[choice[0]].list_cities[:cutting_point]
        second_slice_1 = survivors[choice[1]].list_cities[cutting_point:]

        first_slice_2 = survivors[choice[0]].list_cities[cutting_point:]
        second_slice_2 = survivors[choice[1]].list_cities[:cutting_point]

        chromosome_prototype = first_slice_1 + second_slice_1
        chromosome_prototype_tool = first_slice_2 + second_slice_2  # used to get the others repeated values to exchange

        duplicates_value = [x for n, x in enumerate(chromosome_prototype) if x in chromosome_prototype[:n]]
        duplicates_value_to_exchange = [x for n, x in enumerate(chromosome_prototype_tool) if
                                        x in chromosome_prototype_tool[:n]]
        # Swap values
        for index, city in enumerate(chromosome_prototype):
            if city in duplicates_value:
                chromosome_prototype[index] = duplicates_value_to_exchange[0]
                del duplicates_value[duplicates_value.index(city)]
                del duplicates_value_to_exchange[0]

        populations.append(Chromosome(chromosome_prototype))


def mutate():
    for chromosome in populations:
        for index in range(len(list_cities)):
            if index != 0:
                if round(random.uniform(0, 1), 2) <= mutation_rate / 2:
                    random_position = random.randint(0, len(list_cities) - 1)  # todo random_position != index
                    chromosome.list_cities[index], chromosome.list_cities[random_position] = \
                        chromosome.list_cities[random_position], chromosome.list_cities[index]


def ga_solve(file=None, gui=True, maxtime=0):
    global end, time_specified

    if gui:
        init_pygame()
        if file is None:
            collect_data()
        else:
            open_file(file)

        if maxtime is not None and not 0:
            end = datetime.datetime.now() + datetime.timedelta(seconds=maxtime)
            time_specified = True
        else:
            end = datetime.datetime.now() + datetime.timedelta(seconds=max_time_if_algorithm_stagnant)
        calculate_all_distance()
        populate(population_size)
        processing()
        display_result()
    else:
        if file is None:
            init_pygame()
            collect_data()
            end = datetime.datetime.now() + datetime.timedelta(seconds=max_time_if_algorithm_stagnant)
        else:
            open_file(file)
        if maxtime is not None:
            end = datetime.datetime.now() + datetime.timedelta(seconds=maxtime)
            time_specified = True
        else:
            end = datetime.datetime.now() + datetime.timedelta(seconds=max_time_if_algorithm_stagnant)
        calculate_all_distance()
        populate(population_size)
        processing()


class City(object):
    def __init__(self, pos, name=None):
        self.name = name
        self.pos = pos


class Chromosome(object):
    def __init__(self, cities_path):
        self.list_cities = cities_path
        self.fitness = 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Gander & Neto da Silva André AI Algorithm")
    parser.add_argument('--nogui',
                        dest='nogui',
                        action='store_true',
                        help='Ne pas afficher l\'évolution de l\'algorithme',
                        )

    parser.add_argument('--maxtime',
                        dest='maxtime',
                        help='Temps maximum d\'éxécution',
                        type=int
                        )

    parser.add_argument(dest='file',
                        help='Fichier qui contient les coordonées des villes',
                        nargs='?'
                        )

    args = parser.parse_args()

    ga_solve(args.file, not args.nogui, args.maxtime)
