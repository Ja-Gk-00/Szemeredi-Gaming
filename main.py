import os
import sys
import subprocess
import pygame
from algorithms import registry

CONFIG_DIR = "experiments_configs"
MOVES_DIR = "saved_runs_moves"


def settings_screen() -> dict:
    pygame.init()
    screen = pygame.display.set_mode((1000, 650))
    pygame.display.set_caption("Szemerédi's Game – Settings, Experiments & Replay")
    font = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()

    # — Core game settings inputs —
    algo_names = list(registry.keys()) or ["random"]
    input_boxes = {
        "k": {"rect": pygame.Rect(300, 100, 140, 32), "text": "3"},
        "x": {"rect": pygame.Rect(300, 150, 140, 32), "text": "20"},
        "lower": {"rect": pygame.Rect(300, 200, 140, 32), "text": "1"},
        "bound": {"rect": pygame.Rect(300, 250, 140, 32), "text": "100"},
    }
    algo_box = {
        "rect": pygame.Rect(300, 300, 140, 32),
        "selected": algo_names[0],
        "options": algo_names,
        "open": False,
        "scroll_offset": 0,
    }
    first_box = {
        "rect": pygame.Rect(300, 380, 140, 32),
        "selected": "player",
        "options": ["player", "computer"],
        "open": False,
    }

    # — Experiments config dropdown & button —
    configs = [f for f in os.listdir(CONFIG_DIR) if f.endswith(".json")]
    run_exp_button = pygame.Rect(550, 300, 200, 50)
    config_box = {
        "rect": pygame.Rect(run_exp_button.right + 20, run_exp_button.y + 10, 200, 32),
        "selected": configs[0] if configs else "",
        "options": configs,
        "open": False,
        "scroll_offset": 0,
    }

    # — Simulation dropdown & Play Simulation button —
    sims = [f for f in os.listdir(MOVES_DIR) if f.endswith(".json")]
    sim_box = {
        "rect": pygame.Rect(550, run_exp_button.y - 140, 200, 32),
        "selected": sims[0] if sims else "",
        "options": sims,
        "open": False,
        "scroll_offset": 0,
    }
    play_sim_button = pygame.Rect(550, run_exp_button.y - 90, 200, 50)

    start_button = pygame.Rect(250, 450, 120, 50)
    exit_button = pygame.Rect(430, 450, 120, 50)

    active_box = None
    color_inactive = pygame.Color("lightskyblue3")
    color_active = pygame.Color("dodgerblue2")
    error_msg = ""
    error_timer = 0

    visible_count = 5
    option_h = 32

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # 1) Numeric inputs
                for key, box in input_boxes.items():
                    if box["rect"].collidepoint(event.pos):
                        active_box = key
                        algo_box["open"] = first_box["open"] = config_box["open"] = (
                            sim_box["open"]
                        ) = False
                        break
                else:
                    # 2) Dropdown toggles / selection
                    if algo_box["rect"].collidepoint(event.pos):
                        algo_box["open"] = not algo_box["open"]
                    elif first_box["rect"].collidepoint(event.pos):
                        first_box["open"] = not first_box["open"]
                    elif config_box["rect"].collidepoint(event.pos):
                        config_box["open"] = not config_box["open"]
                    elif sim_box["rect"].collidepoint(event.pos):
                        sim_box["open"] = not sim_box["open"]
                    elif (
                        algo_box["open"]
                        or first_box["open"]
                        or config_box["open"]
                        or sim_box["open"]
                    ):
                        # first_box
                        if first_box["open"]:
                            for i, opt in enumerate(first_box["options"]):
                                r = pygame.Rect(
                                    first_box["rect"].x,
                                    first_box["rect"].y
                                    + first_box["rect"].h
                                    + i * option_h,
                                    first_box["rect"].w,
                                    option_h,
                                )
                                if r.collidepoint(event.pos):
                                    first_box["selected"] = opt
                                    first_box["open"] = False
                                    break
                        # algo_box
                        if algo_box["open"]:
                            for i, opt in enumerate(algo_box["options"]):
                                r = pygame.Rect(
                                    algo_box["rect"].x,
                                    algo_box["rect"].y
                                    + algo_box["rect"].h
                                    + i * option_h
                                    - algo_box["scroll_offset"],
                                    algo_box["rect"].w,
                                    option_h,
                                )
                                if r.collidepoint(event.pos):
                                    algo_box["selected"] = opt
                                    algo_box["open"] = False
                                    break
                        # config_box
                        if config_box["open"]:
                            for i, opt in enumerate(config_box["options"]):
                                r = pygame.Rect(
                                    config_box["rect"].x,
                                    config_box["rect"].y
                                    + config_box["rect"].h
                                    + i * option_h
                                    - config_box["scroll_offset"],
                                    config_box["rect"].w,
                                    option_h,
                                )
                                if r.collidepoint(event.pos):
                                    config_box["selected"] = opt
                                    config_box["open"] = False
                                    break
                        # sim_box
                        if sim_box["open"]:
                            for i, opt in enumerate(sim_box["options"]):
                                r = pygame.Rect(
                                    sim_box["rect"].x,
                                    sim_box["rect"].y
                                    + sim_box["rect"].h
                                    + i * option_h
                                    - sim_box["scroll_offset"],
                                    sim_box["rect"].w,
                                    option_h,
                                )
                                if r.collidepoint(event.pos):
                                    sim_box["selected"] = opt
                                    sim_box["open"] = False
                                    break
                    # 3) Buttons
                    elif start_button.collidepoint(event.pos) and event.button == 1:
                        try:
                            k_ = int(input_boxes["k"]["text"])
                            x_ = int(input_boxes["x"]["text"])
                            lo = int(input_boxes["lower"]["text"])
                            bo = int(input_boxes["bound"]["text"])
                            if lo > bo or k_ <= 0 or x_ < k_ or x_ > (bo - lo + 1):
                                raise ValueError
                            running = False
                        except:
                            error_msg = "Invalid input: resetting to defaults."
                            error_timer = pygame.time.get_ticks()
                            input_boxes["k"]["text"] = "3"
                            input_boxes["x"]["text"] = "20"
                            input_boxes["lower"]["text"] = "1"
                            input_boxes["bound"]["text"] = "100"
                            algo_box["selected"] = algo_names[0]
                            first_box["selected"] = "player"
                    elif exit_button.collidepoint(event.pos) and event.button == 1:
                        pygame.quit()
                        sys.exit()
                    elif event.button == 1 and run_exp_button.collidepoint(event.pos):
                        if not config_box["selected"]:
                            error_msg = "No config selected!"
                            error_timer = pygame.time.get_ticks()
                        else:
                            cfg_path = os.path.join(CONFIG_DIR, config_box["selected"])
                            subprocess.Popen(
                                [
                                    sys.executable,
                                    "-u",
                                    "benchmark.py",
                                    "--config",
                                    cfg_path,
                                ],
                                close_fds=True,
                            )
                    elif event.button == 1 and play_sim_button.collidepoint(event.pos):
                        if sim_box["selected"]:
                            sim_path = os.path.join(MOVES_DIR, sim_box["selected"])
                            subprocess.Popen(
                                [
                                    sys.executable,
                                    "-u",
                                    "simulation.py",
                                    "--moves",
                                    sim_path,
                                ]
                            )
                        # else do nothing

            if event.type == pygame.MOUSEWHEEL:
                for db in (algo_box, config_box, sim_box):
                    if db["open"]:
                        max_off = max(
                            0, len(db["options"]) * option_h - visible_count * option_h
                        )
                        db["scroll_offset"] = max(
                            0, min(max_off, db["scroll_offset"] - event.y * option_h)
                        )

            if event.type == pygame.KEYDOWN and active_box:
                if event.key == pygame.K_RETURN:
                    active_box = None
                elif event.key == pygame.K_BACKSPACE:
                    input_boxes[active_box]["text"] = input_boxes[active_box]["text"][
                        :-1
                    ]
                else:
                    input_boxes[active_box]["text"] += event.unicode

        # — Rendering —
        screen.fill((30, 30, 30))

        # Numeric inputs
        for key, box in input_boxes.items():
            txt_surf = font.render(box["text"], True, (255, 255, 255))
            box["rect"].w = max(140, txt_surf.get_width() + 10)
            col = color_active if active_box == key else color_inactive
            pygame.draw.rect(screen, col, box["rect"], 2)
            screen.blit(txt_surf, (box["rect"].x + 5, box["rect"].y + 5))
            lbl = font.render(key, True, (255, 255, 255))
            screen.blit(lbl, (box["rect"].x - 150, box["rect"].y + 5))

        # Algorithm & first dropdowns
        for label, db in [("algorithm", algo_box), ("first", first_box)]:
            pygame.draw.rect(screen, color_inactive, db["rect"], 2)
            screen.blit(
                font.render(db["selected"], True, (255, 255, 255)),
                (db["rect"].x + 5, db["rect"].y + 5),
            )
            screen.blit(
                font.render(label, True, (255, 255, 255)),
                (db["rect"].x - 150, db["rect"].y + 5),
            )
            if db["open"]:
                for i, opt in enumerate(db["options"]):
                    r = pygame.Rect(
                        db["rect"].x,
                        db["rect"].y
                        + db["rect"].h
                        + i * option_h
                        - db.get("scroll_offset", 0),
                        db["rect"].w,
                        option_h,
                    )
                    pygame.draw.rect(screen, (50, 50, 50), r)
                    pygame.draw.rect(screen, color_inactive, r, 2)
                    screen.blit(
                        font.render(opt, True, (255, 255, 255)), (r.x + 5, r.y + 5)
                    )

        # Simulation label & dropdown
        sim_label_pos = (sim_box["rect"].x, sim_box["rect"].y - 30)
        screen.blit(
            font.render("choose saved game", True, (255, 255, 255)), sim_label_pos
        )
        pygame.draw.rect(screen, color_inactive, sim_box["rect"], 2)
        screen.blit(
            font.render(sim_box["selected"], True, (255, 255, 255)),
            (sim_box["rect"].x + 5, sim_box["rect"].y + 5),
        )
        if sim_box["open"]:
            for i, opt in enumerate(sim_box["options"]):
                r = pygame.Rect(
                    sim_box["rect"].x,
                    sim_box["rect"].y
                    + sim_box["rect"].h
                    + i * option_h
                    - sim_box["scroll_offset"],
                    sim_box["rect"].w,
                    option_h,
                )
                pygame.draw.rect(screen, (50, 50, 50), r)
                pygame.draw.rect(screen, color_inactive, r, 2)
                screen.blit(font.render(opt, True, (255, 255, 255)), (r.x + 5, r.y + 5))

        # Play Simulation button
        pygame.draw.rect(screen, (100, 150, 0), play_sim_button)
        screen.blit(
            font.render("Play Simulation", True, (255, 255, 255)),
            font.render("Play Simulation", True, (255, 255, 255)).get_rect(
                center=play_sim_button.center
            ),
        )

        # Config label & dropdown
        pygame.draw.rect(screen, color_inactive, config_box["rect"], 2)
        screen.blit(
            font.render(config_box["selected"], True, (255, 255, 255)),
            (config_box["rect"].x + 5, config_box["rect"].y + 5),
        )
        if config_box["open"]:
            for i, opt in enumerate(config_box["options"]):
                r = pygame.Rect(
                    config_box["rect"].x,
                    config_box["rect"].y
                    + config_box["rect"].h
                    + i * option_h
                    - config_box["scroll_offset"],
                    config_box["rect"].w,
                    option_h,
                )
                pygame.draw.rect(screen, (50, 50, 50), r)
                pygame.draw.rect(screen, color_inactive, r, 2)
                screen.blit(font.render(opt, True, (255, 255, 255)), (r.x + 5, r.y + 5))

        # Experiments button
        pygame.draw.rect(screen, (0, 120, 200), run_exp_button)
        screen.blit(
            font.render("Run Experiments", True, (255, 255, 255)),
            font.render("Run Experiments", True, (255, 255, 255)).get_rect(
                center=run_exp_button.center
            ),
        )

        # Core Start/Exit buttons
        pygame.draw.rect(screen, (0, 200, 0), start_button)
        screen.blit(
            font.render("Start Game", True, (255, 255, 255)),
            font.render("Start Game", True, (255, 255, 255)).get_rect(
                center=start_button.center
            ),
        )
        pygame.draw.rect(screen, (200, 0, 0), exit_button)
        screen.blit(
            font.render("Exit Game", True, (255, 255, 255)),
            font.render("Exit Game", True, (255, 255, 255)).get_rect(
                center=exit_button.center
            ),
        )

        # Error message
        if error_msg:
            screen.blit(
                font.render(error_msg, True, (255, 0, 0)),
                (sim_box["rect"].x, sim_box["rect"].bottom + 10),
            )
            if pygame.time.get_ticks() - error_timer > 3000:
                error_msg = ""

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    return {
        "k": int(input_boxes["k"]["text"]),
        "x": int(input_boxes["x"]["text"]),
        "lower": int(input_boxes["lower"]["text"]),
        "bound": int(input_boxes["bound"]["text"]),
        "algorithm": algo_box["selected"].lower(),
        "first": first_box["selected"].lower(),
    }


if __name__ == "__main__":
    while True:
        settings = settings_screen()
        from game import run_game

        run_game(settings)
