import pygame
import sys
import math
import random

pygame.init()

screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Crystal Defense")

WHITE = (255, 255, 255)
BLUE = (0, 150, 255)
RED = (255, 50, 50)
DARKRED = (150, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 100)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

clock = pygame.time.Clock()
font = pygame.font.SysFont("malgungothic", 24)
big_font = pygame.font.SysFont("malgungothic", 48)

def reset_game():
    return {
        "player": [300, 400],
        "level": 1,
        "xp": 0,
        "xp_need": 3 + (1 - 1) * 7,  # ✅ 초기 필요 경험치
        "enemies": [],
        "bullets": [],
        "xps": [],
        "crystal_hits": 0,
        "last_shot": 0,
        "shoot_delay": 900,
        "bullet_damage": 3,
        "game_over": False,
        "level_up": False,
        "wave_time": 0,
        "area_attack": False,
        "area_damage": 1,
        "area_timer": 0
    }

game = reset_game()

def spawn_enemy():
    side = random.choice(["top", "bottom", "left", "right"])
    if game["level"] >= 3 and random.random() < 0.2:
        hp = 20
        color = DARKRED
    else:
        hp = 3
        color = RED
    if side == "top":
        return [random.randint(0, 600), 0, hp, color]
    elif side == "bottom":
        return [random.randint(0, 600), 600, hp, color]
    elif side == "left":
        return [0, random.randint(0, 600), hp, color]
    else:
        return [600, random.randint(0, 600), hp, color]

running = True
start_ticks = pygame.time.get_ticks()

while running:
    dt = clock.tick(60)
    current_time = pygame.time.get_ticks()
    elapsed_sec = (current_time - start_ticks) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game["game_over"] and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if 200 < mx < 400 and 300 < my < 350:
                game = reset_game()
                start_ticks = pygame.time.get_ticks()
            if 200 < mx < 400 and 360 < my < 410:
                running = False

        if game["level_up"] and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if 150 < mx < 450:
                if 200 < my < 250:
                    game["shoot_delay"] = max(100, game["shoot_delay"] // 2)
                elif 270 < my < 320:
                    game["bullet_damage"] += 1
                elif 340 < my < 390:
                    game["area_attack"] = True
                game["level_up"] = False

    if not game["game_over"] and not game["level_up"]:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            game["player"][0] -= 5
        if keys[pygame.K_RIGHT]:
            game["player"][0] += 5
        if keys[pygame.K_UP]:
            game["player"][1] -= 5
        if keys[pygame.K_DOWN]:
            game["player"][1] += 5

        if current_time - game["last_shot"] > game["shoot_delay"]:
            mx, my = pygame.mouse.get_pos()
            px, py = game["player"]
            angle = math.atan2(my - py, mx - px)
            dx = math.cos(angle) * 17.5
            dy = math.sin(angle) * 17.5
            # ✅ 총알 크기 반영은 그릴 때 적용
            game["bullets"].append([px, py, dx, dy])
            game["last_shot"] = current_time

        base_spawn = 0.01
        level_factor = 0.01
        spawn_prob = min(base_spawn + game["level"] * level_factor + elapsed_sec * 0.001, 0.08)
        if random.random() < spawn_prob:
            game["enemies"].append(spawn_enemy())

        for e in game["enemies"]:
            angle = math.atan2(300 - e[1], 300 - e[0])
            speed = 1.1 if e[2] <= 3 else 0.5
            e[0] += math.cos(angle) * speed
            e[1] += math.sin(angle) * speed

        for b in game["bullets"]:
            b[0] += b[2]
            b[1] += b[3]

        for b in game["bullets"][:]:
            for e in game["enemies"][:]:
                if math.hypot(b[0]-e[0], b[1]-e[1]) < 15:
                    e[2] -= game["bullet_damage"]
                    if e[2] <= 0:
                        game["enemies"].remove(e)
                        game["xps"].append([e[0], e[1]])
                    if b in game["bullets"]:
                        game["bullets"].remove(b)
                    break

        if game["area_attack"] and current_time - game["area_timer"] > 500:
            px, py = game["player"]
            for e in game["enemies"][:]:
                if math.hypot(px-e[0], py-e[1]) < 50:
                    e[2] -= game["area_damage"]
                    if e[2] <= 0:
                        game["enemies"].remove(e)
                        game["xps"].append([e[0], e[1]])
            game["area_timer"] = current_time

        px, py = game["player"]
        for xp in game["xps"][:]:
            dist = math.hypot(px-xp[0], py-xp[1])
            if dist < 25:
                xp[0] += (px - xp[0]) * 0.2
                xp[1] += (py - xp[1]) * 0.2
            if dist < 10:
                game["xps"].remove(xp)
                game["xp"] += 1
                if game["area_attack"]:
                    game["area_damage"] += 1

        if game["xp"] >= game["xp_need"]:
            game["xp"] = 0
            game["level"] += 1
            game["xp_need"] = 3 + (game["level"] - 1) * 7
            game["level_up"] = True

        for e in game["enemies"][:]:
            if math.hypot(e[0]-300, e[1]-300) < 20:
                game["enemies"].remove(e)
                game["crystal_hits"] += 1
        if game["crystal_hits"] >= 10:
            game["game_over"] = True

    screen.fill(WHITE)
    pygame.draw.circle(screen, GREEN, (300, 300), 20)

    px, py = game["player"]
    pygame.draw.circle(screen, BLUE, (int(px), int(py)), 15)
    screen.blit(font.render(f"Lv.{game['level']}", True, BLACK), (px-20, py-35))

    for e in game["enemies"]:
        color = e[3]
        pygame.draw.circle(screen, color, (int(e[0]), int(e[1])), 10 if e[2]<=3 else 15)

    # ✅ 총알 크기 1.8배
    for b in game["bullets"]:
        pygame.draw.circle(screen, BLACK, (int(b[0]), int(b[1])), int(5*1.8))

    for xp in game["xps"]:
        pygame.draw.circle(screen, YELLOW, (int(xp[0]), int(xp[1])), 5)

    screen.blit(font.render(f"경험치: {game['xp']}/{game['xp_need']}", True, BLACK), (10, 10))
    screen.blit(font.render(f"크리스탈: {game['crystal_hits']}/10", True, BLACK), (10, 30))
    if game["area_attack"]:
        screen.blit(font.render(f"근접피해: {game['area_damage']}", True, ORANGE), (10, 50))

    if game["game_over"]:
        screen.blit(big_font.render("당신은 실패한!!!", True, RED), (130, 200))
        pygame.draw.rect(screen, BLACK, (200, 300, 200, 50))
        pygame.draw.rect(screen, BLACK, (200, 360, 200, 50))
        screen.blit(font.render("다시하기", True, WHITE), (250, 315))
        screen.blit(font.render("종료하기", True, WHITE), (250, 375))

    if game["level_up"]:
        pygame.draw.rect(screen, BLACK, (100, 150, 400, 300))
        screen.blit(font.render("무기 선택!", True, WHITE), (240, 170))
        screen.blit(font.render("1. 공격속도 증가", True, WHITE), (150, 210))
        screen.blit(font.render("2. 데미지 증가", True, WHITE), (150, 280))
        screen.blit(font.render("3. 주변 공격 추가", True, WHITE), (150, 350))

    pygame.display.flip()

pygame.quit()
sys.exit()