import pygame

# Initialize Pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((300, 200))
pygame.display.set_caption('Toggle Button')

# Define colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Button state
button_on = False

# Button rectangle
button_rect = pygame.Rect(100, 75, 100, 50)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                button_on = not button_on  # Toggle button state

    # Fill the screen with white
    screen.fill(WHITE)

    # Draw button
    if button_on:
        pygame.draw.rect(screen, GREEN, button_rect)
        text = "ON"
    else:
        pygame.draw.rect(screen, RED, button_rect)
        text = "OFF"

    # Render text
    font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)

    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit()

