import pygame
import sys
import math

pygame.init()
pygame.mixer.init()

# --- 사운드 설정 ---
try:
    hit_sound = pygame.mixer.Sound("6주차/code/assets/sounds/boom.mp3")
except:
    hit_sound = None

def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0: return font
    return pygame.font.SysFont(None, size)

WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE, GRAY, RED, YELLOW, BLUE, GREEN, ORANGE = (255,255,255), (40,40,40), (220,50,50), (240,200,0), (50,120,220), (50,200,50), (240,140,0)
BLACK = (10, 10, 10)
BLOCK_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("벽돌 깨기 - 아이템 마스터리 시스템")
clock = pygame.time.Clock()
font, font_small, font_big = get_korean_font(30), get_korean_font(18), get_korean_font(50)

LEVELS = [{"rows": 3, "label": "레벨 1"}, {"rows": 4, "label": "레벨 2"}, {"rows": 5, "label": "레벨 3"}, {"rows": 6, "label": "레벨 4"}]
BLOCK_COLS, BLOCK_MARGIN, BLOCK_TOP = 10, 4, 80
BLOCK_W = (WIDTH - (BLOCK_MARGIN * (BLOCK_COLS + 1))) // BLOCK_COLS
BLOCK_H = 25

def make_blocks(rows, lv):
    blocks = []
    for r in range(rows):
        hp = 1 + (rows - 1 - r) // 2 + (lv // 2)
        for c in range(BLOCK_COLS):
            x = BLOCK_MARGIN + c * (BLOCK_W + BLOCK_MARGIN)
            y = BLOCK_TOP + r * (BLOCK_H + BLOCK_MARGIN)
            blocks.append({"rect": pygame.Rect(x, y, BLOCK_W, BLOCK_H), "color": BLOCK_COLORS[r % len(BLOCK_COLORS)], "hp": hp, "last_hit_time": 0})
    return blocks

# --- 개선된 UI 상점 시스템 ---
def item_shop(item_id, up_lv):
    while True:
        screen.fill(GRAY)
        # 헤더 영역
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 120))
        title = font_big.render("ROUND CLEAR!", True, YELLOW)
        subtitle = font.render("아이템 강화 선택", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 75))
        
        upgrades = []
        if item_id == 1:
            upgrades = [
                ("1. 초가속 모드", "가속 주기가 2초 -> 1.2초로 대폭 단축됩니다."),
                ("2. 파괴의 속도", "공의 기본 데미지가 +1 증가합니다."),
                ("3. 신속한 복구", "목숨을 1개 회복하고 패들이 조금 길어집니다.")
            ]
        elif item_id == 2:
            upgrades = [
                ("1. 기간틱 파워", "거대화 시 데미지가 2 -> 4로 증가합니다."),
                ("2. 에너지 효율", "거대화 지속 시간이 2초 더 늘어납니다."),
                ("3. 위기 탈출", "거대화 중에는 패들 속도가 1.5배 빨라집니다.")
            ]
        elif item_id == 3:
            upgrades = [
                ("1. 무한 궤도", "관통 쿨타임이 3초 감소합니다."),
                ("2. 연쇄 폭발", "관통 중 벽돌을 부수면 점수를 2배로 얻습니다."),
                ("3. 날카로운 파편", "관통 유지 시간이 1초 증가합니다.")
            ]

        for i, (name, desc) in enumerate(upgrades):
            card_rect = pygame.Rect(100, 150 + i * 130, 600, 100)
            pygame.draw.rect(screen, (60, 60, 60), card_rect, border_radius=15)
            pygame.draw.rect(screen, GREEN, card_rect, 2, border_radius=15)
            
            n_surf = font.render(name, True, GREEN)
            d_surf = font_small.render(desc, True, WHITE)
            screen.blit(n_surf, (130, 170 + i * 130))
            screen.blit(d_surf, (130, 210 + i * 130))
        
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in [pygame.K_1, pygame.K_KP1]: return 1
                if e.key in [pygame.K_2, pygame.K_KP2]: return 2
                if e.key in [pygame.K_3, pygame.K_KP3]: return 3

