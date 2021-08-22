import pygame
from classes import *
from functions import *
import sys
import random
from math import floor


# Game setup
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((600, 900))
pygame.display.set_caption('Space Invaders')
icon = pygame.image.load(resource_path('assets/icons/icon.png'))
pygame.display.set_icon(icon)
music = Sound('assets/sounds/music.mp3')
music.set_volume(0.7)
music.play(-1)

# General stats
ball_speed = 9
enemy_shooting_delay = 200
enemyx_speed = 3 # Bigger = slower
player_speed = 5
score = 0


def main():
    global ball_speed, enemy_shooting_delay, player_speed, score, enemyx_speed
    # Game state
    state = 2
    font = resource_path('assets/general/font.ttf')
    bg_image = pygame.image.load(resource_path('assets/general/bg.png'))
    WHITE = (255, 255, 255)
    you_lost_text = Text(font, (screen.get_width()/2, screen.get_height()/2), 'You Lost', WHITE)
    you_lost_text.reposition(you_lost_text.rect.left-you_lost_text.size('x')/2, you_lost_text.rect.top-you_lost_text.size('y')/2)
    restart_text = Text(font, (0, 0), 'Press Enter to Restart', WHITE, 16)
    restart_text.reposition(you_lost_text.rect.left-restart_text.size('x')/8, you_lost_text.rect.top+100)
    pause_text = Text(font, (screen.get_width()/2, screen.get_height()/2), 'Paused', WHITE)
    pause_text.reposition(pause_text.rect.left-pause_text.size('x')/2, pause_text.rect.top-pause_text.size('y')/2)
    # Score
    score_text = Text(font, (5, screen.get_height()), str(score), (255, 255, 255))
    score_text.reposition(5, screen.get_height()-score_text.font.get_height())

    # Sounds
    shoot_sound = Sound(resource_path('assets/sounds/shoot.wav'))
    shoot_sound.set_volume(0.3)
    kill_sound = Sound(resource_path('assets/sounds/invaderkilled.wav'))
    kill_sound.set_volume(0.3)
    player_hit_sound = Sound(resource_path('assets/sounds/playerhit.wav'))
    player_hit_sound.set_volume(0.3)
    pause_sound = Sound(resource_path('assets/sounds/pause.wav'))
    pause_sound.set_volume(0.3)
    resume_sound = Sound(resource_path('assets/sounds/resume.wav'))
    resume_sound.set_volume(0.3)
    lvlup_sound = Sound(resource_path('assets/sounds/lvlup.wav'))
    gameover_sound = Sound(resource_path('assets/sounds/gameover.wav'))
    gameover_sound.set_volume(0.3)

    # Player lives
    lives = 3
    heart_img = pygame.image.load(resource_path('assets/general/heart.png'))
    heart_img = rescale(heart_img, 30)
    heart = Entity(heart_img, (screen.get_width()-heart_img.get_width(), screen.get_height()-heart_img.get_height()))

    #   Player
    player_image = pygame.image.load(resource_path('assets/entities/player/player_01.gif'))
    player_x = screen.get_width()/2-player_image.get_width()/2
    player_y = (screen.get_height()*85)/100
    player_position = (player_x, player_y)
    player = Player(player_position)
    player_movementL, player_movementR = 0, 0

    # Borders
    border_image = pygame.image.load(resource_path('assets/general/border.png'))
    border_image = rescale(border_image, (1, screen.get_height()))
    border_L = Entity(border_image, (-1, 0))
    border_R = Entity(border_image, (screen.get_width()-border_image.get_width()+1, 0))

    #  Enemy
    len_enemies = 55
    enemies = pygame.sprite.Group()
    enemy_index, enemy_x, enemy_y, enemy_gap = 0, 20, 20, 50
    for i in range(len_enemies):
        enemies.add(Enemy(i, (enemy_x, enemy_y), screen))
        enemy_x += enemy_gap
        enemy_index += 1
        if enemy_index == 11:
            enemy_index = 0
            enemy_x = 20
            enemy_y += enemy_gap
    enemy_shooting_timer = 0
    enemy_possible_attackers = []
    shootcooldown = True
    enemy_dir = 55/(len_enemies*round(enemyx_speed))
    enemy_border_collisions = 0
    explosions = pygame.sprite.Group()

    # Shoot mechanic
    is_shooting = False
    while True:
        timer = pygame.time.get_ticks()
        dt = clock.tick()
        clock.tick(60)
        enemy_shooting_timer += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and state == 0:
                    main()
                if event.key == pygame.K_ESCAPE and state == 2:
                    pygame.mixer.pause()
                    pause_sound.play()
                    state = 1
                elif event.key == pygame.K_ESCAPE and state == 1:
                    pygame.mixer.unpause()
                    resume_sound.play()
                    state = 2
                if event.key == pygame.K_a:
                    player_movementL -= player_speed
                if event.key == pygame.K_d:
                    player_movementR += player_speed
                if event.key == pygame.K_SPACE and not(is_shooting):
                    shoot_sound.play()
                    ball_pos = [player.rect.left+player.image.get_width()/2, player.rect.top]
                    ball_img = pygame.image.load(resource_path('assets/projectiles/player_ball.png'))
                    ball_img = rescale(ball_img, 9)
                    ball = Entity(ball_img, ball_pos)
                    is_shooting = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    player_movementL = 0
                if event.key == pygame.K_d:
                    player_movementR = 0
        if state == 2:
            # Movement
            player.rect.left += player_movementR
            player.rect.left += player_movementL

            # Screen boundaries
            if player.rect.left >= screen.get_width()-player.image.get_width():
                player.rect.left = screen.get_width()-player.image.get_width()
            elif player.rect.left <= 0:
                player.rect.left = 0

            # Generate game background and entities
            screen.fill((0, 0, 0))
            screen.blit(bg_image, (0, 0))
            screen.blit(border_L.image, border_L.rect.topleft)
            screen.blit(border_R.image, border_R.rect.topleft)
            player.draw(screen)
            player.animate()
            enemies.draw(screen)
            for enemy in enemies:
                enemy.animate()
            # Enemies shooting mechanic
            if enemy_shooting_timer >= enemy_shooting_delay and shootcooldown:
                for enemy in enemies:
                    enemy.bullet.rect.left = enemy.rect.left
                shootcooldown = False
                for enemy in enemies:
                    enemy.check_shoot(screen, enemies)
                    if enemy.could_attack and len(enemy_possible_attackers) != 11:
                        enemy_possible_attackers.append(enemy)
                random_attack_num = 5
                if random_attack_num > len(enemy_possible_attackers):
                    random_attack_num = len(enemy_possible_attackers)
                try:
                    attackers_count = random.randrange(1, random_attack_num)
                except ValueError:
                    attackers_count = 1
                enemies_attacking = random.sample(enemy_possible_attackers, attackers_count)
                enemy_possible_attackers = []
            if enemy_shooting_timer >= enemy_shooting_delay:
                bullets = pygame.sprite.Group()
                for enemy in enemies_attacking:
                    if not(enemy.bullet.rect.top >= screen.get_height()) and not(pygame.sprite.collide_mask(enemy.bullet, player)):
                        bullets.add(enemy.bullet)
                        enemy.bullet.rect.top += ball_speed
                    if pygame.sprite.collide_mask(enemy.bullet, player):
                        player_hit_sound.play()
                        enemies_attacking.remove(enemy)
                        explosion = Explosion(player.rect.topleft)
                        explosions.add(explosion)
                        lives -= 1
                        enemy.bullet.rect.topleft = (enemy.rect.left+enemy.image.get_width()/2, enemy.rect.top+enemy.image.get_height())
                if len(bullets) == 0:
                    enemy_shooting_timer = 0
                    shootcooldown = True
                    enemy.bullet.rect.topleft = (enemy.rect.left+enemy.image.get_width()/2, enemy.rect.top+enemy.image.get_height())
                bullets.draw(screen)

            for enemy in enemies:
                enemy.computation += enemy_dir
                enemy.rect.left = floor(enemy.computation)
            if pygame.sprite.spritecollideany(border_L, enemies) or pygame.sprite.spritecollideany(border_R, enemies):
                enemy_dir *= -1
                enemy_border_collisions += 1
            if enemy_border_collisions == 2:
                for enemy in enemies:
                    enemy.rect.top += enemy_gap
                    enemy.bullet.rect.top += enemy_gap
                enemy_border_collisions = 0

            # Player shooting
            if is_shooting:
                ball.draw(screen)
                ball.rect.top -= ball_speed
                if ball.rect.top <= 0:
                    is_shooting = False
                    ball.rect.top = ball_pos[1]
                if pygame.sprite.spritecollideany(ball, enemies):
                    score += 100
                    kill_sound.play()
                    score_text.text = score_text.font.render(str(score), False, score_text.color)
                    collided = pygame.sprite.spritecollideany(ball, enemies)
                    explosion = Explosion((collided.rect.left-collided.image.get_width()/8, collided.rect.top-collided.image.get_height()/8))
                    explosions.add(explosion)
                    len_enemies -= 1
                    if len_enemies > 0:
                        enemy_dir = (enemy_dir/abs(enemy_dir))*(55/(len_enemies*round(enemyx_speed)))
                    else:
                        ball_speed += 1
                        enemy_shooting_delay -= 50
                        enemyx_speed -= 1
                        lvlup_sound.play()
                        main()
                    enemy = pygame.sprite.spritecollideany(ball, enemies)
                    enemy.kill()
                    collided.kill()
                    is_shooting = False
            for explosion in explosions:
                explosion.animate()
            explosions.draw(screen)

            # Score Text
            screen.blit(score_text.text, score_text.rect.topleft)

            # Player lives
            heart_displacement = 0
            for i in range(lives):
                screen.blit(heart_img, (heart.rect.left-heart_displacement-10, heart.rect.top-10))
                heart_displacement += heart_img.get_width()+5
            for enemy in enemies:
                if enemy.rect.top >= screen.get_height()-50:
                    gameover_sound.play()
                    state = 0
            if lives <= 0:
                gameover_sound.play()
                state = 0
            pygame.display.update()
            pygame.display.flip()
        elif state == 1:
            screen.fill((0, 0, 0))
            screen.blit(pause_text.text, pause_text.rect.topleft)
            pygame.display.update()
            pygame.display.flip()
        elif state == 0:
            screen.fill((0, 0, 0))
            screen.blit(you_lost_text.text, you_lost_text.rect.topleft)
            screen.blit(restart_text.text, restart_text.rect.topleft)
            score = 0
            pygame.display.update()
            pygame.display.flip()


if __name__ == "__main__":
    main()
