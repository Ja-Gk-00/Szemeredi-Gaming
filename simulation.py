# simulation.py

import os
import sys
import json
import argparse
import pygame
import math
from game import Game  # Game.__init__(self, k, x, lower, bound)
from utils import find_all_arithmetic_progressions

# Colors (should match your game.py constants)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PLAYER_COLOR = (70, 130, 180)  # steelblue
COMPUTER_COLOR = (178, 34, 34)  # firebrick
MOVE_TEXT_COLOR = (255, 215, 0)  # gold


def run_simulation(moves_file: str, delay: float = 1.0):
    """
    Load a saved game from JSON (including the original grid)
    and replay it in a Pygame window with smooth timing.
    """
    # Load saved game data
    if not os.path.isfile(moves_file):
        print(f"Moves file not found: {moves_file}")
        sys.exit(1)
    with open(moves_file, "r") as f:
        data = json.load(f)

    settings = data["settings"]
    original_grid = data["grid"]  # full list of numbers in grid order
    moves = data["moves"]
    first_algo = data.get("first_player", "First")
    second_algo = data.get("second_player", "Second")
    game_id = data.get("game_id", 0)

    # Initialize game logic (for validation) and then override grid
    k, x, lower, bound = (
        settings["k"],
        settings["x"],
        settings["lower"],
        settings["bound"],
    )
    game = Game(k, x, lower, bound)
    game.X = original_grid
    game.available_numbers = set(original_grid)
    game.player1_moves = []
    game.player2_moves = []
    game.winner = None

    # Pygame setup
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Replay Game #{game_id}: {first_algo} vs {second_algo}")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    large_font = pygame.font.Font(None, 36)

    # Compute grid layout
    left, right, top, bottom = 20, 20, 80, 20
    cols = int(math.ceil(x**0.5))
    rows = int(math.ceil(x / cols))
    cw = (WIDTH - left - right) / cols
    ch = (HEIGHT - top - bottom) / rows
    radius = int(min(cw, ch) / 2 * 0.8)

    # Build visual cells list
    cells = []
    for idx, value in enumerate(original_grid):
        row = idx // cols
        col = idx % cols
        cx = left + col * cw + cw / 2
        cy = top + row * ch + ch / 2
        cells.append({"value": value, "center": (int(cx), int(cy)), "color": BLACK})

    # Timing control
    next_move_time = pygame.time.get_ticks() + int(delay * 1000)
    move_idx = 0
    running = True
    finished = False

    while running:
        now = pygame.time.get_ticks()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

        # Play next move at scheduled time
        if not finished and move_idx < len(moves) and now >= next_move_time:
            move = moves[move_idx]
            # Mark in UI and apply to game logic
            for cell in cells:
                if cell["value"] == move and cell["color"] == BLACK:
                    color = PLAYER_COLOR if (move_idx % 2 == 0) else COMPUTER_COLOR
                    cell["color"] = color
                    game.make_move(move)
                    break
            move_idx += 1
            next_move_time += int(delay * 1000)
            if move_idx >= len(moves):
                finished = True
                finish_time = now + 500  # wait 0.5s before showing result

        # Draw board
        screen.fill((30, 30, 30))
        # Render game settings at top-left
        settings_text = f"Settings: k={k}, x={x}, lower={lower}, bound={bound}"
        settings_surf = font.render(settings_text, True, WHITE)
        screen.blit(settings_surf, (20, 20))
        for cell in cells:
            pygame.draw.circle(screen, cell["color"], cell["center"], radius)
            txt = font.render(str(cell["value"]), True, WHITE)
            screen.blit(txt, txt.get_rect(center=cell["center"]))

        # After all moves played, show result & moves lists
        if finished and now >= finish_time:
            # Determine winner text
            if game.winner == 1:
                result_text = f"{first_algo} wins!"
            elif game.winner == 2:
                result_text = f"{second_algo} wins!"
            else:
                result_text = "Draw!"
            # Render result
            result_surf = large_font.render(result_text, True, WHITE)
            screen.blit(result_surf, result_surf.get_rect(center=(WIDTH // 2, 30)))

            # Render each player's move sequence
            first_moves = moves[0::2]
            second_moves = moves[1::2]
            first_s = f"{first_algo} moves:  " + ", ".join(map(str, first_moves))
            second_s = f"{second_algo} moves: " + ", ".join(map(str, second_moves))
            first_surf = font.render(first_s, True, MOVE_TEXT_COLOR)
            second_surf = font.render(second_s, True, MOVE_TEXT_COLOR)
            screen.blit(first_surf, (20, HEIGHT - 60))
            screen.blit(second_surf, (20, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Replay a saved Szemerédi's Game from moves JSON."
    )
    parser.add_argument(
        "--moves",
        required=True,
        help="Path to the .json file with saved moves (including grid).",
    )
    parser.add_argument(
        "--delay", type=float, default=1.0, help="Seconds between move animations."
    )
    args = parser.parse_args()

    run_simulation(args.moves, delay=args.delay)
