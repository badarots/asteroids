import math
import random
import pyglet
from . import resources
from .utils import distance, cycle
from pyglet.window import key

window_size = [640, 480]

# classe base dos objetos do jogo
class PhysicalObject(pyglet.sprite.Sprite):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.velocity_x, self.velocity_y = 0.0, 0.0
        self.dead = False
        self.new_objects = []
        self.is_bullet = False
        self.reacts_to_bullets = True
        self.event_handlers = []

    def __repr__(self):
        return "<Objeto Base>"

    def update(self, dt):
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.check_bounds()    

    # checa se o objeto saiu da tela e atualiza ciclicamente sua posicao
    def check_bounds(self):
        min_x = -self.width / 2 + 10
        min_y = -self.height / 2 + 10
        max_x = window_size[0] + self.width / 2 - 10
        max_y = window_size[1] + self.height / 2 -10
        self.x = cycle(self.x, max_x, min_x)
        self.y = cycle(self.y, max_y, min_y)

    # checa se houve colisao com o `other_object`
    # apenas ha colisoes dos asterois com a nave e os tiros
    # outros tipos de colicoes sao ignoradas
    def collides_with(self, other_object):
        if not self.reacts_to_bullets and other_object.is_bullet:
            return False
        if self.is_bullet and not other_object.reacts_to_bullets:
            return False
        collision_distance = self.width/2 + other_object.width/2
        actual_distance = distance(self.position, other_object.position)
        return (actual_distance <= collision_distance)

    # lida com a colisao
    def handle_collision_with(self, other_object):
        if other_object.__class__ != self.__class__:
            self.dead = True
   

# os tiros tbm sao objetos, olha so
class Bullet(PhysicalObject):

    def __init__(self, *args, **kwargs):
        super(Bullet, self).__init__(resources.bullet_image, *args, **kwargs)
        pyglet.clock.schedule_once(self.die, 0.5)
        self.is_bullet = True
        self.reacts_to_bullets = False

    def __repr__(self):
        return "<Bullet>"
    
    def die(self, dt):
        self.dead = True


# esse aqui eh a nave do jogador
class Player(PhysicalObject):

    def __init__(self, *args, **kwargs):
        super().__init__(img=resources.player_image, *args, **kwargs)
        self.thrust = 700.0 #300.0
        self.rotate_speed = 300.0 #200.0
        self.bullet_speed = 700.0
        self.reacts_to_bullets = False

        self.key_handler = key.KeyStateHandler()
        self.event_handlers = [self, self.key_handler]
        
        # adciona o foguinho
        self.engine_sprite = pyglet.sprite.Sprite(img=resources.engine_image,
                                                  *args, **kwargs)
        self.engine_sprite.visible = False

    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

    # aqui sao atualizadas a posicao da nave do foguinho
    # a velocidade tbm eh altera pelo arrasto e com a propulsao
    def update(self, dt):
        super(Player, self).update(dt)

        if self.key_handler[key.LEFT]:
            self.rotation -= self.rotate_speed * dt
        
        if self.key_handler[key.RIGHT]:
            self.rotation += self.rotate_speed * dt    
        
        if self.key_handler[key.UP]:
            angle_radians = math.radians(self.rotation)
            force_x = math.sin(angle_radians) * self.thrust
            force_y = math.cos(angle_radians) * self.thrust
            self.velocity_x += force_x * dt
            self.velocity_y += force_y * dt
            self.engine_sprite.rotation = self.rotation
            self.engine_sprite.x = self.x
            self.engine_sprite.y = self.y
            self.engine_sprite.visible = True
        
        else:
            self.engine_sprite.visible = False
        
        # adcionado um arrasto proporcional a velocidade
        # o bom eh que isso sozinho limita a velocidade da nave
        self.velocity_x -= self.velocity_x * 5e-1* dt
        self.velocity_y -= self.velocity_y * 5e-1* dt

        
    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.fire()
        
    # ATIRA! cria um tiro
    def fire(self):
        angle_radians = math.radians(self.rotation)
        ship_radius = self.width/2
        bullet_x = self.x + math.sin(angle_radians) * ship_radius
        bullet_y = self.y + math.cos(angle_radians) * ship_radius
        new_bullet = Bullet(bullet_x, bullet_y, batch=self.batch)

        bullet_vx = (
            self.velocity_x + math.sin(angle_radians) * self.bullet_speed
        )
        bullet_vy = (
            self.velocity_y + math.cos(angle_radians) * self.bullet_speed
        )
        new_bullet.velocity_x = bullet_vx
        new_bullet.velocity_y = bullet_vy
        new_bullet.rotation = self.rotation

        self.new_objects.append(new_bullet)

    def delete(self):
        # We have a child sprite which must be deleted when this object
        # is deleted from batches, etc.
        self.engine_sprite.delete()
        super(Player, self).delete()
    

# classe dos asteroids
class Asteroid(PhysicalObject):
    """An asteroid that divides a little before it dies"""

    def __init__(self, *args, **kwargs):
        super(Asteroid, self).__init__(resources.asteroid_image, *args, **kwargs)

        # Slowly rotate the asteroid as it moves
        self.rotate_speed = random.random() * 100.0 - 50.0
        self.points = 2

    def __repr__(self):
        return "<Asteroid size {}>".format(self.scale)

    def update(self, dt):
        super(Asteroid, self).update(dt)
        self.rotation += self.rotate_speed * dt

    def handle_collision_with(self, other_object):
        super(Asteroid, self).handle_collision_with(other_object)

        # gera outros asteroides menores numa colisao, para quando chega a 
        # 1/4 do tamanho original
        if self.dead and self.scale > 0.25:
            num_asteroids = random.randint(2, 3)
            for _ in range(num_asteroids):
                new_asteroid = Asteroid(x=self.x, y=self.y, batch=self.batch)
                new_asteroid.rotation = random.randint(0, 360)
                new_asteroid.velocity_x = (random.random()*2-1) * 70 + self.velocity_x
                new_asteroid.velocity_y = (random.random()*2-1)* 70 + self.velocity_y
                new_asteroid.scale = self.scale * 0.5
                new_asteroid.points = 5 if self.scale == 1 else 10
                self.new_objects.append(new_asteroid)
