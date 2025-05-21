import pygame, sys, math
from typing import List, Dict, Any, Set, Optional
from utils import (
    has_arithmetic_progression,
    find_winning_progression,
    find_all_arithmetic_progressions,
    generate_random_subset_with_progression,
)
from algorithms import registry

BLACK: tuple[int, int, int] = (0, 0, 0)
WHITE: tuple[int, int, int] = (255, 255, 255)
PLAYER_COLOR: tuple[int, int, int] = (0, 0, 255)
COMPUTER_COLOR: tuple[int, int, int] = (255, 0, 0)


def draw_text_with_outline(
    screen: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    center: tuple[int, int],
    text_color: tuple[int, int, int] = WHITE,
    outline_color: tuple[int, int, int] = BLACK,
) -> None:
    txt = font.render(text, True, text_color)
    outline = font.render(text, True, outline_color)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                pos = (center[0] + dx, center[1] + dy)
                screen.blit(outline, outline.get_rect(center=pos))
    screen.blit(txt, txt.get_rect(center=center))


def show_all_progressions_screen(
    screen: pygame.Surface, font: pygame.font.Font, progressions: List[List[int]]
) -> None:
    clock = pygame.time.Clock()
    back_button = pygame.Rect(350, 530, 100, 40)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    running = False
        screen.fill((40, 40, 40))
        title = font.render("All Winning APs:", True, WHITE)
        screen.blit(title, (50, 20))
        y = 60
        for prog in progressions:
            d = prog[1] - prog[0] if len(prog) >= 2 else "N/A"
            prog_text = " ".join(str(n) for n in prog) + f" ; d = {d}"
            line = font.render(prog_text, True, WHITE)
            screen.blit(line, (50, y))
            y += 30
            if y > 500:
                break
        pygame.draw.rect(screen, (200, 0, 0), back_button)
        draw_text_with_outline(screen, "Back", font, back_button.center)
        pygame.display.flip()
        clock.tick(30)


def end_game_screen(
    screen: pygame.Surface,
    font: pygame.font.Font,
    winner: Optional[str],
    forced_prog: List[int],
    all_progs: List[List[int]],
    win_prog: Optional[List[int]],
) -> str:
    clock = pygame.time.Clock()
    play_button = pygame.Rect(150, 500, 120, 50)
    menu_button = pygame.Rect(330, 500, 120, 50)
    show_ap_button = pygame.Rect(510, 500, 220, 50)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    return "play_again"
                if menu_button.collidepoint(event.pos):
                    return "main_menu"
                if show_ap_button.collidepoint(event.pos):
                    show_all_progressions_screen(screen, font, all_progs)
        screen.fill((30, 30, 30))
        msg = f"{winner} wins!" if winner else "Draw!"
        draw_text_with_outline(screen, msg, font, (400, 80))
        if winner and win_prog:
            d_val = win_prog[1] - win_prog[0] if len(win_prog) >= 2 else "N/A"
            prog_str = (
                "Winning AP: " + " ".join(str(n) for n in win_prog) + f" ; d = {d_val}"
            )
            draw_text_with_outline(screen, prog_str, font, (400, 140))
        else:
            d_val = forced_prog[1] - forced_prog[0] if len(forced_prog) >= 2 else "N/A"
            prog_str = (
                "Forced AP: "
                + " ".join(str(n) for n in forced_prog)
                + f" ; d = {d_val}"
            )
            draw_text_with_outline(screen, prog_str, font, (400, 140))
        pygame.draw.rect(screen, (0, 200, 0), play_button)
        draw_text_with_outline(screen, "Play Again", font, play_button.center)
        pygame.draw.rect(screen, (0, 0, 200), menu_button)
        draw_text_with_outline(screen, "Main Menu", font, menu_button.center)
        pygame.draw.rect(screen, (200, 200, 0), show_ap_button)
        draw_text_with_outline(screen, "Show All APs", font, show_ap_button.center)
        turn_info = font.render("Game Over", True, WHITE)
        screen.blit(turn_info, (10, 10))
        pygame.display.flip()
        clock.tick(30)


class Game:
    def __init__(self, k, x, lower, bound):
        self.k: int = k
        self.x: int = x
        self.lower: int = lower
        self.bound: int = bound

        try:
            self.X, self.forced_prog = generate_random_subset_with_progression(
                k, x, lower, bound
            )
        except Exception as e:
            print("Error generating set:", e)

        self.all_possible: List[List[int]] = find_all_arithmetic_progressions(k, self.X)
        if not self.all_possible:
            print(
                "No arithmetic progression of length",
                k,
                "found with the given settings.",
            )

        self.player1_moves: List[int] = []
        self.player2_moves: List[int] = []

        self.game_over: bool = False
        self.winner: Optional[int] = None
        self.player1_turn: bool = True
        self.turn_count: int = 1
        self.winning_progression = None
        self.available_numbers: Set[int] = set(self.X)

    def make_move(self, value):
        player_moves = self.player1_moves if self.player1_turn else self.player2_moves
        player_moves.append(value)
        self.available_numbers.remove(value)

        player_moves_set = set(player_moves)
        for ap in self.all_possible:
            if set(ap).issubset(player_moves_set):
                self.winner = 1 if self.player1_turn else 2
                self.game_over = True
                self.winning_progression = ap
                return

        if not self.available_numbers:
            self.game_over = True
            return

        self.player1_turn = not self.player1_turn
        self.turn_count += 1


