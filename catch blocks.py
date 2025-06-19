import pygame
import random
import sys
import math

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 600, 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch Blocks Game - Fun & Polished")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (30, 144, 255)
RED = (255, 80, 80)
GREEN = (80, 255, 80)
YELLOW = (255, 255, 80)
CYAN = (80, 255, 255)
PURPLE = (180, 100, 255)
DARK_BLUE = (15, 60, 120)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)

FONT = pygame.font.SysFont("Arial", 24)
BIG_FONT = pygame.font.SysFont("Arial", 64, bold=True)
MEDIUM_FONT = pygame.font.SysFont("Arial", 36, bold=True)

clock = pygame.time.Clock()
FPS = 60

player = pygame.Rect(WIDTH//2 - 50, HEIGHT - 60, 100, 20)
player_speed = 12

block_size = 45
blocks = []

score = 0
lives = 3
level = 1
block_speed = 4

shield = False
slow_motion = False
slow_motion_timer = 0

game_state = 0  # 0=START, 1=PLAYING, 2=GAME_OVER, 3=LEVEL_UP

level_up_time = 0
LEVEL_UP_DURATION = 180  # frames (~3 seconds)

score_pop_timer = 0
powerup_pop_timer = 0

def ease_out_quad(t):
    return 1 - (1 - t) * (1 - t)

def create_block():
    colors = [RED, GREEN, YELLOW, CYAN, PURPLE]
    color = random.choice(colors)
    x = random.randint(0, WIDTH - block_size)
    y = -block_size
    return {"rect": pygame.Rect(x, y, block_size, block_size), "color": color}

def draw_start_screen():
    SCREEN.fill(DARK_BLUE)
    title = BIG_FONT.render("Catch Blocks", True, WHITE)
    instruction = FONT.render("Press SPACE to start", True, LIGHT_GRAY)
    # Shadow text effect
    SCREEN.blit(title, title.get_rect(center=(WIDTH//2+4, HEIGHT//3+4)))
    SCREEN.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//3)))
    SCREEN.blit(instruction, instruction.get_rect(center=(WIDTH//2, HEIGHT//2)))
    pygame.display.flip()

def draw_game_over():
    SCREEN.fill(BLACK)
    over_text = BIG_FONT.render("GAME OVER", True, RED)
    score_text = FONT.render(f"Your Score: {score}", True, WHITE)
    restart_text = FONT.render("Press R to Restart or Q to Quit", True, WHITE)
    SCREEN.blit(over_text, over_text.get_rect(center=(WIDTH//2, HEIGHT//3)))
    SCREEN.blit(score_text, score_text.get_rect(center=(WIDTH//2, HEIGHT//2)))
    SCREEN.blit(restart_text, restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 60)))
    pygame.display.flip()

def draw_player():
    shadow_rect = player.copy()
    shadow_rect.y += 5
    pygame.draw.rect(SCREEN, BLACK, shadow_rect, border_radius=12)
    pygame.draw.rect(SCREEN, BLUE, player, border_radius=12)
    # Player highlight
    highlight = pygame.Rect(player.x, player.y, player.width, player.height//2)
    pygame.draw.rect(SCREEN, (120, 180, 255), highlight, border_radius=12)

    if shield:
        radius = max(player.width, player.height) // 2 + 15
        bubble_pos = (player.centerx, player.centery)
        # Pulsing alpha effect
        alpha = 120 + int(80 * math.sin(pygame.time.get_ticks() * 0.01))
        bubble_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(bubble_surf, (80, 255, 255, alpha), (radius, radius), radius, width=5)
        SCREEN.blit(bubble_surf, (bubble_pos[0] - radius, bubble_pos[1] - radius))

def draw_block(b):
    shadow = b["rect"].copy()
    shadow.x += 3
    shadow.y += 3
    pygame.draw.rect(SCREEN, BLACK, shadow, border_radius=10)
    pygame.draw.rect(SCREEN, b["color"], b["rect"], border_radius=10)
    # Glow effect
    glow_color = tuple(min(255, c + 70) for c in b["color"])
    glow_rect = b["rect"].inflate(12, 12)
    pygame.draw.rect(SCREEN, glow_color, glow_rect, width=4, border_radius=14)

def draw_labels(b):
    label = ""
    if b["color"] == RED:
        label = "+10"
    elif b["color"] == GREEN:
        label = "+20"
    elif b["color"] == YELLOW:
        label = "LIFE"
    elif b["color"] == CYAN:
        label = "SHIELD"
    elif b["color"] == PURPLE:
        label = "SLOW"

    if label:
        text_surface = FONT.render(label, True, BLACK)
        text_rect = text_surface.get_rect(center=b["rect"].center)
        SCREEN.blit(text_surface, text_rect)

def draw_background_gradient():
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(DARK_BLUE[0] * (1-ratio) + BLACK[0] * ratio)
        g = int(DARK_BLUE[1] * (1-ratio) + BLACK[1] * ratio)
        b = int(DARK_BLUE[2] * (1-ratio) + BLACK[2] * ratio)
        pygame.draw.line(SCREEN, (r, g, b), (0, y), (WIDTH, y))

def draw_hud():
    hud_rect = pygame.Rect(5, 5, 210, 130)
    pygame.draw.rect(SCREEN, (0,0,0,150), hud_rect)  # semi-transparent
    pygame.draw.rect(SCREEN, (40, 40, 60), hud_rect, border_radius=10)

    global score_pop_timer
    score_color = WHITE
    score_scale = 1.0
    if score_pop_timer > 0:
        progress = (30 - score_pop_timer) / 30
        score_scale = 1 + 0.3 * math.sin(progress * math.pi)
        score_pop_timer -= 1

    score_text = FONT.render(f"Score: {score}", True, score_color)
    score_surface = pygame.transform.smoothscale(score_text,
                    (int(score_text.get_width()*score_scale), int(score_text.get_height()*score_scale)))
    SCREEN.blit(score_surface, (15, 15))

    lives_text = FONT.render(f"Lives: {lives}", True, WHITE)
    SCREEN.blit(lives_text, (15, 50))

    level_text = FONT.render(f"Level: {level}", True, WHITE)
    SCREEN.blit(level_text, (15, 85))

    y_offset = 120
    if shield:
        shield_text = FONT.render("Shield ACTIVE", True, CYAN)
        SCREEN.blit(shield_text, (15, y_offset))
        y_offset += 30
    if slow_motion:
        slow_text = FONT.render("Slow Motion ON", True, PURPLE)
        SCREEN.blit(slow_text, (15, y_offset))
        y_offset += 30

def level_up_animation():
    global level_up_time
    SCREEN.fill(BLACK)
    t = level_up_time / LEVEL_UP_DURATION  # 0 to 1

    size = int(ease_out_quad(t) * 150)
    alpha = int(ease_out_quad(t) * 255)
    alpha = max(0, min(255, alpha))

    text = f"LEVEL {level}"
    text_surface = BIG_FONT.render(text, True, WHITE)
    # Scale text to max width 80% screen width
    max_width = WIDTH * 0.8
    scale_factor = min(1, max_width / text_surface.get_width())
    scaled_size = (int(text_surface.get_width() * scale_factor),
                   int(text_surface.get_height() * scale_factor))
    text_surface = pygame.transform.smoothscale(text_surface, scaled_size)
    text_surface.set_alpha(alpha)

    bounce_scale = 1 + 0.2 * math.sin(level_up_time * 0.15)
    bounce_size = (int(scaled_size[0] * bounce_scale), int(scaled_size[1] * bounce_scale))
    text_surface = pygame.transform.smoothscale(text_surface, bounce_size)

    rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
    SCREEN.blit(text_surface, rect)

    brightness = int(30 * (1 - t))
    flash_color = (brightness, brightness, brightness)
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(120)
    overlay.fill(flash_color)
    SCREEN.blit(overlay, (0, 0))

    pygame.display.flip()

    level_up_time += 1
    if level_up_time > LEVEL_UP_DURATION:
        return True
    return False

def main():
    global score, lives, level, block_speed, shield, slow_motion, slow_motion_timer, game_state, blocks, level_up_time, score_pop_timer, powerup_pop_timer

    running = True
    spawn_timer = 0

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == 0:  # Start
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    score = 0
                    lives = 3
                    level = 1
                    block_speed = 4
                    shield = False
                    slow_motion = False
                    slow_motion_timer = 0
                    blocks = []
                    game_state = 1

            elif game_state == 2:  # Game over
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game_state = 0
                    elif event.key == pygame.K_q:
                        running = False

        keys = pygame.key.get_pressed()
        if game_state == 1:  # Playing
            # Move player
            if keys[pygame.K_LEFT] and player.left > 0:
                player.x -= player_speed
            if keys[pygame.K_RIGHT] and player.right < WIDTH:
                player.x += player_speed

            spawn_timer += 1
            spawn_interval = max(10, 60 - level * 3)
            if spawn_timer >= spawn_interval:
                blocks.append(create_block())
                spawn_timer = 0

            speed = block_speed // 2 if slow_motion else block_speed
            for b in blocks[:]:
                b["rect"].y += speed

                if b["rect"].colliderect(player):
                    if b["color"] == RED:
                        score += 10
                        score_pop_timer = 30
                    elif b["color"] == GREEN:
                        score += 20
                        score_pop_timer = 30
                    elif b["color"] == YELLOW:
                        lives += 1
                        powerup_pop_timer = 30
                    elif b["color"] == CYAN:
                        shield = True
                        powerup_pop_timer = 30
                    elif b["color"] == PURPLE:
                        slow_motion = True
                        slow_motion_timer = pygame.time.get_ticks()
                        powerup_pop_timer = 30

                    blocks.remove(b)

            for b in blocks[:]:
                if b["rect"].top > HEIGHT:
                    blocks.remove(b)
                    if not shield:
                        lives -= 1
                    else:
                        shield = False

            if slow_motion:
                if pygame.time.get_ticks() - slow_motion_timer > 5000:
                    slow_motion = False

            new_level = score // 100 + 1
            if new_level > level:
                level = new_level
                block_speed = 4 + level
                level_up_time = 0
                game_state = 3  # Level up animation state

            if lives <= 0:
                game_state = 2  # Game over

            draw_background_gradient()
            draw_player()
            for b in blocks:
                draw_block(b)
                draw_labels(b)
            draw_hud()

            pygame.display.flip()

        elif game_state == 3:  # Level Up Animation
            done = level_up_animation()
            if done:
                game_state = 1  # Back to playing

        elif game_state == 0:
            draw_start_screen()

        elif game_state == 2:
            draw_game_over()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
