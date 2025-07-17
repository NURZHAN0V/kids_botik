def игра_дино():
    import pygame
    import random

    # Инициализация
    pygame.init()
    WIDTH, HEIGHT = 800, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dino Game")
    clock = pygame.time.Clock()

    # Цвета
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # Параметры динозавра
    dino_rect = pygame.Rect(50, HEIGHT - 60, 40, 60)
    gravity = 0.8
    jump_speed = -15
    velocity_y = 0
    on_ground = True

    # Кактусы
    cactus_list = []
    SPAWN_CACTUS = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_CACTUS, 1500)  # Как часто появляются кактусы

    # Счёт
    score = 0
    font = pygame.font.SysFont(None, 36)

    # Основной цикл игры
    running = True
    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == SPAWN_CACTUS:
                cactus_width = random.randint(20, 40)
                cactus_height = 50
                cactus_rect = pygame.Rect(WIDTH, HEIGHT - cactus_height, cactus_width, cactus_height)
                cactus_list.append(cactus_rect)

        # Управление прыжком
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and on_ground:
            velocity_y = jump_speed
            on_ground = False

        # Обновление позиции динозавра
        velocity_y += gravity
        dino_rect.y += velocity_y
        if dino_rect.y >= HEIGHT - 60:
            dino_rect.y = HEIGHT - 60
            velocity_y = 0
            on_ground = True

        # Рисуем динозавра
        pygame.draw.rect(screen, BLACK, dino_rect)

        # Обновляем кактусы
        for cactus in cactus_list:
            cactus.x -= 5
            pygame.draw.rect(screen, BLACK, cactus)

        # Удаляем кактусы за экраном
        cactus_list = [c for c in cactus_list if c.x > -40]

        # Проверка столкновений
        for cactus in cactus_list:
            if dino_rect.colliderect(cactus):
                print("Game Over! Score:", score)
                running = False

        # Обновление счёта
        score += 1
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()