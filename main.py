import pygame
import sys
import random
import os
from pygame.locals import *

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
GRAVITY = 0.25
FLAP_STRENGTH = -7
PIPE_SPEED = 3
PIPE_SPAWN_TIME = 1500  # milliseconds
PIPE_GAP = 150
GROUND_HEIGHT = 100

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)

# Set up the game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Flappy Bird')
clock = pygame.time.Clock()

class Bird:
    def __init__(self):
        self.x = WINDOW_WIDTH // 3
        self.y = WINDOW_HEIGHT // 2
        self.velocity = 0
        self.rect = pygame.Rect(self.x, self.y, 30, 30)

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = self.y

    def draw(self):
        pygame.draw.rect(screen, (255, 255, 0), self.rect)  # Yellow bird

class Pipe:
    def __init__(self):
        self.gap_y = random.randint(200, WINDOW_HEIGHT - 200)
        self.x = WINDOW_WIDTH
        self.width = 50
        self.passed = False
        
        self.top_height = self.gap_y - PIPE_GAP // 2
        self.bottom_height = WINDOW_HEIGHT - (self.gap_y + PIPE_GAP // 2)
        
        self.top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        self.bottom_rect = pygame.Rect(
            self.x,
            WINDOW_HEIGHT - self.bottom_height,
            self.width,
            self.bottom_height
        )

    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self):
        pygame.draw.rect(screen, (0, 255, 0), self.top_rect)  # Green pipes
        pygame.draw.rect(screen, (0, 255, 0), self.bottom_rect)

class Game:
    def __init__(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.high_score = self.load_high_score()
        self.game_over = False
        self.last_pipe = pygame.time.get_ticks()

    def load_high_score(self):
        try:
            with open('high_score.txt', 'r') as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        with open('high_score.txt', 'w') as f:
            f.write(str(self.high_score))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE and not self.game_over:
                    self.bird.flap()
                if event.key == K_r and self.game_over:
                    self.__init__()

    def update(self):
        if not self.game_over:
            self.bird.update()

            # Spawn new pipes
            now = pygame.time.get_ticks()
            if now - self.last_pipe > PIPE_SPAWN_TIME:
                self.pipes.append(Pipe())
                self.last_pipe = now

            # Update pipes and check collisions
            for pipe in self.pipes[:]:
                pipe.update()
                
                # Check if pipe is passed
                if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                    pipe.passed = True
                    self.score += 1
                
                # Remove off-screen pipes
                if pipe.x + pipe.width < 0:
                    self.pipes.remove(pipe)
                
                # Check collisions
                if (pipe.top_rect.colliderect(self.bird.rect) or
                    pipe.bottom_rect.colliderect(self.bird.rect)):
                    self.game_over = True

            # Check ground/ceiling collision
            if self.bird.y < 0 or self.bird.y + self.bird.rect.height > WINDOW_HEIGHT:
                self.game_over = True

            # Update high score
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

    def draw(self):
        screen.fill(SKY_BLUE)
        
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw()
        
        # Draw bird
        self.bird.draw()
        
        # Draw ground
        pygame.draw.rect(screen, (101, 67, 33), (0, WINDOW_HEIGHT - GROUND_HEIGHT, WINDOW_WIDTH, GROUND_HEIGHT))
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, BLACK)
        high_score_text = font.render(f'High Score: {self.high_score}', True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 40))

        if self.game_over:
            game_over_text = font.render('Game Over! Press R to restart', True, BLACK)
            screen.blit(game_over_text, (WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2))

        pygame.display.flip()

def main():
    game = Game()
    
    while True:
        game.handle_events()
        game.update()
        game.draw()
        clock.tick(60)

if __name__ == '__main__':
    main()