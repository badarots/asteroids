import pyglet
from pyglet.window import key
from game import resources, load, game_objects
from random import randint
from math import log

# Configuracoes do jogo
n_asteroids = 6 
max_lives = lives = 3

# Configuracao da janela
width = 800
height = 600
font_name = 'Noto Sans Mono'
info_height = height - 20
player_position = (width//2, height//2)

game_objects.window_size = [width, height]

window = pyglet.window.Window(width, height)
main_batch = pyglet.graphics.Batch()

# variaveis globais
score = 0
level = 1
objects = []
event_stack_size = 0
player_ship = None
player_lives = []

score_label = pyglet.text.Label(text="Nvl: 0 Pontos: 0", font_name=font_name,
                                x=10, y=info_height, batch=main_batch)
level_label = pyglet.text.Label(text="Asteroids", font_name=font_name,
                                x=window.width//2, y=info_height,
                                anchor_x='center', batch=main_batch)
info_label = pyglet.text.Label(text="", font_name=font_name,
                                font_size=36,
                                x=window.width//2, y=window.height//2,
                                anchor_x='center', batch=main_batch)                             


class ContinueGame():
    def on_key_press(self, symbol, modifiers):
        if symbol != key.SPACE:
            return
        
        # if info_label.text == "Aperte ESPAÇO":
        if len(player_lives) > 0:
            continue_game(lives)
        else:
            init()

menu_handler = ContinueGame()

# inicia o jogo
def init():
    global objects, score, lives, player_lives, level

    score = 0
    level = 1
    lives = max_lives
   
    asteroids = load.asteroids(n_asteroids, player_position, 
                               window.width, window.height, main_batch)
    player_lives = load.player_lives(lives, width, height, main_batch)

    objects = asteroids
    menu()

# "menu" do jogo. acessado no inicio e quando o jogador morre
def menu(dead=False):
    global lives, event_stack_size, player_lives

    while event_stack_size > 0:
        window.pop_handlers()
        event_stack_size -= 1

    if dead:
        lives -= 1
    if lives > 0:
        info_label.text = "Aperte ESPAÇO"
    else:
        info_label.text = "Pontuação: {}".format(score)

    window.push_handlers(menu_handler)
    event_stack_size += 1

# adciona o jogador a tela
def continue_game(lives):
    global event_stack_size, player_ship

    while event_stack_size > 0:
        window.pop_handlers()
        event_stack_size -= 1
    
    player_lives.pop()
    info_label.text = ""

    player_ship = game_objects.Player(x=player_position[0], y=player_position[1],
                                      batch=main_batch)
    player_ship.scale = 0.75   
    objects.append(player_ship)

    for obj in objects:
        for handler in obj.event_handlers:
            window.push_handlers(handler)
            event_stack_size += 1

# aqui que a magica acontece
def update(dt):
    global score, level
    # checa por colisoes
    for i in range(len(objects)):
        for j in range(i+1, len(objects)):
            obj_1 = objects[i]
            obj_2 = objects[j]
            if not obj_1.dead and not obj_2.dead:
                if obj_1.collides_with(obj_2):
                    p1 = obj_1.handle_collision_with(obj_2)
                    p2 = obj_2.handle_collision_with(obj_1)

    to_add = []
    asteroids_count = 0
    player_dead = False
    points = 0
    
    # adciona novos objetos ao jogo (tiros e asteroids)
    for obj in objects:
        obj.update(dt)
        to_add.extend(obj.new_objects)
        obj.new_objects = []

        if isinstance(obj, game_objects.Asteroid):
            asteroids_count += 1
    
    # remove objetos mortos
    for to_remove in [obj for obj in objects if obj.dead]:
        if isinstance(to_remove, game_objects.Player):
            player_dead = True
        if isinstance(to_remove, game_objects.Asteroid):
            points += to_remove.points
        
        to_add.extend(obj.new_objects)
        to_remove.delete()
        objects.remove(to_remove)

    objects.extend(to_add)

    # atuliza o estado do jogo
    if points > 0 and not player_dead:
        score += points
        score_label.text = "Nvl: {} Pontos {}".format(level, score)
    if player_dead:
        menu(dead=True)
    elif asteroids_count == 0:
        level += 1
        score_label.text = "Nvl: {} Pontos: {}".format(level, score)
        asteroids = load.asteroids(n_asteroids + int(2*log(level, 2)), 
                                   player_ship.position, 
                                   window.width, window.height, main_batch)
        objects.extend(asteroids)


@window.event
def on_draw():
    window.clear()
    # desenha todos os objetos
    main_batch.draw()


if __name__ == "__main__":
    init()
    pyglet.clock.schedule_interval(update, 1/120.0)
    pyglet.app.run()
