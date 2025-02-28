
# Copyright (c) 2025 Korde Warnsley. All rights reserved.
# This code is licensed under Apache License.



####################################################################
import pygame, random, math

pygame.init()

pygame.mixer.init()

pygame.mixer.music.load("backgroundmusic.mp3")
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(loops=-30, start=0.0)

gem_pickup_sound = pygame.mixer.Sound("coinsound.mp3") 
gem_pickup_sound.set_volume(0.1)

WIDTH, HEIGHT = 2500, 1300        #1500, 1000 
SCREEN_RES = (WIDTH, HEIGHT)
RED, GREEN, BLUE, GREY, YELLOW, WHITE, BLACK = (255, 0, 0), (20, 100, 20), (0, 0, 255), (77, 77, 77), (255, 255, 0), (255, 255, 255), (0, 0, 0)

screen = pygame.display.set_mode(SCREEN_RES)
pygame.display.set_caption("Sunset Chronicles")
clock = pygame.time.Clock()

ball_image = pygame.image.load('dvd.png')
background_images = ['Background.png', 'Background2.png', 'Background3.png']
cookie_background = pygame.image.load('cookie.png')
background_image = pygame.image.load(random.choice(background_images))
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
ball_rect = ball_image.get_rect(center=(100, 100))
move_speed = 13
keys = {'w': False, 'a': False, 's': False, 'd': False}

player_health, score, round_number = 100, 0, 1   ######################

is_paused = False

safe_zone = pygame.Rect(0, 0, 150, 150)

class BadGuy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('badguy.png')
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect(center=(x, y))
        self.dead = False
        self.explosion_timer = 1
        self.speed = 3

    def update(self, target_rect, obstacles):
        if self.dead: 
            return

        dx, dy = target_rect.centerx - self.rect.centerx, target_rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        dx, dy = dx / distance, dy / distance if distance != 0 else (0, 0)

        new_rect = self.rect.copy()
        new_rect.x += dx * self.speed
        new_rect.y += dy * self.speed

        for obstacle in obstacles:
            if new_rect.colliderect(obstacle.rect):
                self.avoid_obstacle(obstacle)

        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

    def avoid_obstacle(self, obstacle):
        if isinstance(obstacle, Obstacle):
            if self.rect.colliderect(obstacle.rect):
                if self.rect.centerx < obstacle.rect.centerx:
                    self.rect.x -= 5
                elif self.rect.centerx > obstacle.rect.centerx:
                    self.rect.x += 5
                if self.rect.centery < obstacle.rect.centery:
                    self.rect.y -= 5
                elif self.rect.centery > obstacle.rect.centery:
                    self.rect.y += 5

    def explode(self):
        self.dead = True
        self.explosion_timer = 40

    def draw_explosion(self, surface):
        if self.explosion_timer > 0:
            pygame.draw.circle(surface, YELLOW, self.rect.center, 10 + (30 - self.explosion_timer), 0)
            self.explosion_timer -= 1
        elif self.explosion_timer <= 0:
            self.kill()

