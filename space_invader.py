import pygame
import random
import sys
import os

# --- Fonction pour trouver le chemin des assets (cruciale pour le .exe) ---
def resource_path(relative_path):
    """ Obtenir le chemin absolu vers la ressource, fonctionne pour le dev et pour PyInstaller """
    try:
        # PyInstaller crée un dossier temporaire et y stocke le chemin dans _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Constantes du jeu ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
# Paramètres du joueur
PLAYER_WIDTH = 60
PLAYER_HEIGHT = 40
PLAYER_SPEED = 5
# Paramètres des projectiles
BULLET_WIDTH = 10
BULLET_HEIGHT = 30
BULLET_SPEED = 7
# Paramètres des aliens
ALIEN_WIDTH = 40
ALIEN_HEIGHT = 30
ALIEN_H_SPACING = 20
ALIEN_V_SPACING = 20
ALIEN_ROWS = 5
ALIEN_COLS = 10

# --- Initialisation de Pygame ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()
font_name = pygame.font.match_font('arial')

# --- Chargement des assets (sprites et sons) ---
assets_folder = "assets"

# Chargement des images en utilisant la fonction resource_path
try:
    player_img = pygame.image.load(resource_path(os.path.join(assets_folder, 'player.png'))).convert_alpha()
    player_img = pygame.transform.scale(player_img, (PLAYER_WIDTH, PLAYER_HEIGHT))
    alien_img = pygame.image.load(resource_path(os.path.join(assets_folder, 'alien.png'))).convert_alpha()
    alien_img = pygame.transform.scale(alien_img, (ALIEN_WIDTH, ALIEN_HEIGHT))
    player_bullet_img = pygame.image.load(resource_path(os.path.join(assets_folder, 'player_bullet.png'))).convert_alpha()
    player_bullet_img = pygame.transform.scale(player_bullet_img, (BULLET_WIDTH, BULLET_HEIGHT))
    alien_bullet_img = pygame.image.load(resource_path(os.path.join(assets_folder, 'alien_bullet.png'))).convert_alpha()
    alien_bullet_img = pygame.transform.scale(alien_bullet_img, (BULLET_WIDTH, BULLET_HEIGHT))
    
    background_img = pygame.image.load(resource_path(os.path.join(assets_folder, 'background.png'))).convert()
    background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    scrolling_background_img = pygame.image.load(resource_path(os.path.join(assets_folder, 'background_stars.png'))).convert()
    scrolling_background_img = pygame.transform.scale(scrolling_background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

except pygame.error as e:
    print(f"Erreur de chargement d'image : {e}")
    sys.exit()

# Chargement des sons en utilisant la fonction resource_path
try:
    shoot_sound = pygame.mixer.Sound(resource_path(os.path.join(assets_folder, 'laser.wav')))
    explosion_sound = pygame.mixer.Sound(resource_path(os.path.join(assets_folder, 'explosion.wav')))
    pygame.mixer.music.load(resource_path(os.path.join(assets_folder, 'music.ogg')))
    pygame.mixer.music.set_volume(0.3)
except pygame.error as e:
    print(f"Erreur de chargement de son : {e}")
    sys.exit()

# --- Classes du jeu ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img 
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speedx = 0
        self.lives = 3
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 250

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT] or keystate[pygame.K_a]:
            self.speedx = -PLAYER_SPEED
        if keystate[pygame.K_RIGHT] or keystate[pygame.K_d]:
            self.speedx = PLAYER_SPEED
        self.rect.x += self.speedx
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            player_bullets.add(bullet)
            shoot_sound.play()

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = alien_img 
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, is_alien=False):
        super().__init__()
        self.is_alien = is_alien
        if self.is_alien:
            self.image = alien_bullet_img
            self.speedy = BULLET_SPEED
        else:
            self.image = player_bullet_img
            self.speedy = -BULLET_SPEED
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y if not is_alien else y + BULLET_HEIGHT
    
    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

