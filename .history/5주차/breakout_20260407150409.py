import pygame
import sys

pygame.init()
pygame.mixer.init()

# --- 사운드 로드 ---
try:
    # 경로: 6주차/code/assets/sounds/boom.mp3
    hit_sound = pygame.mixer.Sound("6주차/code/assets/sounds/boom.mp3")
except:
    print("사운드 파일을 찾을 수 없습니다. 경로를 확인하세요.")
    hit_sound = None

def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0: return font
    return pygame.font.SysFont(None, size)

def format_time(ms):
    return f"{ms // 60000:02}:{(ms % 60000) // 1000:02}.{(ms % 1000) // 10:02}"

WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE, GRAY, RED, YELLOW, BLUE, GREEN, ORANGE = (255,255,255), (40,40,40), (220,50,50), (240,200,0), (50,120,220), (50,200,50), (240,140,0)
BLOCK_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("벽돌 깨기 - 강화 및 가속 시스템")
clock = pygame.time.Clock()
font, font_small, font_big = get_korean_font(30), get_korean_font(16), get_korean_font(60)

LEVELS = [{"rows": 3, "label": "레벨 1"}, {"rows": 4, "label": "레벨 2"}, {"rows": 5, "label": "레벨 3"}, {"rows": 6, "label": "레벨 4"}]
BLOCK_COLS, BLOCK_MARGIN, BLOCK_TOP = 10, 4, 80
BLOCK_W = (WIDTH - (BLOCK_MARGIN * (BLOCK_COLS + 1))) // BLOCK_COLS
BLOCK_H = 25

def make_blocks(rows, hp_boost):
    blocks = []
    for r in range(rows):
        hp_value = 1 + (rows - 1 - r) // 2 + hp_boost
        for c in range(BLOCK_COLS):
            x = BLOCK_MARGIN + c * (BLOCK_W + BLOCK_MARGIN)
            y = BLOCK_TOP + r * (BLOCK_H + BLOCK_MARGIN)
            blocks.append({"rect": pygame.Rect(x, y, BLOCK_W, BLOCK_H), "color": BLOCK_COLORS[r % len(BLOCK_COLORS)], "hp": hp_value, "last_hit_time": 0})
    return blocks