class Gem(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        gem_images = ['bluegem.png', 'redgem.png', 'greengem.png', 'purplegem.png', 'yellowgem.png', 'orangegem.png', 'cyangem.png', 'pinkgem.png']
        selected_image = random.choice(gem_images)
        self.image = pygame.image.load(selected_image)
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect(center=(x, y))

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, shape="rect"):
        super().__init__()
        self.shape = shape
        if self.shape == "circle":
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.circle(self.image, YELLOW, (width // 2, height // 2), min(width, height) // 2)
        else:
            self.image = pygame.Surface((width, height))
            self.image.fill(YELLOW)

        self.rect = self.image.get_rect(topleft=(x, y))

def reset_game(round_num):
    global score, bad_guys, gems, obstacles, background_image
    score = 0
    bad_guys, gems, obstacles = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()

    # Cookie
    if round_num >= 10 and round_num < 11:
        background_image = pygame.transform.scale(cookie_background, (WIDTH, HEIGHT))
    else:
        background_image = pygame.image.load(random.choice(background_images))
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

    for _ in range(round_num * 5):  # Add bad guys
        while True:
            x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
            if not safe_zone.collidepoint(x, y):
                bad_guys.add(BadGuy(x, y))
                break

    for _ in range(5 + round_num):  # Add gems
        while True:
            x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
            if not safe_zone.collidepoint(x, y):
                gems.add(Gem(x, y))
                break

    for _ in range(round_num * 8):  # Add obstacles
        width, height = random.randint(20, 50), random.randint(50, 50)
        shape = random.choice(["rect", "circle"])
        while True:
            x, y = random.randint(0, WIDTH - width), random.randint(0, HEIGHT - height)
            if not safe_zone.colliderect(pygame.Rect(x, y, width, height)):
                obstacles.add(Obstacle(x, y, width, height, shape))
                break

reset_game(round_number)

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                is_paused = not is_paused

            if event.key == pygame.K_w:
                keys['w'] = True
            if event.key == pygame.K_a:
                keys['a'] = True
            if event.key == pygame.K_s:
                keys['s'] = True
            if event.key == pygame.K_d:
                keys['d'] = True
            if event.key == pygame.K_r:
                if player_health <= 0:
                    reset_game(round_number)
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                keys['w'] = False
            if event.key == pygame.K_a:
                keys['a'] = False
            if event.key == pygame.K_s:
                keys['s'] = False
            if event.key == pygame.K_d:
                keys['d'] = False

    if is_paused:
        font = pygame.font.SysFont('Arial', 80)
        screen.blit(font.render("PAUSED", True, WHITE), (WIDTH // 2 - 150, HEIGHT // 2))
        pygame.display.flip()
        continue

    if keys['w'] and ball_rect.top > 0:
        ball_rect.y -= move_speed
    if keys['a'] and ball_rect.left > 0:
        ball_rect.x -= move_speed
    if keys['s'] and ball_rect.bottom < HEIGHT:
        ball_rect.y += move_speed
    if keys['d'] and ball_rect.right < WIDTH:
        ball_rect.x += move_speed

    for obstacle in obstacles:
        if ball_rect.colliderect(obstacle.rect):
            if keys['w']: ball_rect.y += move_speed
            if keys['a']: ball_rect.x += move_speed
            if keys['s']: ball_rect.y -= move_speed
            if keys['d']: ball_rect.x -= move_speed

    # Draw the background
    screen.blit(background_image, (0, 0))

    # Draw the safe zone
    pygame.draw.rect(screen, (0, 255, 0), safe_zone)

    # Update bad guys
    bad_guys.update(ball_rect, obstacles)

    to_remove_bad_guys = []
    for bad_guy in bad_guys:
        if bad_guy.dead:
            continue
        if ball_rect.colliderect(bad_guy.rect):
            player_health -= 3
            bad_guy.explode()
            to_remove_bad_guys.append(bad_guy)
            score += 50
    for bad_guy in to_remove_bad_guys:
        if bad_guy.dead and bad_guy.explosion_timer <= 0:
            bad_guys.remove(bad_guy)

    # Draw the bad guys
    for bad_guy in bad_guys:
        if bad_guy.dead:
            bad_guy.draw_explosion(screen)
        else:
            screen.blit(bad_guy.image, bad_guy.rect)

    # Draw the gems
    for gem in gems:
        screen.blit(gem.image, gem.rect)

    to_remove_gems = []
    for gem in gems:
        if ball_rect.colliderect(gem.rect):
            to_remove_gems.append(gem)
            score += 20
            gem_pickup_sound.play()

    for gem in to_remove_gems:
        gems.remove(gem)

    # Draw obstacles
    for obstacle in obstacles:
        screen.blit(obstacle.image, obstacle.rect)

    # Check for game over
    if player_health <= 0:
        font = pygame.font.SysFont('Arial', 80)
        screen.blit(font.render("GAME OVER", True, RED), (WIDTH // 2 - 200, HEIGHT // 2))
        pygame.display.flip()
        continue
        
    if not gems:
        font = pygame.font.SysFont('Arial', 80)
        screen.blit(font.render(f"Round {round_number} Complete!", True, WHITE), (WIDTH // 2 - 300, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        round_number += 1                          ###############
        reset_game(round_number)

    colored_ball = ball_image.copy()
    screen.blit(colored_ball, ball_rect)

    # Draw health bar
    pygame.draw.rect(screen, RED, (50, 50, 400, 20))
    pygame.draw.rect(screen, GREEN, (50, 50, (player_health / 100) * 400, 20))

    # Display low health warning
    if player_health <= 20:
        font = pygame.font.SysFont('Arial', 50)
        if not is_paused:
            screen.blit(font.render("Warning! Low Health", True, RED), (WIDTH // 2 - 200, HEIGHT // 2))

    # Display score and round
    font = pygame.font.SysFont('Arial', 50)
    screen.blit(font.render(f"Gems: {score}", True, WHITE), (50, 100))
    screen.blit(font.render(f"Round: {round_number}", "/30" , True, RED), (50, 150))
    screen.blit(font.render(f"Reminder: Free cookie if you reach round 10 ", True, WHITE), (50, 200))
    screen.blit(font.render(f"Highest score: 22 ", True, BLACK), (50, 250))
    screen.blit(font.render(f"Pause: - (P) ", True, WHITE), (2200, 10))

    # Draw border
    pygame.draw.rect(screen, BLUE, (0, 0, WIDTH, HEIGHT), 10)

    pygame.display.flip()
    clock.tick(60)