# --- Fonctions utilitaires ---
def draw_text(surf, text, size, x, y, color):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def create_aliens():
    for row in range(ALIEN_ROWS):
        for col in range(ALIEN_COLS):
            x = col * (ALIEN_WIDTH + ALIEN_H_SPACING) + 50
            y = row * (ALIEN_HEIGHT + ALIEN_V_SPACING) + 50
            alien = Alien(x, y)
            all_sprites.add(alien)
            aliens.add(alien)

def show_start_screen():
    screen.blit(background_img, (0, 0))
    draw_text(screen, "SPACE INVADERS", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, WHITE)
    draw_text(screen, "Flèches ou A/D pour bouger, Espace pour tirer", 22, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, WHITE)
    draw_text(screen, "Appuyez sur une touche pour commencer", 18, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4, WHITE)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                waiting = False

def show_game_over_screen():
    screen.blit(background_img, (0, 0))
    draw_text(screen, "GAME OVER", 64, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, RED)
    draw_text(screen, f"Score final : {score}", 28, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, WHITE)
    draw_text(screen, "Appuyez sur 'R' pour rejouer ou 'Q' pour quitter", 18, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 4, WHITE)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    waiting = False

# Variables pour le défilement
scrolling_background_rect = scrolling_background_img.get_rect()
scroll_y = 0
scroll_speed = 1.5

# --- Boucle principale du jeu ---
pygame.mixer.music.play(loops=-1)
game_over = True
running = True
while running:
    if game_over:
        if 'score' in locals() and score > 0:
            show_game_over_screen()
        else:
            show_start_screen()
        game_over = False
        # Réinitialisation
        all_sprites = pygame.sprite.Group()
        aliens = pygame.sprite.Group()
        player_bullets = pygame.sprite.Group()
        alien_bullets = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        create_aliens()
        score = 0
        level = 1
        alien_speed_x = 1
        alien_speed_y = 15
        alien_shoot_chance = 0.0005 * level

    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    all_sprites.update()

    move_down = False
    for alien in aliens:
        alien.rect.x += alien_speed_x
        if alien.rect.right > SCREEN_WIDTH or alien.rect.left < 0:
            move_down = True
    if move_down:
        alien_speed_x *= -1
        for alien in aliens:
            alien.rect.y += alien_speed_y
            if alien.rect.bottom >= player.rect.top:
                 player.lives = 0
                 game_over = True

    if random.random() < alien_shoot_chance and aliens.sprites():
        random_alien = random.choice(aliens.sprites())
        bullet = Bullet(random_alien.rect.centerx, random_alien.rect.bottom, is_alien=True)
        all_sprites.add(bullet)
        alien_bullets.add(bullet)
            
    hits = pygame.sprite.groupcollide(aliens, player_bullets, True, True)
    for hit in hits:
        score += 10
        explosion_sound.play()

    hits = pygame.sprite.spritecollide(player, alien_bullets, True)
    if hits:
        player.lives -= 1
        if player.lives <= 0:
            game_over = True

    hits = pygame.sprite.spritecollide(player, aliens, False)
    if hits:
        player.lives = 0
        game_over = True

    if not aliens:
        level += 1
        create_aliens()
        alien_speed_x = 1 * (1 + 0.2 * level)
        alien_shoot_chance = 0.0005 * level

    # --- Affichage ---
    rel_y = scroll_y % scrolling_background_rect.height
    screen.blit(scrolling_background_img, (0, rel_y - scrolling_background_rect.height))
    if rel_y < SCREEN_HEIGHT:
        screen.blit(scrolling_background_img, (0, rel_y))
    scroll_y += scroll_speed

    all_sprites.draw(screen)
    
    draw_text(screen, f"Score: {score}", 18, SCREEN_WIDTH / 2, 10, WHITE)
    draw_text(screen, f"Vies: {player.lives}", 18, 50, 10, GREEN)
    draw_text(screen, f"Niveau: {level}", 18, SCREEN_WIDTH - 50, 10, WHITE)
    
    pygame.display.flip()

pygame.quit()
sys.exit()