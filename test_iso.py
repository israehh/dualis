import pygame

pygame.init()

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("DUALIS - Test Isométrico")

clock = pygame.time.Clock()

running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()