import pygame
import random
import sys
import math

pygame.init()

# Costanti
TILE_SIZE = 28
COLS = 19
ROWS = 21
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Crep a Coer")
CLOCK = pygame.time.Clock()
FONT = pygame.font.Font(None, 36)
BIG_FONT = pygame.font.Font(None, 72)

# Colori
BLACK = (0, 0, 0)
BLUE = (0, 100, 200)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (255, 100, 150)
CYAN = (100, 255, 255)
ORANGE = (255, 150, 0)
GHOST_BLUE = (20, 0, 200)
GOLD = (255, 215, 0)

# Carica immagini (mocassino e logo)
mocassino_img = None
logo_img = None

try:
    mocassino_img = pygame.image.load('mocassino.png').convert_alpha()
    mocassino_img = pygame.transform.scale(mocassino_img, (32, 32))
except Exception as e:
    print("mocassino.png non trovato:", e)

try:
    logo_img = pygame.image.load('logo_amr.png').convert_alpha()
    logo_img = pygame.transform.scale(logo_img, (TILE_SIZE * 2, TILE_SIZE * 2))
except Exception as e:
    print("logo_amr.png non trovato:", e)

# Posizioni loghi
logo_positions = [
    (9 * TILE_SIZE + TILE_SIZE//2, 6 * TILE_SIZE + TILE_SIZE//2),
    (4 * TILE_SIZE + TILE_SIZE//2, 12 * TILE_SIZE + TILE_SIZE//2),
    (14 * TILE_SIZE + TILE_SIZE//2, 12 * TILE_SIZE + TILE_SIZE//2),
    (9 * TILE_SIZE + TILE_SIZE//2, 16 * TILE_SIZE + TILE_SIZE//2)
]

# Power-up
powerup_active = False
powerup_timer = 0
POWERUP_DURATION = 8

# Labirinto
MAZE = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,2,1],
    [1,2,2,2,2,1,2,2,2,2,2,2,2,1,2,2,2,2,1],
    [1,1,1,1,2,1,1,1,1,1,1,1,1,1,2,1,1,1,1],
    [0,0,0,1,2,1,0,0,2,1,2,0,0,1,2,1,0,0,0],
    [1,1,1,1,2,1,0,1,2,1,2,1,0,1,2,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,1,2,1,1,1,2,1,1,1,1,1,2,1],
    [1,2,2,2,2,0,2,2,0,0,0,2,2,0,2,2,2,2,1],
    [1,1,1,1,2,1,1,1,1,1,1,1,1,1,2,1,1,1,1],
    [0,2,2,2,2,2,0,0,0,0,0,0,0,2,2,2,2,0,0],
    [1,1,1,1,2,2,2,1,1,0,1,1,2,2,2,1,1,1,1],
    [0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
    [1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,1],
    [1,2,2,2,2,1,2,0,0,0,0,0,2,1,2,2,2,2,1],
    [1,1,1,1,2,1,2,1,1,1,1,1,2,1,2,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,1,1,2,1,2,1,1,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

def crea_elementi():
    walls = []
    dots = []
    for y in range(ROWS):
        for x in range(COLS):
            if MAZE[y][x] == 1:
                walls.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif MAZE[y][x] == 2:
                dots.append(pygame.Rect(x * TILE_SIZE + 8, y * TILE_SIZE + 8, 12, 12))
    return walls, dots

def get_shoe_sprite(direction):
    if mocassino_img is None:
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(surf, (200, 200, 200), (16, 16), 14)
        return surf
    else:
        angle = -90 * direction
        rotated = pygame.transform.rotate(mocassino_img, angle)
        return rotated

def draw_ghost(screen, color, rect):
    body_rect = pygame.Rect(rect.left + 2, rect.top + 8, 16, 12)
    pygame.draw.rect(screen, color, body_rect)
    
    head_center = (rect.centerx, rect.centery - 2)
    pygame.draw.circle(screen, color, head_center, 9)
    
    left_eye = (rect.centerx - 4, rect.centery)
    right_eye = (rect.centerx + 4, rect.centery)
    pygame.draw.circle(screen, WHITE, left_eye, 2)
    pygame.draw.circle(screen, WHITE, right_eye, 2)
    pygame.draw.circle(screen, GHOST_BLUE, left_eye, 1)
    pygame.draw.circle(screen, GHOST_BLUE, right_eye, 1)
    
    wave_points = [
        (rect.left + 2, rect.bottom - 2),
        (rect.left + 6, rect.bottom),
        (rect.centerx, rect.bottom - 4),
        (rect.right - 6, rect.bottom),
        (rect.right - 2, rect.bottom - 2)
    ]
    pygame.draw.lines(screen, color, False, wave_points, 0)
    pygame.draw.circle(screen, color, (rect.centerx - 3, rect.bottom - 5), 2)
    pygame.draw.circle(screen, color, (rect.centerx + 3, rect.bottom - 5), 2)

def draw_animated_logo(screen, pos, time):
    if logo_img is not None:
        scale = 1.0 + 0.1 * math.sin(time * 4)
        angle = 10 * math.sin(time * 2)
        
        scaled = pygame.transform.scale(logo_img,
            (int(logo_img.get_width() * scale), int(logo_img.get_height() * scale)))
        rotated = pygame.transform.rotate(scaled, angle)
        
        rect = rotated.get_rect(center=pos)
        screen.blit(rotated, rect)
    else:
        text = BIG_FONT.render("AMR", True, (220, 20, 60))
        text = pygame.transform.rotate(text, 10 * math.sin(time * 2))
        rect = text.get_rect(center=pos)
        screen.blit(text, rect)

def reset():
    global walls, dots, player, ghosts, player_dir, score, state, start_time, powerup_active, powerup_timer
    walls, dots = crea_elementi()
    
    # Posizione SICURA del mocassino (tile completamente libero)
    player = pygame.Rect(0, 0, 20, 20)
    player.center = (266, 322)  # Centro tile (9,11) libero

    ghosts = [
        pygame.Rect(5 * TILE_SIZE, 5 * TILE_SIZE, 20, 20),
        pygame.Rect(13 * TILE_SIZE, 5 * TILE_SIZE, 20, 20),
        pygame.Rect(5 * TILE_SIZE, 15 * TILE_SIZE, 20, 20),
        pygame.Rect(13 * TILE_SIZE, 15 * TILE_SIZE, 20, 20)
    ]
    
    player_dir = 0
    score = 0
    state = 'playing'
    start_time = pygame.time.get_ticks() / 1000.0
    powerup_active = False
    powerup_timer = 0

reset()

SPEED_PLAYER = 4.5
SPEED_GHOST = 2.8

running = True
while running:
    current_time = pygame.time.get_ticks() / 1000.0
    anim_time = current_time - start_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if state != 'playing' and event.key == pygame.K_SPACE:
                reset()

    if state == 'playing':
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]: dx = -SPEED_PLAYER
        if keys[pygame.K_RIGHT]: dx = SPEED_PLAYER
        if keys[pygame.K_UP]: dy = -SPEED_PLAYER
        if keys[pygame.K_DOWN]: dy = SPEED_PLAYER

        if dx != 0:
            player_dir = 0 if dx > 0 else 2
        elif dy != 0:
            player_dir = 1 if dy > 0 else 3

        # Movimento con tolleranza
        old_center = player.center
        player.centerx += dx
        if player.collidelist(walls) != -1:
            player.centerx = old_center[0]
        player.centery += dy
        if player.collidelist(walls) != -1:
            player.centery = old_center[1]

        # Power-up: contatto con logo
        for i in range(len(logo_positions)-1, -1, -1):
            lx, ly = logo_positions[i]
            logo_rect = pygame.Rect(lx - 20, ly - 20, 40, 40)
            if player.colliderect(logo_rect):
                powerup_active = True
                powerup_timer = current_time + POWERUP_DURATION

        if powerup_active and current_time > powerup_timer:
            powerup_active = False

        # Movimento fantasmi migliorato
        for ghost in ghosts:
            directions = [(SPEED_GHOST,0), (-SPEED_GHOST,0), (0,SPEED_GHOST), (0,-SPEED_GHOST)]
            best_dir = random.choice(directions)
            best_dist = float('inf')

            for ddx, ddy in directions:
                test = ghost.copy()
                test.centerx += ddx
                test.centery += ddy
                if test.collidelist(walls) == -1:
                    dist = math.hypot(player.centerx - test.centerx, player.centery - test.centery)
                    if dist < best_dist:
                        best_dist = dist
                        best_dir = (ddx, ddy)

            ghost.centerx += best_dir[0]
            ghost.centery += best_dir[1]

            # Se ancora bloccato, prova casuale
            if ghost.collidelist(walls) != -1:
                random.shuffle(directions)
                for ddx, ddy in directions:
                    test = ghost.copy()
                    test.centerx += ddx
                    test.centery += ddy
                    if test.collidelist(walls) == -1:
                        ghost.centerx += ddx
                        ghost.centery += ddy
                        break

        # Mangia puntini
        i = 0
        while i < len(dots):
            if player.colliderect(dots[i]):
                del dots[i]
                score += 10
            else:
                i += 1

        # Collisione fantasmi
        for ghost in ghosts:
            if player.colliderect(ghost):
                if powerup_active:
                    ghost.center = (280, 280)  # riposiziona
                    score += 200
                else:
                    state = 'lose'
                    break

        if not dots:
            state = 'win'

    # Disegna
    SCREEN.fill(BLACK)
    for wall in walls:
        pygame.draw.rect(SCREEN, BLUE, wall)
    for dot in dots:
        pygame.draw.circle(SCREEN, WHITE, dot.center, 6)

    # Mocassino
    shoe_sprite = get_shoe_sprite(player_dir)

    if powerup_active:
        gold_overlay = pygame.Surface(shoe_sprite.get_size(), pygame.SRCALPHA)
        gold_overlay.fill((255, 215, 0, 140))
        shoe_sprite.blit(gold_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    shoe_rect = shoe_sprite.get_rect(center=player.center)
    SCREEN.blit(shoe_sprite, shoe_rect)

    # Fantasmi
    colors_ghost = [RED, PINK, CYAN, ORANGE]
    for i, ghost in enumerate(ghosts):
        draw_ghost(SCREEN, colors_ghost[i], ghost)

    # Loghi animati
    for pos in logo_positions:
        draw_animated_logo(SCREEN, pos, anim_time)

    # UI
    score_text = FONT.render(f"Punteggio: {score}", True, WHITE)
    SCREEN.blit(score_text, (10, 10))

    if state == 'win':
        win_text = FONT.render("VITTORIA! Premi SPAZIO per rigiocare", True, WHITE)
        SCREEN.blit(win_text, (WIDTH//2 - 220, HEIGHT//2))
    elif state == 'lose':
        lose_text = FONT.render("PERSO! Premi SPAZIO per rigiocare", True, WHITE)
        SCREEN.blit(lose_text, (WIDTH//2 - 220, HEIGHT//2))

    pygame.display.flip()
    CLOCK.tick(60)

pygame.quit()
sys.exit()