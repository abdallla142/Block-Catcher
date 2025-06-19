import pygame
import random
import sys

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 800, 900
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch Blocks Ultimate")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (30, 144, 255)
RED = (255, 80, 80)
GREEN = (80, 255, 80)
YELLOW = (255, 255, 80)
CYAN = (80, 255, 255)
PURPLE = (180, 100, 255)
DARK_BLUE = (15, 60, 120)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)

FONT = pygame.font.SysFont("Arial", 24)
BIG_FONT = pygame.font.SysFont("Arial", 64, bold=True)

clock = pygame.time.Clock()
FPS = 60

START, PLAYING, GAME_OVER, SHOP, LEVEL_UP, DIFFICULTY_SELECT, INFO = range(7)

player = pygame.Rect(WIDTH//2 - 50, HEIGHT - 60, 100, 20)
player_speed = 10

block_size = 45
blocks = []

score = 0
lives = 3
level = 1
coins = 0
block_speed = 4
game_state = DIFFICULTY_SELECT
shield = False
slow_motion = False
slow_timer = 0
level_up_time = 0
turrets = []
difficulty = 'medium'

shield_level = 0
slow_duration = 5000
turret_count = 0

shield_cost = 50
slow_cost = 75
turret_cost = 100

def create_block():
    types = ['red', 'green', 'yellow', 'cyan', 'purple']
    color = random.choice(types)
    x = random.randint(0, WIDTH - block_size)
    y = -block_size
    return {"rect": pygame.Rect(x, y, block_size, block_size), "type": color}

def draw_centered_text(lines, y_start, color=WHITE):
    for i, line in enumerate(lines):
        surf = FONT.render(line, True, color)
        rect = surf.get_rect(center=(WIDTH//2, y_start + i * 40))
        SCREEN.blit(surf, rect)

def draw_info_screen():
    SCREEN.fill(BLACK)
    lines = [
        "HOW TO PLAY",
        "← → to move. Catch falling blocks!",
        "Red: +10 pts  |  Green: +20 pts",
        "Yellow: +1 life | Cyan: Shield",
        "Purple: Slow motion",
        "",
        "Coins are used to buy power-ups in the shop.",
        "Press ESC to return."
    ]
    draw_centered_text(lines, 180)
    pygame.display.flip()

def draw_shop_screen():
    SCREEN.fill((10, 10, 30))
    SCREEN.blit(BIG_FONT.render("SHOP", True, YELLOW), (WIDTH//2 - 100, 80))
    items = [
        f"1. Shield Upgrade ({shield_cost} coins)",
        f"2. Slow Motion Upgrade ({slow_cost} coins)",
        f"3. Add Turret ({turret_cost} coins)",
        "Press SPACE to continue"
    ]
    for i, item in enumerate(items):
        SCREEN.blit(FONT.render(item, True, WHITE), (180, 200 + i * 60))
    SCREEN.blit(FONT.render(f"Your coins: {coins}", True, GREEN), (280, 450))
    pygame.display.flip()

def draw_player():
    pygame.draw.rect(SCREEN, BLUE, player, border_radius=12)
    if shield:
        pygame.draw.circle(SCREEN, CYAN, player.center, 60, width=3)

def draw_blocks():
    for b in blocks:
        color_map = {"red": RED, "green": GREEN, "yellow": YELLOW, "cyan": CYAN, "purple": PURPLE}
        pygame.draw.rect(SCREEN, color_map[b["type"]], b["rect"], border_radius=10)
        SCREEN.blit(FONT.render(b["type"][0].upper(), True, BLACK), (b["rect"].x+15, b["rect"].y+10))

def fire_turrets():
    for turret in turrets:
        pygame.draw.rect(SCREEN, ORANGE, turret, border_radius=5)
        for b in blocks[:]:
            if abs(turret.centerx - b["rect"].centerx) < 20:
                pygame.draw.line(SCREEN, RED, turret.midtop, b["rect"].center, 2)
                blocks.remove(b)
                break

def draw_hud():
    SCREEN.blit(FONT.render(f"Score: {score}", True, WHITE), (10, 10))
    SCREEN.blit(FONT.render(f"Lives: {lives}", True, WHITE), (10, 40))
    SCREEN.blit(FONT.render(f"Level: {level}", True, WHITE), (10, 70))
    SCREEN.blit(FONT.render(f"Coins: {coins}", True, YELLOW), (10, 100))

stars = [{"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT), "speed": random.randint(1, 3)} for _ in range(100)]

def draw_animated_background():
    SCREEN.fill((5, 5, 20))
    for star in stars:
        pygame.draw.circle(SCREEN, WHITE, (star["x"], star["y"]), 2)
        star["y"] += star["speed"]
        if star["y"] > HEIGHT:
            star["y"] = 0
            star["x"] = random.randint(0, WIDTH)

def main():
    global score, lives, level, block_speed, shield, slow_motion, slow_timer
    global game_state, blocks, level_up_time, coins, difficulty
    global shield_cost, slow_cost, turret_cost, shield_level, slow_duration, turrets
    global player

    running = True
    spawn_timer = 0

    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == DIFFICULTY_SELECT and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    difficulty = 'easy'; block_speed = 3; game_state = START
                elif event.key == pygame.K_2:
                    difficulty = 'medium'; block_speed = 5; game_state = START
                elif event.key == pygame.K_3:
                    difficulty = 'hard'; block_speed = 7; game_state = START

            if game_state == START and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    score = 0; lives = 3; level = 1; coins = 0
                    blocks.clear(); turrets.clear()
                    shield = False; slow_motion = False
                    game_state = PLAYING
                elif event.key == pygame.K_i:
                    game_state = INFO
                elif event.key == pygame.K_c:
                    # CRAZY MODE: max powerups, lives, turrets
                    score = 0; lives = 99; level = 99; coins = 9999
                    blocks.clear()
                    shield = True
                    slow_motion = True
                    turrets.clear()
                    turrets.extend([pygame.Rect(x, HEIGHT - 120, 20, 40) for x in range(100, WIDTH, 150)])
                    game_state = PLAYING

            if game_state == INFO and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = START

            if game_state == SHOP and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and coins >= shield_cost:
                    coins -= shield_cost
                    shield_level += 1
                    shield_cost += 25
                elif event.key == pygame.K_2 and coins >= slow_cost:
                    coins -= slow_cost
                    slow_duration += 1000
                    slow_cost += 25
                elif event.key == pygame.K_3 and coins >= turret_cost:
                    coins -= turret_cost
                    turrets.append(pygame.Rect(100 + len(turrets)*150, HEIGHT - 120, 20, 40))
                    turret_cost += 50
                elif event.key == pygame.K_SPACE:
                    game_state = PLAYING

        if game_state == DIFFICULTY_SELECT:
            SCREEN.fill(BLACK)
            draw_centered_text([
                "Select Difficulty",
                "1. Easy     2. Medium     3. Hard"
            ], 300)
            pygame.display.flip()
            continue

        if game_state == START:
            SCREEN.fill(DARK_BLUE)
            draw_centered_text([
                "Catch Blocks ULTIMATE",
                "",
                "SPACE: Start Game",
                "I: Info / How to Play",
                "C: Crazy Mode (All Power-ups!)"
            ], 300)
            pygame.display.flip()

        elif game_state == INFO:
            draw_info_screen()

        elif game_state == SHOP:
            draw_shop_screen()

        elif game_state == PLAYING:
            if keys[pygame.K_LEFT]: player.x -= player_speed
            if keys[pygame.K_RIGHT]: player.x += player_speed
            player.x = max(0, min(WIDTH - player.width, player.x))

            spawn_timer += 1
            if spawn_timer >= max(20, 60 - level * 2):
                blocks.append(create_block())
                spawn_timer = 0

            speed = block_speed // 2 if slow_motion else block_speed

            for b in blocks[:]:
                b["rect"].y += speed
                if b["rect"].colliderect(player):
                    if b["type"] == "red": score += 10; coins += 5
                    elif b["type"] == "green": score += 20; coins += 10
                    elif b["type"] == "yellow": lives += 1
                    elif b["type"] == "cyan": shield = True
                    elif b["type"] == "purple":
                        slow_motion = True
                        slow_timer = pygame.time.get_ticks()
                    blocks.remove(b)
                elif b["rect"].top > HEIGHT:
                    blocks.remove(b)
                    if not shield:
                        lives -= 1
                    else:
                        shield = False

            if slow_motion and pygame.time.get_ticks() - slow_timer > slow_duration:
                slow_motion = False

            if score // 100 + 1 > level:
                level += 1
                block_speed += 1
                game_state = SHOP

            if lives <= 0:
                game_state = GAME_OVER

            draw_animated_background()
            draw_player()
            draw_blocks()
            fire_turrets()
            draw_hud()
            pygame.display.flip()

        elif game_state == GAME_OVER:
            SCREEN.fill(BLACK)
            draw_centered_text([
                "GAME OVER",
                f"Final Score: {score}",
                "Press ESC to Quit"
            ], 320, RED)
            pygame.display.flip()
            if keys[pygame.K_ESCAPE]:
                running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