def upgrade_screen(current_items):
    screen.fill(GRAY)
    title = font_big.render("라운드 클리어! 강화 선택", True, YELLOW)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
    
    options = ["1. 패들 크기 증가", "2. 기본 데미지 +1", "3. 목숨 +1 추가"]
    for i, opt in enumerate(options):
        surf = font.render(opt, True, WHITE)
        screen.blit(surf, (WIDTH//2 - 120, 250 + i * 60))
    
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in [pygame.K_1, pygame.K_KP1]: return "pad"
                if e.key in [pygame.K_2, pygame.K_KP2]: return "dmg"
                if e.key in [pygame.K_3, pygame.K_KP3]: return "life"

def main():
    # 아이템 선택 (최초 1회)
    selected_item = 1 # 기본 선택
    screen.fill(GRAY)
    msg = font.render("아이템 1, 2, 3 중 하나를 눌러 게임 시작", True, WHITE)
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in [pygame.K_1, pygame.K_2, pygame.K_3]: 
                    selected_item = int(e.unicode); waiting = False

    game_start_ticks = pygame.time.get_ticks()
    level_idx, score, lives, cooldown_timer, active_timer = 0, 0, 3, 0, 0
    base_damage, extra_pad_w = 1, 0
    
    def init_level(idx):
        cfg = LEVELS[idx]
        return make_blocks(cfg["rows"], idx), cfg["label"], False, 5, -5

    blocks, current_label, launched, bx, by = init_level(level_idx)
    pad = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 40, 120, 15)
    ball = pygame.Rect(0, 0, 16, 16)
    
    last_speed_up_time = 0

    while True:
        clock.tick(FPS)
        now = pygame.time.get_ticks()
        elapsed_ms = now - game_start_ticks
        pad.width = 120 + extra_pad_w # 업그레이드 반영

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE: launched = True
                if e.key == pygame.K_e and now > cooldown_timer:
                    if selected_item == 2: active_timer, cooldown_timer = now + 4000, now + 10000
                    elif selected_item == 3: active_timer, cooldown_timer = now + 2000, now + 15000

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and pad.left > 0: pad.x -= 8
        if keys[pygame.K_RIGHT] and pad.right < WIDTH: pad.x += 8

        is_giant = (selected_item == 2 and now < active_timer)
        is_piercing = (selected_item == 3 and now < active_timer)
        current_damage = (base_damage + 1) if is_giant else base_damage
        r = 14 if is_giant else 8
        ball.size = (r*2, r*2)

        if not launched:
            ball.centerx, ball.bottom = pad.centerx, pad.top
            last_speed_up_time = now # 발사 전까지 시간 초기화
        else:
            # --- 시간 경과에 따른 가속 시스템 ---
            if now - last_speed_up_time > 2000: # 2초마다 가속
                bx *= 1.1; by *= 1.1
                last_speed_up_time = now

            ball.x += bx
            ball.y += by

            if ball.left <= 0: ball.left = 0; bx = abs(bx)
            if ball.right >= WIDTH: ball.right = WIDTH; bx = -abs(bx)
            if ball.top <= 0: ball.top = 0; by = abs(by)

            # 패들 충돌 (속도 초기화)
            if ball.colliderect(pad) and by > 0:
                ball.bottom = pad.top
                bx = int((ball.centerx - pad.centerx) / (pad.width / 2) * 6) or bx
                by = -5 # 패들에 닿으면 속도 초기화 (기본값 -5)
                bx = 5 if bx > 0 else -5
                last_speed_up_time = now

            for b in blocks[:]:
                if ball.colliderect(b["rect"]):
                    if hit_sound: hit_sound.play() # 사운드 재생
                    if not is_piercing:
                        overlap = ball.clip(b["rect"])
                        if overlap.width > overlap.height:
                            if ball.centery < b["rect"].centery: ball.bottom = b["rect"].top
                            else: ball.top = b["rect"].bottom
                            by *= -1
                        else:
                            if ball.centerx < b["rect"].centerx: ball.right = b["rect"].left
                            else: ball.left = b["rect"].right
                            bx *= -1
                    if now > b["last_hit_time"] + 100:
                        b["hp"] -= current_damage
                        b["last_hit_time"] = now
                        if b["hp"] <= 0: blocks.remove(b); score += 10
                    if not is_piercing: break

            if ball.top > HEIGHT:
                lives -= 1; launched = False
                if lives <= 0: main(); return

        if not blocks: # 레벨 클리어
            reward = upgrade_screen(selected_item)
            if reward == "pad": extra_pad_w += 30
            elif reward == "dmg": base_damage += 1
            elif reward == "life": lives += 1
            
            level_idx += 1
            if level_idx < len(LEVELS):
                blocks, current_label, launched, bx, by = init_level(level_idx)
            else: main(); return

        screen.fill(GRAY)
        for b in blocks:
            pygame.draw.rect(screen, b["color"], b["rect"], border_radius=3)
            hp_txt = font_small.render(str(b["hp"]), True, WHITE)
            screen.blit(hp_txt, hp_txt.get_rect(center=b["rect"].center))
        
        # HUD 정보
        screen.blit(font.render(f"Score: {score}  Dmg: {base_damage}", True, WHITE), (15, 10))
        screen.blit(font.render(f"Life: {'♥'*lives}", True, RED), (WIDTH - 180, 10))
        ball_color = (150,255,255) if is_piercing else (WHITE if not is_giant else YELLOW)
        pygame.draw.ellipse(screen, ball_color, ball)
        pygame.draw.rect(screen, WHITE, pad, border_radius=5)
        pygame.display.flip()

if __name__ == "__main__": main()