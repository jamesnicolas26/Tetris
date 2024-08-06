import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
BACKGROUND_COLOR = (0, 0, 0)
GRID_COLOR = (100, 100, 100)
TETROMINO_COLORS = [
    (0, 255, 255),  # Cyan
    (255, 165, 0),  # Orange
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (0, 255, 0),    # Green
    (128, 0, 128),  # Purple
    (255, 0, 0),    # Red
]
FONT_SIZE = 30
FALL_TIME = 50  # Time in milliseconds for tetromino to fall
PAUSE_TIME = 50  # Time delay for instant drop

# Define tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # Z
    [[1, 1, 0], [0, 1, 1]],  # S
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
]

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')

# Setup fonts
font = pygame.font.Font(None, FONT_SIZE)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def draw_grid(surface):
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))

def draw_tetromino(surface, shape, offset, color):
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(
                    surface,
                    color,
                    (offset[0] + x * GRID_SIZE, offset[1] + y * GRID_SIZE, GRID_SIZE, GRID_SIZE),
                    border_radius=5
                )

def check_collision(grid, shape, offset):
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                grid_x = x + offset[0] // GRID_SIZE
                grid_y = y + offset[1] // GRID_SIZE
                if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y >= GRID_HEIGHT or grid[grid_y][grid_x]:
                    return True
    return False

def clear_lines(grid):
    full_lines = []
    for y, row in enumerate(grid):
        if all(row):
            full_lines.append(y)
    for y in full_lines:
        del grid[y]
        grid.insert(0, [0] * GRID_WIDTH)
    return len(full_lines)

def rotate(shape):
    return list(zip(*shape[::-1]))

def drop_tetromino(grid, shape, x, y):
    while not check_collision(grid, shape, (x, y + GRID_SIZE)):
        y += GRID_SIZE
    return y - GRID_SIZE

def draw_game_over_screen(score):
    screen.fill(BACKGROUND_COLOR)
    draw_text("Game Over", font, (255, 0, 0), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
    draw_text(f"Score: {score}", font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_text("Press Enter to Restart", font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5)
    pygame.display.flip()

def main_game_loop():
    grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    clock = pygame.time.Clock()
    game_over = False
    score = 0
    fall_time = 0

    def new_tetromino():
        shape = random.choice(SHAPES)
        color = random.choice(TETROMINO_COLORS)
        return shape, color, GRID_WIDTH // 2 * GRID_SIZE, 0

    def reset_game():
        nonlocal grid, current_shape, current_color, current_x, current_y, game_over, score
        grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        current_shape, current_color, current_x, current_y = new_tetromino()
        game_over = False
        score = 0

    reset_game()  # Start the game immediately

    while True:
        if game_over:
            draw_game_over_screen(score)
            while game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        reset_game()
                        break
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            if not game_over:
                # Move left
                if keys[pygame.K_LEFT]:
                    current_x -= GRID_SIZE
                    if check_collision(grid, current_shape, (current_x, current_y)):
                        current_x += GRID_SIZE

                # Move right
                if keys[pygame.K_RIGHT]:
                    current_x += GRID_SIZE
                    if check_collision(grid, current_shape, (current_x, current_y)):
                        current_x -= GRID_SIZE

                # Rotate
                if keys[pygame.K_UP]:
                    new_shape = rotate(current_shape)
                    if not check_collision(grid, new_shape, (current_x, current_y)):
                        current_shape = new_shape

                # Instant drop with Enter key
                if keys[pygame.K_RETURN]:
                    current_y = drop_tetromino(grid, current_shape, current_x, current_y)
                    pygame.time.wait(PAUSE_TIME)  # Small delay to prevent multiple drops in one key press

                # Move down automatically
                fall_time += clock.get_rawtime()
                if fall_time > FALL_TIME:
                    fall_time = 0
                    current_y += GRID_SIZE
                    if check_collision(grid, current_shape, (current_x, current_y)):
                        current_y -= GRID_SIZE
                        for y, row in enumerate(current_shape):
                            for x, cell in enumerate(row):
                                if cell:
                                    grid[current_y // GRID_SIZE + y][current_x // GRID_SIZE + x] = 1
                        score += clear_lines(grid)
                        current_shape, current_color, current_x, current_y = new_tetromino()
                        if check_collision(grid, current_shape, (current_x, current_y)):
                            game_over = True

            # Draw everything
            screen.fill(BACKGROUND_COLOR)
            draw_grid(screen)
            draw_tetromino(screen, current_shape, (current_x, current_y), current_color)
            for y, row in enumerate(grid):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(
                            screen,
                            GRID_COLOR,
                            (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE),
                            border_radius=5
                        )
            draw_text(f"Score: {score}", font, (255, 255, 255), screen, SCREEN_WIDTH // 2, FONT_SIZE // 2)
            pygame.display.flip()

            clock.tick(30)

if __name__ == "__main__":
    main_game_loop()
