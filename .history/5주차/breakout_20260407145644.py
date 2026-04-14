import pygame
import sys

pygame.init()

def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0:
            return font
    return pygame.font.SysFont(None, size)

def format_time(ms):
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    centiseconds = (ms % 1000) // 10
    return f"{minutes:02}:{seconds:02}.{centiseconds:02}"

# 설정값
WIDTH, HEIGHT = 800, 600
FPS = 60

# 색상
WHITE, BLACK, GRAY = (255, 255, 255), (0, 0, 0), (40, 40, 40)
BLUE, RED, YELLOW, ORANGE, GREEN = (50, 120, 220), (220, 50, 50), (240, 200, 0), (240, 140, 0), (50, 200, 50)
BLOCK_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("벽돌 깨기 - 물리 엔진 최적화")
clock = pygame.time.Clock()
font = get_korean_font(30)
font_small = get_korean_font(16)
font_big = get_korean_font(60)

# 레벨 설정
LEVELS = [
    {"rows": 3, "label": "레벨 1"},
    {"rows": 5, "label": "레벨 2"},
    {"rows": 7, "label": "레벨 3"},
]

PAD_W, PAD_H = 120, 15
BALL_R_DEFAULT = 8
BLOCK_COLS = 10
BLOCK_MARGIN = 4
BLOCK_TOP = 80
# [수정] 화면 너비에 맞춰 블록 너비 자동 계산 (빈 공간 제거)
BLOCK_W = (WIDTH - (BLOCK_MARGIN * (BLOCK_COLS + 1))) // BLOCK_COLS
BLOCK_H = 25

def make_blocks(rows):
    blocks = []
    for r in range(rows):
        hp_value = 1 + (rows - 1 - r) // 2
        for c in range(BLOCK_COLS):
            x = BLOCK_MARGIN + c * (BLOCK_W + BLOCK_MARGIN)
            y = BLOCK_TOP + r * (BLOCK_H + BLOCK_MARGIN)
            blocks.append({
                "rect": pygame.Rect(x, y, BLOCK_W, BLOCK_H), 
                "color": BLOCK_COLORS[r % len(BLOCK_COLORS)], 
                "hp": hp_value,
                "last_hit_time": 0 
            })
    return blocks

