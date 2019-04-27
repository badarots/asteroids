import pyglet
import random
from . import resources, game_objects
from .utils import distance
from math import sqrt

# gera n asteroids em posicoes aleatorias mas afastados da jogador
def asteroids(num_asteroids, player_position, width, height, batch=None):
    asteroids = []
    for _ in range(num_asteroids):
        asteroid_x, asteroid_y = player_position
        while distance((asteroid_x, asteroid_y), player_position) < 100:
            asteroid_x = random.randint(0, width)
            asteroid_y = random.randint(0, height)
        new_asteroid = game_objects.Asteroid(x=asteroid_x, y=asteroid_y,
                                               batch=batch)
        new_asteroid.rotation = random.randint(0, 360)
        new_asteroid.velocity_x = (random.random() * 2 -1) * 40
        new_asteroid.velocity_y = (random.random() * 2 -1) * 40
        asteroids.append(new_asteroid)
    return asteroids

# gera a barra de vida
def player_lives(num_icons, width, height, batch=None):
    player_lives = []
    for i in range(num_icons):
        new_sprite = pyglet.sprite.Sprite(img=resources.player_image,
                                        x=width-15-i*30, y=height-20,
                                        batch=batch)
        new_sprite.scale = 0.5 * 0.75
        player_lives.append(new_sprite)
    return player_lives                                    