# --- 게임 오버 화면 ---
def game_over_screen(score):
    while True:
        # 반투명 어두운 배경 효과
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        title = font_big.render("GAME OVER", True, RED)
        score_txt = font.render(f"최종 점수: {score}", True, WHITE)
        retry_txt = font.render("R: 다시하기    Q: 종료하기", True, YELLOW)
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
        screen.blit(score_txt, (WIDTH//2 - score_txt.get_width()//2, HEIGHT//2))
        screen.blit(retry_txt, (WIDTH//2 - retry_txt.get_width()//2, HEIGHT//2 + 80))
        
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True
                if e.key == pygame.K_q: pygame.quit(); sys.exit()

def main():
    # --- 개선된 아이템 선택 UI ---
    screen.fill(GRAY)
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 150))
    intro = font_big.render("ITEM SELECT", True, YELLOW)
    screen.blit(intro, (WIDTH//2 - intro.get_width()//2, 50))
    
    items_info = [
        ("1. [패시브] 속도 조절", "공의 위치에 따라 속도가 자동 조절됩니다."),
        ("2. [액티브] 거대화", "[E키] 공이 커지며 파괴력이 상승합니다."),
        ("3. [액티브] 관통", "[E키] 모든 벽돌을 관통하여 지나갑니다.")
    ]
    
    for i, (title, desc) in enumerate(items_info):
        card = pygame.Rect(100, 180 + i * 110, 600, 90)
        pygame.draw.rect(screen, (50, 50, 70), card, border_radius=10)
        pygame.draw.rect(screen, BLUE, card, 2, border_radius=10)
        t_surf = font.render(title, True, WHITE)
        d_surf = font_small.render(desc, True, (200, 200, 200))
        screen.blit(t_surf, (130, 200 + i * 110))
        screen.blit(d_surf, (130, 235 + i * 110))
    
    pygame.display.flip()
    
    selected_item = 1
    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    selected_item = int(e.unicode); waiting = False

    # 게임 변수 (물리 로직 보호를 위해 기존 변수 유지)
    level_idx, score, lives, cooldown_timer, active_timer = 0, 0, 3, 0, 0
    base_damage, pad_w_add, speed_up_interval = 1, 0, 2000
    giant_dmg, giant_dur, pierce_cd_red, pierce_dur = 2, 4000, 0, 2000
    score_mult = 1
    cheat_seq = 0
    launch_angle = 0
    angle_speed = 2

    def init_level(idx):
        cfg = LEVELS[idx]
        return make_blocks(cfg["rows"], idx), cfg["label"], False, 5, -5

    blocks, current_label, launched, bx, by = init_level(level_idx)
    pad = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 40, 120, 15)
    ball = pygame.Rect(0, 0, 16, 16)
    last_speed_up_time = 0
    ball_fx, ball_fy = float(ball.x), float(ball.y)

    while True:
        clock.tick(FPS)
        now = pygame.time.get_ticks()
        pad.width = 120 + pad_w_add

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE and not launched:
                    rad = math.radians(launch_angle - 90)
                    speed = 7
                    bx = speed * math.cos(rad)
                    by = speed * math.sin(rad)
                    launched = True
                if e.key == pygame.K_e and now > cooldown_timer:
                    if selected_item == 2: active_timer, cooldown_timer = now + giant_dur, now + 10000
                    elif selected_item == 3: active_timer, cooldown_timer = now + pierce_dur, now + (15000 - pierce_cd_red)
                
                # 치트키
                if e.key == pygame.K_1: cheat_seq = 1
                elif e.key == pygame.K_2 and cheat_seq == 1: cheat_seq = 2
                elif e.key == pygame.K_3 and cheat_seq == 2:
                    blocks.clear()
                    cheat_seq = 0
                elif e.key not in [pygame.K_SPACE, pygame.K_e, pygame.K_LEFT, pygame.K_RIGHT]:
                    cheat_seq = 0

        keys = pygame.key.get_pressed()
        p_speed = 12 if (selected_item == 2 and now < active_timer and score_mult == 1.5) else 8
        if keys[pygame.K_LEFT] and pad.left > 0: pad.x -= p_speed
        if keys[pygame.K_RIGHT] and pad.right < WIDTH: pad.x += p_speed

        is_giant = (selected_item == 2 and now < active_timer)
        is_piercing = (selected_item == 3 and now < active_timer)
        current_damage = giant_dmg if is_giant else base_damage
        r = 16 if is_giant else 8
        ball.size = (r*2, r*2)

        if not launched:
            ball.centerx, ball.bottom = pad.centerx, pad.top
            ball_fx, ball_fy = float(ball.x), float(ball.y)
            launch_angle += angle_speed
            if abs(launch_angle) > 60: angle_speed *= -1
            status_msg = "스페이스바로 발사!"
        else:
            if selected_item == 1:
                target_spd = 8 if ball.centery < HEIGHT // 2 else 4
                status_msg = "상단 가속 중!" if target_spd == 8 else "하단 감속 중!"
                bx = target_spd if bx > 0 else -target_spd
                by = target_spd if by > 0 else -target_spd
            else:
                status_msg = "공 이동 중"
                if now - last_speed_up_time > speed_up_interval:
                    bx *= 1.15; by *= 1.15
                    last_speed_up_time = now

            # [물리 로직: 절대 수정 금지 영역]
            steps = int(max(abs(bx), abs(by)) // 5) + 1
            step_bx, step_by = bx / steps, by / steps
            for _ in range(steps):
                ball_fx += step_bx; ball_fy += step_by
                ball.x, ball.y = int(ball_fx), int(ball_fy)
                if ball.left <= 0: ball.left = 0; bx = abs(bx); step_bx = abs(step_bx); ball_fx = float(ball.x)
                if ball.right >= WIDTH: ball.right = WIDTH; bx = -abs(bx); step_bx = -abs(step_bx); ball_fx = float(ball.x)
                if ball.top <= 0: ball.top = 0; by = abs(by); step_by = abs(step_by); ball_fy = float(ball.y)
                if ball.colliderect(pad) and by > 0:
                    ball.bottom = pad.top
                    bx = (ball.centerx - pad.centerx) / (pad.width / 2) * 7
                    by = -abs(by); step_bx, step_by = bx, by
                    ball_fx, ball_fy = float(ball.x), float(ball.y)
                    last_speed_up_time = now; break
                for b in blocks[:]:
                    if ball.colliderect(b["rect"]):
                        if hit_sound: hit_sound.play()
                        if not is_piercing:
                            overlap = ball.clip(b["rect"])
                            if overlap.width > overlap.height:
                                if ball.centery < b["rect"].centery: ball.bottom = b["rect"].top
                                else: ball.top = b["rect"].bottom
                                by *= -1; step_by *= -1; ball_fy = float(ball.y)
                            else:
                                if ball.centerx < b["rect"].centerx: ball.right = b["rect"].left
                                else: ball.left = b["rect"].right
                                bx *= -1; step_bx *= -1; ball_fx = float(ball.x)
                        if now > b["last_hit_time"] + 100:
                            b["hp"] -= current_damage; b["last_hit_time"] = now
                            if b["hp"] <= 0:
                                blocks.remove(b)
                                score += 10 * (2 if (is_piercing and score_mult == 2) else 1)
                        if not is_piercing: break

            if ball.top > HEIGHT:
                lives -= 1; launched = False
                if lives <= 0:
                    if game_over_screen(score): main(); return # 다시하기 선택 시 메인으로

        if not blocks:
            up_choice = item_shop(selected_item, level_idx)
            if selected_item == 1:
                if up_choice == 1: speed_up_interval = 1200
                elif up_choice == 2: base_damage += 1
                elif up_choice == 3: lives += 1; pad_w_add += 20
            elif selected_item == 2:
                if up_choice == 1: giant_dmg = 4
                elif up_choice == 2: giant_dur += 2000
                elif up_choice == 3: score_mult = 1.5
            elif selected_item == 3:
                if up_choice == 1: pierce_cd_red = 3000
                elif up_choice == 2: score_mult = 2
                elif up_choice == 3: pierce_dur += 1000
            
            level_idx += 1
            if level_idx < len(LEVELS):
                blocks, current_label, launched, bx, by = init_level(level_idx)
            else: main(); return

        # 배경 및 게임 객체 드로잉
        screen.fill(GRAY)
        for b in blocks:
            pygame.draw.rect(screen, b["color"], b["rect"], border_radius=3)
            hp_txt = font_small.render(str(b["hp"]), True, WHITE)
            screen.blit(hp_txt, hp_txt.get_rect(center=b["rect"].center))
        
        pygame.draw.rect(screen, (20, 20, 20), (0, 0, WIDTH, 80))
        info = font_small.render(f"점수: {score}  데미지: {base_damage}  목숨: {lives}", True, WHITE)
        screen.blit(info, (15, 10))
        
        item_names = ["속도 조절(P)", "거대화(E)", "관통(E)"]
        screen.blit(font_small.render(f"장착: {item_names[selected_item-1]}", True, (0, 255, 255)), (15, 35))
        
        if selected_item == 1:
            color = GREEN if "가속" in status_msg else ORANGE
            screen.blit(font_small.render(f"패시브: {status_msg}", True, color), (15, 55))
        else:
            cd, dur = max(0, (cooldown_timer - now) // 1000), max(0, (active_timer - now) // 1000)
            if dur > 0: screen.blit(font_small.render(f"지속 시간: {dur}초!", True, GREEN), (15, 55))
            else: screen.blit(font_small.render(f"쿨타임: {cd}초", True, RED if cd > 0 else WHITE), (15, 55))

        screen.blit(font.render(current_label, True, YELLOW), (WIDTH//2 - 40, 10))
        
        if not launched:
            rad = math.radians(launch_angle - 90)
            for i in range(1, 12):
                dot_x, dot_y = ball.centerx + i * 25 * math.cos(rad), ball.centery + i * 25 * math.sin(rad)
                if 0 < dot_x < WIDTH and 0 < dot_y < HEIGHT: pygame.draw.circle(screen, YELLOW, (int(dot_x), int(dot_y)), 3)

        ball_color = (150,255,255) if is_piercing else (WHITE if not is_giant else YELLOW)
        pygame.draw.ellipse(screen, ball_color, ball)
        pygame.draw.rect(screen, WHITE, pad, border_radius=5)
        pygame.display.flip()

if __name__ == "__main__": main()