#importar las librerias necesarias  

import pygame
import sys
import random
import time
import json
from datetime import datetime
import math
import pygame.mixer
import os

# Inicialización de Pygame y el sistema de sonido
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("-= Space Conquers =-")
clock = pygame.time.Clock()

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# Colores modernos
NEON_GREEN = (57, 255, 20)
NEON_BLUE = (30, 144, 255)
NEON_PINK = (255, 20, 147)
NEON_PURPLE = (147, 20, 255)
NEON_RED = (255, 20, 60)
DARK_GRAY = (40, 40, 40)

try:
    # Ruta relativa al archivo actual
    BASE_PATH = os.path.join(os.path.dirname(__file__), "assets")
    
    print(f"Intentando cargar archivos desde: {BASE_PATH}")
    print(f"Ruta completa del fondo: {os.path.join(BASE_PATH, 'estrellas-galaxia.jpg')}")
    
    # Cargar imágenes
    player_image = pygame.image.load(os.path.join(BASE_PATH, 'juego-arcade.png'))
    enemy_image = pygame.image.load(os.path.join(BASE_PATH, 'monstruo.png'))
    menu_background = pygame.image.load(os.path.join(BASE_PATH, 'invaders.png'))
    game_background = pygame.image.load(f'{BASE_PATH}/estrellas-galaxia-jpg')
    game_logo = pygame.image.load(os.path.join(BASE_PATH, 'Space_Conquers_logo.png'))
    
    # Escalar imágenes
    game_logo = pygame.transform.scale(game_logo, (400, 200))
    menu_background = pygame.transform.scale(menu_background, (800, 600)) 
    
    # Cargar sonidos
    pygame.mixer.music.load(os.path.join(BASE_PATH, 'spaceinvaders1.mpeg'))
    shoot_sound = pygame.mixer.Sound(os.path.join(BASE_PATH, 'shoot.wav'))
    explosion_sound = pygame.mixer.Sound(os.path.join(BASE_PATH, 'explosion.wav'))
    
    # Escalar imágenes
    player_image = pygame.transform.scale(player_image, (50, 50))
    enemy_image = pygame.transform.scale(enemy_image, (40, 40))
    menu_background = pygame.transform.scale(menu_background, (800, 600))
    game_background = pygame.transform.scale(game_background, (800, 600))

#error al cargar recursos
except pygame.error as e:
    print(f"Error al cargar recursos: {e}")
    print(f"Ruta actual: {BASE_PATH}")
    pygame.quit()
    sys.exit(1)

# Constantes del juego
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_BULLET_SPEED = 7
INVULNERABLE_DURATION = 2000
LEVEL_PAUSE_DURATION = 2000

# Constantes para el menú
MENU_OPTIONS = ["Jugar", "Instrucciones", "Puntuaciones", "Salir"]
HIGH_SCORES_FILE = "high_scores.json"

# Funciones para manejar puntuaciones
def load_high_scores():
    try:
        with open(HIGH_SCORES_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"highest_score": 0, "recent_games": []}