def run_game(settings: Dict[str, Any]) -> None:
    k: int = settings.get("k", 3)
    x: int = settings.get("x", 20)
    lower: int = settings.get("lower", 1)
    bound: int = settings.get("bound", 100)
    ai_choice: str = settings.get("algorithm", "random")
    # Retrieve the algorithm function that accepts four parameters.
    ai_algorithm = registry.get(ai_choice.lower(), registry.get("random"))
    game = Game(k, x, lower, bound)

    pygame.init()
    available_indices: Set[int] = set(range(x))
    screen_width: int = 800
    screen_height: int = 600
    screen: pygame.Surface = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Szemerédi's Game")
    clock = pygame.time.Clock()
    font: pygame.font.Font = pygame.font.Font(None, 24)
    left_margin: int = 20
    right_margin: int = 20
    top_margin: int = 80
    bottom_margin: int = 20
    cols: int = int(math.ceil(x**0.5))
    rows: int = int(math.ceil(x / cols))
    cell_width: float = (screen_width - left_margin - right_margin) / cols
    cell_height: float = (screen_height - top_margin - bottom_margin) / rows
    radius: int = int(min(cell_width, cell_height) / 2 * 0.8)
    cells: List[Dict[str, Any]] = []
    for index in range(x):
        row: int = index // cols
        col: int = index % cols
        cx: float = left_margin + col * cell_width + cell_width / 2
        cy: float = top_margin + row * cell_height + cell_height / 2
        rect: pygame.Rect = pygame.Rect(
            int(cx - radius), int(cy - radius), 2 * radius, 2 * radius
        )
        cell: Dict[str, Any] = {
            "value": game.X[index],
            "center": (int(cx), int(cy)),
            "rect": rect,
            "color": BLACK,
        }
        cells.append(cell)

    player_first: bool = settings.get("first", "player").lower() == "player"
    while not game.game_over:
        player_turn = game.player1_turn == player_first
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if player_turn and event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for i in available_indices.copy():
                    cell = cells[i]
                    if cell["rect"].collidepoint(pos):
                        cell["color"] = PLAYER_COLOR
                        available_indices.remove(i)
                        game.make_move(cell["value"])
                        break

            if not player_turn and not game.game_over:
                if available_indices:
                    if game.player1_turn:
                        computer_moves: List[int] = game.player1_moves
                        player_moves: List[int] = game.player2_moves
                    else:
                        computer_moves: List[int] = game.player2_moves
                        player_moves: List[int] = game.player1_moves

                    chosen_number: int = ai_algorithm(
                        list(game.available_numbers),
                        computer_moves,
                        player_moves,
                        game.k,
                    )
                    chosen_index: Optional[int] = None
                    for idx in available_indices:
                        if cells[idx]["value"] == chosen_number:
                            chosen_index = idx
                            break
                    if chosen_index is None:
                        chosen_index = available_indices.pop()
                    else:
                        available_indices.remove(chosen_index)
                    cell = cells[chosen_index]
                    cell["color"] = COMPUTER_COLOR
                    game.make_move(chosen_number)

        screen.fill(WHITE)
        for cell in cells:
            pygame.draw.circle(screen, cell["color"], cell["center"], radius)
            pygame.draw.circle(screen, BLACK, cell["center"], radius, 2)
            draw_text_with_outline(screen, str(cell["value"]), font, cell["center"])

        winner = "Player" if player_turn else "Computer"
        turn_text: str = f"Turn: {winner}"
        count_text: str = f"Turn Number: {game.turn_count}"
        turn_surf = font.render(turn_text, True, BLACK)
        count_surf = font.render(count_text, True, BLACK)
        screen.blit(turn_surf, (10, 10))
        screen.blit(count_surf, (10, 40))
        pygame.display.flip()
        clock.tick(30)

    win_prog = game.winning_progression

    if game.forced_prog in game.all_possible:
        game.all_possible.remove(game.forced_prog)

    result: str = end_game_screen(
        screen, font, winner, game.forced_prog, game.all_possible, win_prog
    )
    pygame.quit()
    if result == "play_again":
        run_game(settings)
    else:
        return
