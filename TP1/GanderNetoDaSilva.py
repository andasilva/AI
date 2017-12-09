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

# Processing configuration
mutation_rate = 0.5
cross_over_rate = 0.6
population_size = 30
number_of_elites = 3
two_opt_needed = False
counter_iteration_before_two_opt = 0
limit_iteration_before_two_opt = 3

# Contains all the chromosomes
populations = []

# Contains the cities retrieved by clicking or file
list_cities = []

# Contains the best chromosome found so far
best_chromosome = None

# Contains all the distances between two cities
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
    """
    Draw a path in the pygame window
    :param city_path: list of cities position
    """
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
    """
    Collect the cities with the position of the click in the Pygame window.
    Print the click in the Pygame window
    """

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
    cities_to_draw = []
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
    """
    Draw the best chromosome
    """
    draw_path([city.pos for city in best_chromosome.list_cities])

    text = font.render("Maybe the best path!", True, font_color)
    text_rect = text.get_rect()
    screen.blit(text, text_rect)
    pygame.display.flip()

    while True:
        event = pygame.event.wait()
        if event.type == KEYDOWN:
            break


def open_file(path):
    """
    Fill the cities list with the cities that are in the file
    :param path: Path to the file
    """
    if path:
        with open(path, 'r') as file:
            for line in file:
                content = line.split()
                list_cities.append(City((int(content[1]), int(content[2])), content[0]))
    else:
        print("File doesn't exist")


def populate(size):
    """
    Create a population with "size" chromosomes
    :param size: Size of the population
    """

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
    """
    Calculate the distance between two cities
    :param c1: city one
    :param c2: city two
    :return: distance squared between c1 and c2
    """
    return get_distance_between_two_cities(c1, c2) ** 2


def calculate_distance_between_two_cities(c1, c2):
    """
    Calculate the distance between two cities
    :param c1: city one
    :param c2: city two
    :return: distance between c1 and c2
    """
    x1 = c1.pos[0]
    x2 = c2.pos[0]
    y1 = c1.pos[1]
    y2 = c2.pos[1]
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def get_distance_between_two_cities(c1, c2):
    """
    Get the distance between two cities
    :param c1: city one
    :param c2: city two
    :return: distance between c1 and c2
    """
    return distances[int(c1.name[1:])][int(c2.name[1:])]


def calculate_all_distance():
    """
    Calculate all distance between all the cities and stores in an array.
    """
    for i in range(len(list_cities)):
        distances.append([])
        for j in range(len(list_cities)):
            if i == j:
                distances[i].append(0)
            else:
                city1 = list_cities[i]
                city2 = list_cities[j % len(list_cities)]
                distances[i].append(calculate_distance_between_two_cities(city1, city2))


def processing():
    """
    All processes are here and are executed as long as a terminal condition is not encountered
    """
    global two_opt_needed
    while datetime.datetime.now() < end:
        if two_opt_needed:
            # two_opt(best_chromosome.list_cities)
            two_opt_needed = False
        evaluate()
        selection()
        crossing()
        mutate()
        if counter_iteration_before_two_opt > limit_iteration_before_two_opt:
            two_opt_needed = True


def two_opt(chromosome):
    improvement = True
    draw_path([city.pos for city in chromosome])

    while improvement:
        improvement = False
        for index_1, city_1 in enumerate(chromosome):
            for index_2, city_2 in enumerate(chromosome):
                if index_2 not in [index_1, index_1 + 1, index_1 - 1, len(chromosome) - 1] and index_1 is not len(
                        chromosome) - 1:
                    first_distance = get_distance_between_two_cities(chromosome[index_1], chromosome[index_1 + 1])
                    second_distance = get_distance_between_two_cities(chromosome[index_2],
                                                                      chromosome[index_2 + 1])
                    third_distance = get_distance_between_two_cities(chromosome[index_1], chromosome[index_2])
                    fourth_distance = get_distance_between_two_cities(chromosome[index_1 + 1],
                                                                      chromosome[index_2 + 1])

                    if first_distance + second_distance > third_distance + fourth_distance:
                        chromosome[index_1 + 1], chromosome[index_2] = chromosome[index_2], chromosome[index_1 + 1]
                        draw_path([city.pos for city in chromosome])
                        improvement = True
                        break
                if improvement:
                    break


