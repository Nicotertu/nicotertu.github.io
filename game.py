import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
SNAKE_SIZE = 10
FOOD_SIZE = 5
FPS = 30
SNAKE_SPEED = 5
NUM_RANDOM_SNAKES = 10
LEADERBOARD_X = 10
LEADERBOARD_Y = 10
LEADERBOARD_SPACING = 20
DIRECTION_CHANGE_INTERVAL = 1  # frames
INITIAL_SNAKE_SIZE = 5
INITIAL_FOOD = 200
ROTATION_SPEED = 15  # degrees per frame
RESPAWN_SAFE_DISTANCE = 300

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
        self.length = INITIAL_SNAKE_SIZE
        self.direction = random.randint(0, 359)
        self.target_direction = self.direction
        self.body = [(self.x, self.y)]
        self.alive = True
        self.kills = 0

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
            pygame.draw.rect(surface, self.color, (segment[0], segment[1], SNAKE_SIZE, SNAKE_SIZE), border_radius= 10)

    def grow(self):
        self.length += 1

    def check_collision(self):
        if self.x < 0 or self.x >= SCREEN_WIDTH or self.y < 0 or self.y >= SCREEN_HEIGHT:
            return True
        return False

    def check_collision_with_snakes(self, other_snakes):
        for snake in other_snakes:
            if snake != self and snake.alive:
                for segment in snake.body:
                    if self.x < segment[0] + SNAKE_SIZE and self.x + SNAKE_SIZE > segment[0] and \
                    self.y < segment[1] + SNAKE_SIZE and self.y + SNAKE_SIZE > segment[1]:
                        if snake.alive:  # Ensure that only alive snakes can kill
                            snake.kills += 1  # Increment the kills count
                        return True
        return False

    def respawn(self, is_player=False, other_snakes=[]):
        self.kills = 0
        if is_player:
            self.x = SCREEN_WIDTH // 2
            self.y = SCREEN_HEIGHT // 2
        else:
            while True:
                self.x = random.randint(SCREEN_WIDTH / 10, SCREEN_WIDTH * 9/10)
                self.y = random.randint(SCREEN_HEIGHT / 10, SCREEN_HEIGHT * 9/10)
                too_close = False
                for snake in other_snakes:
                    if distance(self.x, self.y, snake.x, snake.y) < RESPAWN_SAFE_DISTANCE:
                        too_close = True
                        break
                if not too_close:
                    break
        self.direction = random.randint(0, 359)
        self.target_direction = self.direction
        self.length = INITIAL_SNAKE_SIZE
        self.body = [(self.x, self.y)]
        self.alive = True

    def update_direction(self):
        if self.direction != self.target_direction:
            difference = (self.target_direction - self.direction + 360) % 360
            if difference > 180:
                difference -= 360
            change = min(ROTATION_SPEED, abs(difference)) * (1 if difference > 0 else -1)
            self.direction = (self.direction + change) % 360

# Food class
class Food:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH - FOOD_SIZE)
        self.y = random.randint(0, SCREEN_HEIGHT - FOOD_SIZE)
        self.color = GREEN

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, FOOD_SIZE, FOOD_SIZE))

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")

# Clock
clock = pygame.time.Clock()

# Player
player = Snake(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE)

# Food
foods = [Food() for _ in range(INITIAL_FOOD)]

# Random snakes
random_snakes = [Snake(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), RED) for _ in range(NUM_RANDOM_SNAKES)]

# Leaderboard
leaderboard = []

# Main loop
running = True
frame_count = 0
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
    player.target_direction = angle_deg

    # Update the player's direction gradually
    player.update_direction()

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
        if not snake.alive:
            snake.respawn(other_snakes=[player])

        # Change direction periodically
        if frame_count % DIRECTION_CHANGE_INTERVAL == 0:
            snake.target_direction = random.randint(0, 359)

        # Update the snake's direction gradually
        snake.update_direction()

        snake.move()
        snake.draw(screen)

        # Check if random snake collides with border or itself
        if snake.check_collision():
            snake.alive = False
            
        if snake.check_collision_with_snakes([player] + random_snakes):
            snake.alive = False

        # Check if random snake eats food
        for food in foods:
            if (snake.x < food.x + FOOD_SIZE and snake.x + SNAKE_SIZE > food.x and
                    snake.y < food.y + FOOD_SIZE and snake.y + SNAKE_SIZE > food.y):
                foods.remove(food)
                foods.append(Food())
                snake.grow()

    # Check if player collides with border
    if player.check_collision():
        player.alive = False
    
    # Check collisions between the player and random snakes
    if player.check_collision_with_snakes(random_snakes):
        player.alive = False

    # Respawn player if dead
    if not player.alive:
        player.respawn(is_player=True)

    # Update the leaderboard
    leaderboard = sorted(random_snakes + [player], key=lambda x: x.length, reverse=True)[:5]

    # Draw the leaderboard
    for i, snake in enumerate(leaderboard):
        score_text = f"{i+1}. Snake Length: {snake.length} | Kills: {snake.kills}"
        score_surface = pygame.font.Font(None, 24).render(score_text, True, YELLOW)
        screen.blit(score_surface, (LEADERBOARD_X, LEADERBOARD_Y + i * LEADERBOARD_SPACING))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)
    frame_count += 1

pygame.quit()