def item_selection_screen():
    screen.fill(GRAY)
    title = font_big.render("아이템을 선택하세요", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    items = ["1. [패시브] 상단 가속 (7 vs 4)", "2. [액티브] 거대 공 (데미지 2)", "3. [액티브] 관통 모드"]
    for i, txt in enumerate(items):
        surf = font.render(txt, True, YELLOW)
        screen.blit(surf, (WIDTH//2 - 150, 250 + i * 60))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in [pygame.K_1, pygame.K_KP1]: return 1
                if e.key in [pygame.K_2, pygame.K_KP2]: return 2
                if e.key in [pygame.K_3, pygame.K_KP3]: return 3

def draw_hud(score, lives, level_cfg, item_id, cooldown_timer, active_timer, elapsed_ms):
    screen.blit(font.render(f"Score: {score}", True, WHITE), (15, 10))
    screen.blit(font.render(f"Life: {'♥' * lives}", True, RED), (WIDTH - 180, 10))
    screen.blit(font.render(level_cfg["label"], True, YELLOW), (WIDTH // 2 - 40, 10))
    timer_surf = font.render(format_time(elapsed_ms), True, WHITE)
    screen.blit(timer_surf, (WIDTH // 2 - timer_surf.get_width() // 2, 45))

def main():
    selected_item = item_selection_screen()
    game_start_ticks = pygame.time.get_ticks()
    level_idx, score, lives = 0, 0, 3
    
    def reset_level(idx):
        cfg = LEVELS[idx]
        b = make_blocks(cfg["rows"])
        p = pygame.Rect(WIDTH // 2 - PAD_W // 2, HEIGHT - 40, PAD_W, PAD_H)
        ball_obj = pygame.Rect(0, 0, BALL_R_DEFAULT*2, BALL_R_DEFAULT*2)
        return cfg, b, p, ball_obj, False, 5, -5

    level_cfg, blocks, pad, ball, launched, bx, by = reset_level(level_idx)
    cooldown_timer = active_timer = 0

    while True:
        clock.tick(FPS)
        now = pygame.time.get_ticks()
        elapsed_ms = now - game_start_ticks

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE: launched = True
                if e.key == pygame.K_e and now > cooldown_timer:
                    if selected_item == 2: active_timer, cooldown_timer = now + 4000, now + 10000
                    elif selected_item == 3: active_timer, cooldown_timer = now + 2000, now + 15000

        # 패들 이동
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and pad.left > 0: pad.x -= 8
        if keys[pygame.K_RIGHT] and pad.right < WIDTH: pad.x += 8

        # 아이템 효과 적용 (공 크기)
        is_giant = (selected_item == 2 and now < active_timer)
        damage = 2 if is_giant else 1
        r = int(BALL_R_DEFAULT * 1.8) if is_giant else BALL_R_DEFAULT
        ball.size = (r*2, r*2)

        if not launched:
            ball.centerx, ball.bottom = pad.centerx, pad.top
        else:
            # 아이템 1번: 위치에 따른 속도 변화
            if selected_item == 1:
                spd = 8 if ball.centery < HEIGHT // 2 else 5
                bx = spd if bx > 0 else -spd
                by = spd if by > 0 else -spd
            
            ball.x += bx
            ball.y += by

            # [벽 충돌 보정] 벽 안으로 파고드는 현상 방지
            if ball.left <= 0: ball.left = 0; bx = abs(bx)
            if ball.right >= WIDTH: ball.right = WIDTH; bx = -abs(bx)
            if ball.top <= 0: ball.top = 0; by = abs(by)

            # 패들 충돌
            if ball.colliderect(pad) and by > 0:
                ball.bottom = pad.top # 위치 보정
                offset = (ball.centerx - pad.centerx) / (PAD_W / 2)
                bx = int(offset * 6)
                by = -abs(by)

            # 블록 충돌 처리
            is_piercing = (selected_item == 3 and now < active_timer)
            for b in blocks[:]:
                if ball.colliderect(b["rect"]):
                    if not is_piercing:
                        # [정밀 판정] 어느 면에 부딪혔는지 계산
                        overlap = ball.clip(b["rect"])
                        if overlap.width > overlap.height: # 상하 충돌
                            if ball.centery < b["rect"].centery: ball.bottom = b["rect"].top
                            else: ball.top = b["rect"].bottom
                            by *= -1
                        else: # 좌우 충돌
                            if ball.centerx < b["rect"].centerx: ball.right = b["rect"].left
                            else: ball.left = b["rect"].right
                            bx *= -1
                    
                    # 데미지 처리
                    if now > b["last_hit_time"] + 100:
                        b["hp"] -= damage
                        b["last_hit_time"] = now
                        if b["hp"] <= 0:
                            blocks.remove(b)
                            score += 10
                    if not is_piercing: break # 관통 아니면 한 번에 블록 하나만

            # 바닥 추락
            if ball.top > HEIGHT:
                lives -= 1
                launched = False
                if lives <= 0:
                    from sys import exit # 재시작 로직 단순화
                    main()
                    return

        # 레벨 클리어
        if not blocks:
            level_idx += 1
            if level_idx < len(LEVELS):
                level_cfg, blocks, pad, ball, launched, bx, by = reset_level(level_idx)
            else:
                pygame.quit(); sys.exit()

        # 그리기
        screen.fill(GRAY)
        for b in blocks:
            pygame.draw.rect(screen, b["color"], b["rect"], border_radius=3)
            hp_txt = font_small.render(str(b["hp"]), True, WHITE)
            screen.blit(hp_txt, hp_txt.get_rect(center=b["rect"].center))
        
        draw_hud(score, lives, level_cfg, selected_item, cooldown_timer, active_timer, elapsed_ms)
        ball_color = (150, 255, 255) if is_piercing else (WHITE if not is_giant else YELLOW)
        pygame.draw.ellipse(screen, ball_color, ball)
        pygame.draw.rect(screen, WHITE, pad, border_radius=5)
        
        if not launched:
            txt = font.render("SPACE TO START", True, WHITE)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 + 50))
            
        pygame.display.flip()

if __name__ == "__main__":
    main()