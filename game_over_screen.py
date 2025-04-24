import pygame
import sys

def game_over_screen(screen, title_font, message):
    clock = pygame.time.Clock()
    WIDTH, HEIGHT = screen.get_size()

    button_width, button_height = 200, 50
    restart_rect = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 + 50, button_width, button_height)
    quit_rect    = pygame.Rect(WIDTH//2 +  20, HEIGHT//2 + 50, button_width, button_height)

    while True:
        screen.fill((0, 0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((30, 30, 30))
        screen.blit(overlay, (0, 0))

        text = title_font.render(message, True, (255, 255, 255))
        screen.blit(text, (WIDTH//2 - text.get_width()//2,
                           HEIGHT//2 - 100))

        pygame.draw.rect(screen, (70, 130, 180), restart_rect)
        pygame.draw.rect(screen, (178, 34,  34), quit_rect)

        restart_text = title_font.render("Restart", True, (255, 255, 255))
        quit_text    = title_font.render("Quit",    True, (255, 255, 255))
        screen.blit(restart_text, (restart_rect.centerx - restart_text.get_width()//2,
                                   restart_rect.centery - restart_text.get_height()//2))
        screen.blit(quit_text,    (quit_rect.centerx    - quit_text.get_width()//2,
                                   quit_rect.centery    - quit_text.get_height()//2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_rect.collidepoint(event.pos):
                    return 'restart'
                elif quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        clock.tick(30)
