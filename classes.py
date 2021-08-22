import pygame
import os
import random
from functions import *


class Entity(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super(Entity, self).__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.left = pos[0]
        self.rect.top = pos[1]

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super(Player, self).__init__()
        self.sprites = []
        for img in os.listdir(resource_path('assets/entities/player')):
            self.sprites.append(pygame.image.load(resource_path(f'assets/entities/player/{img}')))
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def animate(self):
        self.current_sprite += 0.175
        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0
        self.image = self.sprites[int(self.current_sprite)]
        self.image = rescale(self.image, 50)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos):
        super(Explosion, self).__init__()
        self.sprites = []
        for img in os.listdir(resource_path('assets/entities/explosion')):
            self.sprites.append(pygame.image.load(resource_path(f'assets/entities/explosion/{img}')))
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.left = pos[0]
        self.rect.top = pos[1]

    def animate(self):
        self.current_sprite += 1
        if self.current_sprite >= len(self.sprites):
            self.kill()
            return
        self.image = self.sprites[int(self.current_sprite)]
        self.image = rescale(self.image, 50)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, name, position, bullet=None):
        super(Enemy, self).__init__()
        self.name = name
        folder = random.choice(os.listdir(resource_path('assets/entities/enemies')))
        img_list = os.listdir(resource_path(f'assets/entities/enemies/{folder}'))
        self.sprites = []
        for sprite in os.listdir(resource_path(f'assets/entities/enemies/{folder}')):
            self.sprites.append(pygame.image.load(resource_path(f'assets/entities/enemies/{folder}/{sprite}')))
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.image = rescale(self.image, 50)
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self.computation = self.rect.left
        self.could_attack = False
        self.active = True
        enemy_ball_img = pygame.image.load(resource_path('assets/projectiles/enemy_ball.png'))
        enemy_ball_img = rescale(enemy_ball_img, 9)
        self.bullet = Entity(enemy_ball_img, (self.rect.left+self.image.get_width()/2, self.rect.top+self.image.get_height()))

    def animate(self):
        self.current_sprite += 0.350
        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0
        self.image = self.sprites[int(self.current_sprite)]
        self.image = rescale(self.image, 50)

    def check_shoot(self, screen, group):
        check_bullet_position = (self.rect.left+self.image.get_width()/2, self.rect.top+self.image.get_height()+10)
        check_bullet = Entity(pygame.image.load(resource_path('assets/projectiles/ball.png')), check_bullet_position)
        check_bullet.image.set_alpha(0)
        if self.active:
            screen.blit(check_bullet.image, check_bullet.rect.topleft)
        if pygame.sprite.spritecollideany(check_bullet, group):
            self.active = False
        else:
            self.could_attack = True

    def hide_bullet(self):
        self.bullet.image.set_alpha(0)

    def show_bullet(self):
        self.bullet.image.set_alpha(255)


class Text():
    def __init__(self, font_file, pos, text, color, font_size=32):
        self.font = pygame.font.Font(font_file, font_size)
        self.color = color
        self.raw_text = text
        self.text = self.font.render(text, False, color)
        self.rect = self.text.get_rect()
        self.rect.left = pos[0]
        self.rect.top = pos[1]

    def reposition(self, x, y):
        self.rect.left = x
        self.rect.top = y

    def size(self, arg='xy'):
        size = self.font.size(self.raw_text)
        if arg == 'x':
            return size[0]
        elif arg == 'y':
            return size[1]
        else:
            return self.font.size(self.raw_text)


class Sound():
    def __init__(self, path):
        self.file = pygame.mixer.Sound(path)

    def set_volume(self, volume):
        self.file.set_volume(volume)

    def play(self, repeats=0):
        self.file.play(loops=repeats)