def evaluate():
    """
    Evaluate the population by calculating the distance total
    """

    for chromosome in populations:
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
    """
    Select the chromosomes that will survive to generate new chromosomes.
    """
    global best_chromosome, survivors, end, counter_iteration_before_two_opt

    # Sort the actual population by its fitness
    populations.sort(key=lambda x: x.fitness)

    # If there was no best_chromosome, than the best of the current population is saved.
    if best_chromosome is None:
        if not time_specified:
            end = datetime.datetime.now() + datetime.timedelta(seconds=max_time_if_algorithm_stagnant)
        best_chromosome = deepcopy(populations[0])
        if args.nogui is False:
            draw_path([city.pos for city in best_chromosome.list_cities])
    else:
        # If the best fitness of the current population is better than the current stored, then an update is done.
        if populations[0].fitness < best_chromosome.fitness:
            if not time_specified:
                end = datetime.datetime.now() + datetime.timedelta(seconds=max_time_if_algorithm_stagnant)
            best_chromosome = deepcopy(populations[0])
            if args.nogui is False:
                draw_path([city.pos for city in best_chromosome.list_cities])
            counter_iteration_before_two_opt = 0
        else:
            counter_iteration_before_two_opt += 1

    # Select the firsts survivors
    survivors = populations[:number_of_elites]
    # Add the best chromosome to the survivors
    survivors.append(best_chromosome)
    # Fill the population with unique random chromosomes
    random_population_index = random.sample(range(len(survivors), int(population_size / 2)),
                                            int(population_size / 2) - len(survivors))
    for i in random_population_index:
        survivors.append(populations[i])


def crossing():
    """
    Cross each chromosome with another random chromosome. If there is duplicates values in the new chromosomes,
    a swap between the duplicates values of each chromosome is performed.
    """
    global populations
    cutting_point = int(len(list_cities) * cross_over_rate)
    # empty the old population to welcome the new one
    populations[:] = []

    # Feel populations with new chromosomes
    for i in range(int(population_size / 2)):
        choice = random.randint(0, len(survivors) - 1)
        # Generate the four slices to crossover
        first_slice_1 = survivors[i].list_cities[:cutting_point]
        second_slice_1 = survivors[choice].list_cities[cutting_point:]
        first_slice_2 = survivors[i].list_cities[cutting_point:]
        second_slice_2 = survivors[choice].list_cities[:cutting_point]

        # Generate two chromosome with two slices
        chromosome_prototype_1 = first_slice_1 + second_slice_1
        chromosome_prototype_2 = first_slice_2 + second_slice_2

        # Check duplicates values in the first new chromosome
        duplicates_value = []
        for index in first_slice_1:
            for iteration in second_slice_1:
                if index.name == iteration.name:
                    duplicates_value.append(index)

        # Check duplicates values in the second new chromosome
        duplicates_value_to_exchange = []
        for index in first_slice_2:
            for iteration in second_slice_2:
                if index.name == iteration.name:
                    duplicates_value_to_exchange.append(index)

        # Swap duplicates values
        for index, duplicate_value in enumerate(duplicates_value):
            index_1 = chromosome_prototype_1.index(duplicate_value)
            index_2 = chromosome_prototype_2.index(duplicates_value_to_exchange[index])
            chromosome_prototype_1[index_1], chromosome_prototype_2[index_2] = chromosome_prototype_2[index_2], \
                                                                               chromosome_prototype_1[index_1]

        # Add the new chromosomes to the population
        populations.append(Chromosome(chromosome_prototype_1))
        populations.append(Chromosome(chromosome_prototype_2))


def mutate():
    """
    Mutate one chromosome by swaping two cities.
    """
    for chromosome in populations:
        for index in range(len(list_cities)):
            if round(random.uniform(0, 1), 2) <= mutation_rate / 2:
                random_position = random.randint(0, len(list_cities) - 1)
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

    print(best_chromosome.fitness, end=" ")
    for city in best_chromosome.list_cities:
        print(city.name, end=" ")

    return best_chromosome


class City(object):
    """
    Store the name of the city and it's position
    """

    def __init__(self, pos, name=None):
        self.name = name
        self.pos = pos


class Chromosome(object):
    """
    Store a path that passes through all cities and store the total distance of the course as it's fitness.
    """

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