# uardar puntuaciones
def save_high_scores(scores_data, current_score):
    # Actualizar máxima puntuación
    if current_score > scores_data["highest_score"]:
        scores_data["highest_score"] = current_score
    
    # Agregar partida actual a las recientes
    recent_game = {
        "score": current_score,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    scores_data["recent_games"].insert(0, recent_game)
    
    # Lista de las 10 mejores puntuaciones
    scores_data["recent_games"] = scores_data["recent_games"][:10]
    
    # Guardar en archivo
    with open(HIGH_SCORES_FILE, 'w') as file:
        json.dump(scores_data, file)

# Cargar sonidos de fondo
try:
    # Música de fondo
    pygame.mixer.music.load(os.path.join(BASE_PATH, 'spaceinvaders1.mpeg'))
    pygame.mixer.music.set_volume(0.5) 
    
    # Efectos de sonido
    shoot_sound = pygame.mixer.Sound(os.path.join(BASE_PATH, 'shoot.wav'))
    explosion_sound = pygame.mixer.Sound(os.path.join(BASE_PATH, 'explosion.wav'))
    
    # Ajustar volumen de los efectos de sonido
    shoot_sound.set_volume(0.4)
    explosion_sound.set_volume(0.6)
# control de error al cargar sonidos
except pygame.error as e:
    print(f"Error al cargar sonidos: {e}")
    shoot_sound = explosion_sound = pygame.mixer.Sound(buffer=b'')

# Función para controlar la música
def play_background_music():
    try:
        pygame.mixer.music.play(-1) 
    except pygame.error:
        pass
#detener la musica
def stop_background_music():
    try:
        pygame.mixer.music.stop()
    except pygame.error:
        pass

#menu principal
def show_menu():
    selected_option = 0
    menu_font = pygame.font.Font(None, 56)
    footer_font = pygame.font.Font(None, 24)
    
    while True:
        screen.blit(menu_background, (0, 0))
        overlay = pygame.Surface((800, 600))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Dibujar el logo
        logo_rect = game_logo.get_rect(center=(400, 150))
        screen.blit(game_logo, logo_rect)
        
        # dibujar opciones del menu
        for i, option in enumerate(MENU_OPTIONS):
           
            y_pos = 320 + i * 60 

            if i == selected_option:
                # Efecto de brillo para la opción seleccionada
                glow_surf = pygame.Surface((400, 50), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*NEON_GREEN, 30), (0, 0, 400, 50), border_radius=10)
                screen.blit(glow_surf, (200, y_pos - 10))
                
                # Texto seleccionado con efecto de brillo
                text = menu_font.render(option, True, NEON_GREEN)
                # Efecto de sombra
                shadow = menu_font.render(option, True, DARK_GRAY)
                screen.blit(shadow, (402 - text.get_width()//2, y_pos + 2))
            else:
                # Texto no seleccionado
                text = menu_font.render(option, True, WHITE)
            
            # Centrar texto
            text_rect = text.get_rect(center=(400, y_pos))
            screen.blit(text, text_rect)
        
        #footer
        footer_text = "Daniel Ruiz Poli - Academia Conquerblocks 2024"
        footer = footer_font.render(footer_text, True, WHITE)
        footer_rect = footer.get_rect(center=(400, 570)) 
        screen.blit(footer, footer_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(MENU_OPTIONS)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(MENU_OPTIONS)
                elif event.key == pygame.K_RETURN:
                    return MENU_OPTIONS[selected_option]
        
        clock.tick(60)

#instrucciones de juego
def show_instructions():
    instruction_font = pygame.font.Font(None, 36)
    instructions = [
        "Controles:",
        "Flechas: Mover nave",
        "Espacio: Disparar",
        "",
        "Objetivo:",
        "Destruye todos los invasores",
        "Evita que lleguen abajo",
        "",
        "Presiona ENTER para volver"
    ]
    
    while True:
        # Dibujar fondo
        screen.blit(menu_background, (0, 0))
        
        # Overlay semi-transparente
        overlay = pygame.Surface((800, 600))
        overlay.fill(BLACK)
        overlay.set_alpha(160)  
        screen.blit(overlay, (0, 0))
        
        for i, line in enumerate(instructions):
            text = instruction_font.render(line, True, WHITE)
            screen.blit(text, (400 - text.get_width()//2, 100 + i * 40))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return
        
        clock.tick(60)

# Puntuaciones
def show_high_scores():
    scores_data = load_high_scores()
    score_font = pygame.font.Font(None, 36)
    
    while True:
        # Dibujar fondo
        screen.blit(menu_background, (0, 0))
        
        # Overlay semi-transparente
        overlay = pygame.Surface((800, 600))
        overlay.fill(BLACK)
        overlay.set_alpha(160)
        screen.blit(overlay, (0, 0))
        
        # Mostrar máxima puntuación
        highest_text = score_font.render(f"Máxima puntuación: {scores_data['highest_score']}", True, GREEN)
        screen.blit(highest_text, (400 - highest_text.get_width()//2, 100))
        
        # Mostrar últimas partidas
        title_text = score_font.render("Últimas partidas:", True, WHITE)
        screen.blit(title_text, (400 - title_text.get_width()//2, 180))
        
        for i, game in enumerate(scores_data["recent_games"]):
            game_text = score_font.render(
                f"{game['date']}: {game['score']} puntos",
                True, WHITE
            )
            screen.blit(game_text, (400 - game_text.get_width()//2, 220 + i * 30))
        
        back_text = score_font.render("Presiona ENTER para volver", True, GRAY)
        screen.blit(back_text, (400 - back_text.get_width()//2, 550))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return
        
        clock.tick(60)

# Función para el splash screen
def show_splash_screen():
    screen.fill(BLACK)
    
    # Título principal
    title_font = pygame.font.Font(None, 64)
    title_text = title_font.render("Space Conquers", True, GREEN)
    screen.blit(title_text, (400 - title_text.get_width()//2, 200))
    
    # Información del desarrollador
    info_font = pygame.font.Font(None, 32)
    info_texts = [
        "Desarrollado por: Daniel Ruiz Poli",
        "GitHub : PoliXdev",
        "Versión 1.8",
        "Master Desarrollo Full Stack",
        "Academia ConquerBlocks 2024",
        "Presiona ESPACIO para comenzar"
    ]
    
    y_position = 300
    for text in info_texts:
        info_surface = info_font.render(text, True, WHITE)
        screen.blit(info_surface, (400 - info_surface.get_width()//2, y_position))
        y_position += 40
    
    pygame.display.flip()
    
    # Esperar a que el jugador presione espacio
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
        clock.tick(60)

# Jugador
class Player:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 50
        self.speed = PLAYER_SPEED
        self.image = player_image
        self.rect = self.image.get_rect(x=self.x, y=self.y)
        self.lives = 3
        self.is_alive = True
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.shoot_delay = 250
        self.last_shot = 0
        self.shoot_sound = shoot_sound
        self.hit_sound = explosion_sound
#movimiento jugador
    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > SCREEN_HEIGHT // 2:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed
        self.rect.x = self.x
        self.rect.y = self.y
# funcion para disparar
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            self.last_shot = current_time
            try:
                self.shoot_sound.play()
            except pygame.error:
                pass
            return Bullet(self.x + self.width//2, self.y)
        return None
# funcion para golpear al jugador
    def hit(self):
        if not self.invulnerable:
            try:
                self.hit_sound.play()
            except pygame.error:
                pass
            self.lives -= 1
            if self.lives <= 0:
                self.is_alive = False
            else:
                self.invulnerable = True
                self.invulnerable_timer = pygame.time.get_ticks()
# funcion para actualizar jugador
    def update(self):
        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            if current_time - self.invulnerable_timer > INVULNERABLE_DURATION:
                self.invulnerable = False
#dibujar jugador
    def draw(self):
        if not self.invulnerable or pygame.time.get_ticks() % 200 < 100:
            screen.blit(self.image, self.rect)

# Enemigo
class Enemy:
    def __init__(self, x, y, level):
        self.width = 40
        self.height = 40
        self.x = x
        self.y = y
        self.speed = 2 + (level * 0.5)
        self.direction = 1
        self.image = enemy_image
        self.rect = self.image.get_rect(x=x, y=y)
        self.shoot_delay = max(3000 - (level * 200), 1000)
        self.last_shot = pygame.time.get_ticks() + random.randint(0, 2000)
        self.explosion_sound = explosion_sound
#movimiento enemigo
    def move(self):
        self.x += self.speed * self.direction
        self.rect.x = self.x
#disparo enemigo
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            self.last_shot = current_time
            return EnemyBullet(self.x + self.width//2, self.y + self.height)
        return None

    def draw(self):
        screen.blit(self.image, self.rect)
#destruir enemigo
    def destroy(self):
        try:
            self.explosion_sound.play()
        except pygame.error:
            pass

# Disparo
class Bullet:
    def __init__(self, x, y):
        self.width = 5
        self.height = 15
        self.x = x
        self.y = y
        self.speed = 10
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.active = True
        self.trail = []
#movimiento bala
    def move(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
        self.y -= self.speed
        self.rect.y = self.y
        if self.y < 0:
            self.active = False
#dibujar bala
    def draw(self):
        # Dibujar estela
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int((i / len(self.trail)) * 255)
            trail_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(trail_surf, (*NEON_BLUE, alpha), (0, 0, self.width, self.height))
            screen.blit(trail_surf, (trail_x - self.width//2, trail_y))
        
        # Dibujar bala
        pygame.draw.rect(screen, NEON_BLUE, (self.x - self.width//2, self.y, self.width, self.height))

# Clase para los disparos enemigos
class EnemyBullet(Bullet):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = -7  # Velocidad negativa para que vaya hacia abajo
        self.color = NEON_PINK
    
    def draw(self):
        # Dibujar estela
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int((i / len(self.trail)) * 255)
            trail_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(trail_surf, (*self.color, alpha), (0, 0, self.width, self.height))
            screen.blit(trail_surf, (trail_x - self.width//2, trail_y))
        
        # Dibujar bala
        pygame.draw.rect(screen, self.color, (self.x - self.width//2, self.y, self.width, self.height))

# Efectos de partículas para explosiones
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 4)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 5)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.lifetime = 30
  #actualizar partículas
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        self.size = max(0, self.size - 0.1)
   # dibujar partículas
    def draw(self):
        if self.lifetime > 0:
            alpha = int((self.lifetime / 30) * 255)
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (self.size, self.size), self.size)
            screen.blit(surf, (self.x - self.size, self.y - self.size))

# Clase para efectos visuales
class VisualEffects:
    def __init__(self):
        self.particles = []
      # crear explosion
    def create_explosion(self, x, y, color):
        for _ in range(20):
            self.particles.append(Particle(x, y, color))
      # actualizar partículas
    def update(self):
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()
      # dibujar partículas
    def draw(self):
        for particle in self.particles:
            particle.draw()

# Modificar el flujo principal del juego
def main_game():
    level = 1
    while True:  # Bucle de niveles
        player = Player()
        # Aumentan el número de enemigos y su disposición según el nivel
        enemies = []
        rows = min(3 + level//2, 5) 
        cols = min(8 + level//2, 12) 
        for y in range(rows):
            for x in range(cols):
                enemies.append(Enemy(x * 60 + 50, y * 60 + 50, level))
        
        bullets = []
        enemy_bullets = []
        score = 0
        visual_effects = VisualEffects()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            if player.is_alive:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    new_bullet = player.shoot()
                    if new_bullet:
                        bullets.append(new_bullet)

                player.move()
                player.update()
                
                # Disparos enemigos
                for enemy in enemies:
                    new_bullet = enemy.shoot()
                    if new_bullet:
                        enemy_bullets.append(new_bullet)
                
                # Actualizar balas enemigas y detectar colisiones con el jugador
                for bullet in enemy_bullets[:]:
                    bullet.move()
                    if not bullet.active or bullet.y > 600:
                        enemy_bullets.remove(bullet)
                    elif player.rect.colliderect(bullet.rect) and not player.invulnerable:
                        player.hit()
                        enemy_bullets.remove(bullet)
                        visual_effects.create_explosion(player.x + 25, player.y + 25, NEON_BLUE)
                
               # eliminar enemigos y balas
                enemies_to_remove = []
                bullets_to_remove = []
                
                for enemy in enemies:
                    enemy.move()
                    if enemy.x <= 0 or enemy.x >= 760:
                        enemy.direction *= -1
                        enemy.y += 20
                        enemy.rect.y = enemy.y
                    
                    if player.rect.colliderect(enemy.rect) and not player.invulnerable:
                        player.hit()
                    
                    if enemy.y > 440:
                        player.is_alive = False
                        break

                # actualizar balas
                for bullet in bullets:
                    bullet.move()
                    if not bullet.active:
                        bullets_to_remove.append(bullet)
                    else:
                        for enemy in enemies:
                            if bullet.rect.colliderect(enemy.rect):
                                visual_effects.create_explosion(enemy.x + 20, enemy.y + 20, NEON_PINK)
                                enemies_to_remove.append(enemy)
                                bullets_to_remove.append(bullet)
                                score += 100
                                break

                
                # eliminar enemigos y balas
                for enemy in enemies_to_remove:
                    if enemy in enemies: 
                        enemy.destroy()
                        enemies.remove(enemy)
                for bullet in bullets_to_remove:
                    if bullet in bullets:  
                        bullets.remove(bullet)

                
                visual_effects.update()

                # Dibujar
                screen.blit(game_background, (0, 0))
                
                overlay = pygame.Surface((800, 600))
                overlay.fill(BLACK)
                overlay.set_alpha(100)
                screen.blit(overlay, (0, 0))
                
                player.draw()
                player.draw()
                for enemy in enemies:
                    enemy.draw()
                for bullet in bullets:
                    bullet.draw()
                for bullet in enemy_bullets:
                    bullet.draw()
                visual_effects.draw()

                
                ui_background = pygame.Surface((200, 100))
                ui_background.fill(BLACK)
                ui_background.set_alpha(128)
                screen.blit(ui_background, (5, 5))
                
                # UI actualizada
                score_text = font.render(f"Puntuación: {score}", True, WHITE)
                lives_text = font.render(f"Vidas: {player.lives}", True, WHITE)
                level_text = font.render(f"Nivel: {level}", True, WHITE)
                screen.blit(score_text, (10, 10))
                screen.blit(lives_text, (10, 40))
                screen.blit(level_text, (10, 70))

                if not enemies:
                    # Overlay para el mensaje de nivel completado
                    message_overlay = pygame.Surface((800, 600))
                    message_overlay.fill(BLACK)
                    message_overlay.set_alpha(160)
                    screen.blit(message_overlay, (0, 0))
                    
                    # Crear los textos
                    level_complete_text = font.render("¡NIVEL COMPLETADO!", True, NEON_GREEN)
                    next_level_text = font.render("Preparando siguiente nivel...", True, WHITE)
                    
                    # Obtener los rectángulos para centrar
                    level_complete_rect = level_complete_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 25))
                    next_level_rect = next_level_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 25))
                    
                    # Dibujar textos centrados
                    screen.blit(level_complete_text, level_complete_rect)
                    screen.blit(next_level_text, next_level_rect)
                    
                    pygame.display.flip()
                    pygame.time.wait(2000)
                    level += 1
                    break
            else:
                # Overlay para game over
                message_overlay = pygame.Surface((800, 600))
                message_overlay.fill(BLACK)
                message_overlay.set_alpha(160)
                screen.blit(message_overlay, (0, 0))
                
                # Crear los textos
                game_over_text = font.render("GAME OVER", True, NEON_RED)
                final_score_text = font.render(f"Puntuación final: {score}", True, WHITE)
                level_reached_text = font.render(f"Nivel alcanzado: {level}", True, WHITE)
                
                # Calcular posiciones centradas
                game_over_x = (SCREEN_WIDTH - game_over_text.get_width()) // 2
                final_score_x = (SCREEN_WIDTH - final_score_text.get_width()) // 2
                level_reached_x = (SCREEN_WIDTH - level_reached_text.get_width()) // 2
                
                # Dibujar textos centrados
                screen.blit(game_over_text, (game_over_x, 250))
                screen.blit(final_score_text, (final_score_x, 300))
                screen.blit(level_reached_text, (level_reached_x, 350))
                
                pygame.display.flip()
                pygame.time.wait(3000)
                stop_background_music()
                return score

            pygame.display.flip()
            clock.tick(60)


font = pygame.font.Font(None, 36)

# Flujo principal / menu principal
show_splash_screen()

# Iniciar la música 
play_background_music()

while True:
    option = show_menu()
    
    if option == "Jugar":
        final_score = main_game()
        scores_data = load_high_scores()
        save_high_scores(scores_data, final_score)
    elif option == "Instrucciones":
        show_instructions()
    elif option == "Puntuaciones":
        show_high_scores()
    elif option == "Salir":
        stop_background_music()
        break







