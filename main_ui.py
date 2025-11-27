import pygame
import sys
import time
from sb3_contrib import MaskablePPO
from env import Env

WIDTH, HEIGHT = 900, 800
BG_COLOR = (0, 100, 0)
CARD_COLOR = (255, 0, 0)
CARD_BACK_COLOR = (0, 0, 255)
TEXT_COLOR = (255, 255, 255)
CARD_WIDTH, CARD_HEIGHT = 60,80
SPACING = 20

def draw_card(screen, font, card, x, y):
    rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

    if card.face_up:
        pygame.draw.rect(screen, (255,255,255), rect, border_radius=5)
        pygame.draw.rect(screen, (0,0,0), rect, 2, border_radius=5)

        color = (0, 0, 0)
        if hasattr(card, 'suit'):
            if card.suit in [1, 2]:
                color = (255, 0, 0)
            else:
                color = (0, 0, 0)

        rank_str = str(card.rank)
        if card.rank == 1: rank_str = "A"
        if card.rank == 11: rank_str = "J"
        if card.rank == 12: rank_str = "Q"
        if card.rank == 13: rank_str = "K"

        text = font.render(rank_str, True, color)
        screen.blit(text, (x + 5, y + 5))

    else:
        pygame.draw.rect(screen, (0, 0, 150), rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=5)

        pattern_rect = pygame.Rect(x + 5, y + 5, CARD_WIDTH - 10, CARD_HEIGHT - 10)
        pygame.draw.rect(screen, (0, 0, 100), pattern_rect, border_radius=3)

def draw_game(screen, font, env):

    screen.fill(BG_COLOR)

    available_width = WIDTH - 2 * SPACING
    total_cards_width = 10 * CARD_WIDTH
    total_spacing = available_width - total_cards_width
    spacing_between = total_spacing / (10 - 1) if 10 > 1 else 0

    for i, col in enumerate(env.game.columns):
        x = SPACING + i * (CARD_WIDTH + spacing_between)
        y = SPACING + 80

        max_cards_visible = min(len(col), 15)
        start_index = max(0, len(col) - max_cards_visible)

        pygame.draw.rect(screen, (0, 100, 0), (x, y, CARD_WIDTH, CARD_HEIGHT), 2)

        for card_idx, card in enumerate(col[start_index:], start=start_index):
            draw_card(screen, font, card, x, y + card_idx * 25)

    stock_len = len(env.game.stock)
    stock_text = font.render(f"{stock_len}", True, TEXT_COLOR)
    screen.blit(stock_text, (WIDTH - 150, HEIGHT - 50))

    found_text = font.render(f"Completed: {env.game.foundation_count}", True, TEXT_COLOR)
    screen.blit(found_text, (20, HEIGHT - 50))

    instr = font.render("SPACE: Step | ENTER: Auto-Play | Q: Quit", True, TEXT_COLOR)
    screen.blit(instr, (20, 10))

    pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Spider Solitaire")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 16)
    title_font = pygame.font.SysFont("arial", 24, bold=True)

    env = Env(render_mode='console')

    try:
        model = MaskablePPO.load("spider_solitaire_ppo")
    except FileNotFoundError:
        sys.exit("No model")

    obs, _ = env.reset()
    running = True
    auto_play = False
    game_over = False

    while running:
        screen.fill(BG_COLOR)

        title = title_font.render("Spider Solitaire", True, TEXT_COLOR)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))

        info_text = font.render(f"Stock: {len(env.game.stock)} | Completed: {env.game.foundation_count}/8", True,
                                TEXT_COLOR)
        screen.blit(info_text, (20, 50))

        if auto_play:
            auto_text = font.render("AUTO-PLAY MODE - Press ENTER to stop", True, (255, 255, 0))
            screen.blit(auto_text, (WIDTH // 2 - auto_text.get_width() // 2, HEIGHT - 30))

        for i, col in enumerate(env.game.columns):
            x = SPACING + i * (CARD_WIDTH + SPACING)
            y = SPACING + 80

            for card_idx, card in enumerate(col):
                draw_card(screen, font, card, x, y + card_idx * 25)

        instr = font.render("SPACE: Step | ENTER: Auto-Play | R: Reset | Q: Quit", True, TEXT_COLOR)
        screen.blit(instr, (20, HEIGHT - 60))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_r:
                    obs, _ = env.reset()
                    game_over = False
                    auto_play = False
                elif event.key == pygame.K_SPACE and not auto_play and not game_over:
                    if model:
                        action_masks = env.action_masks()
                        if any(action_masks):
                            action, _ = model.predict(obs, action_masks=action_masks, deterministic=True)
                            obs, reward, terminated, _, _ = env.step(action.item())
                            if terminated:
                                game_over = True
                                print("Game Won!")
                        else:
                            print("No legal moves available!")
                            game_over = True
                elif event.key == pygame.K_RETURN:
                    auto_play = not auto_play

        if auto_play and not game_over and model:
            action_masks = env.action_masks()
            if any(action_masks):
                action, _ = model.predict(obs, action_masks=action_masks, deterministic=True)
                obs, reward, terminated, _, _ = env.step(action.item())
                if terminated:
                    game_over = True
                    print("Game Won!")
                    auto_play = False
            else:
                print("No legal moves available!")
                game_over = True
                auto_play = False

            time.sleep(0.5)

        clock.tick(10 if auto_play else 30)

    pygame.quit()


if __name__ == "__main__":
    main()
