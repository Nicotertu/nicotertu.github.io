import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BOX_SIZE = 20
SNAKE_SIZE = 10
FOOD_SIZE = 10
FPS = 30
SNAKE_SPEED = 5
NUM_RANDOM_SNAKES = 19
LEADERBOARD_X = 10
LEADERBOARD_Y = 10
LEADERBOARD_SPACING = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Snake class
class Snake:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.length = 1
        self.direction = random.randint(0, 3) * 90
        self.body = [(self.x, self.y)]

    def move(self):
        dx = SNAKE_SPEED * math.cos(math.radians(self.direction))
        dy = SNAKE_SPEED * math.sin(math.radians(self.direction))
        self.x += dx
        self.y += dy
        self.body.insert(0, (self.x, self.y))
        if len(self.body) > self.length:
            self.body.pop()

    def draw(self, surface):
        for segment in self.body:
            pygame.draw.rect(surface, self.color, (segment[0], segment[1], SNAKE_SIZE, SNAKE_SIZE))

    def grow(self):
        self.length += 1

    def check_collision(self):
        # Check collision with borders
        if self.x < 0 or self.x >= SCREEN_WIDTH or self.y < 0 or self.y >= SCREEN_HEIGHT:
            return True
        # Check collision with itself
        for segment in self.body[1:]:
            if self.x == segment[0] and self.y == segment[1]:
                return True
        return False

# Food class
class Food:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH - FOOD_SIZE)
        self.y = random.randint(0, SCREEN_HEIGHT - FOOD_SIZE)
        self.color = GREEN

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, FOOD_SIZE, FOOD_SIZE))

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")

# Clock
clock = pygame.time.Clock()

# Player
player = Snake(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE)

# Food
foods = [Food() for _ in range(10)]

# Random snakes
random_snakes = [Snake(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), RED) for _ in range(NUM_RANDOM_SNAKES)]

# Leaderboard
leaderboard = []

# Main loop
running = True
while running:
    screen.fill(BLACK)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement towards mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()
    angle = math.atan2(mouse_y - player.y, mouse_x - player.x)
    angle_deg = math.degrees(angle)
    player.direction = angle_deg

    # Move the player
    player.move()

    # Draw the player
    player.draw(screen)

    # Draw the food
    for food in foods:
        food.draw(screen)

    # Check if the player eats food
    for food in foods:
        if (player.x < food.x + FOOD_SIZE and player.x + SNAKE_SIZE > food.x and
                player.y < food.y + FOOD_SIZE and player.y + SNAKE_SIZE > food.y):
            foods.remove(food)
            foods.append(Food())
            player.grow()

    # Move and draw the random snakes
    for snake in random_snakes:
        snake.move()
        snake.draw(screen)

        # Check if random snake collides with player or border
        if snake.check_collision():
            random_snakes.remove(snake)

        # Check if random snake eats food
        for food in foods:
            if (snake.x < food.x + FOOD_SIZE and snake.x + SNAKE_SIZE > food.x and
                    snake.y < food.y + FOOD_SIZE and snake.y + SNAKE_SIZE > food.y):
                foods.remove(food)
                foods.append(Food())
                snake.grow()

    # Check if player collides with border or itself
    if player.check_collision():
        running = False

    # Update the leaderboard
    leaderboard = sorted(random_snakes + [player], key=lambda x: x.length, reverse=True)[:5]

    # Draw the leaderboard
    for i, snake in enumerate(leaderboard):
        score_text = f"{i+1}. Snake Length: {snake.length}"
        score_surface = pygame.font.Font(None, 24).render(score_text, True, YELLOW)
        screen.blit(score_surface, (LEADERBOARD_X, LEADERBOARD_Y + i * LEADERBOARD_SPACING))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

pygame.quit()
