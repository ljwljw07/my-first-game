import pygame
import sys
import math  # 방향 계산을 위해 추가

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

# --- 아이템 설명 및 상점 시스템 ---
def item_shop(item_id, up_lv):
    screen.fill(GRAY)
    title = font_big.render(f"ROUND CLEAR! 아이템 강화", True, YELLOW)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))
    
    # 아이템별 강화 옵션 정의
    upgrades = []
    if item_id == 1: # 속도 패시브 강화
        upgrades = [
            ("1. 초가속 모드", "가속 주기가 2초 -> 1.2초로 대폭 단축됩니다."),
            ("2. 파괴의 속도", "공의 기본 데미지가 +1 증가합니다."),
            ("3. 신속한 복구", "목숨을 1개 회복하고 패들이 조금 길어집니다.")
        ]
    elif item_id == 2: # 거대 공 강화
        upgrades = [
            ("1. 기간틱 파워", "거대화 시 데미지가 2 -> 4로 증가합니다."),
            ("2. 에너지 효율", "거대화 지속 시간이 2초 더 늘어납니다."),
            ("3. 위기 탈출", "거대화 중에는 패들 속도가 1.5배 빨라집니다.")
        ]
    elif item_id == 3: # 관통 공 강화
        upgrades = [
            ("1. 무한 궤도", "관통 쿨타임이 3초 감소합니다."),
            ("2. 연쇄 폭발", "관통 중 벽돌을 부수면 점수를 2배로 얻습니다."),
            ("3. 날카로운 파편", "관통 유지 시간이 1초 증가합니다.")
        ]

    for i, (name, desc) in enumerate(upgrades):
        n_surf = font.render(name, True, GREEN)
        d_surf = font_small.render(desc, True, WHITE)
        screen.blit(n_surf, (150, 220 + i * 100))
        screen.blit(d_surf, (150, 255 + i * 100))
    
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in [pygame.K_1, pygame.K_KP1]: return 1
                if e.key in [pygame.K_2, pygame.K_KP2]: return 2
                if e.key in [pygame.K_3, pygame.K_KP3]: return 3

def main():
    # 최초 아이템 선택
    screen.fill(GRAY)
    intro = font.render("사용할 아이템을 선택하세요 (1, 2, 3)", True, YELLOW)
    items_info = [
        "1. [패시브] 위치별 속도 조절 - 공 제어가 쉬워집니다.",
        "2. [액티브] 거대화 - 일정 시간 동안 강력한 파괴력을 가집니다.",
        "3. [액티브] 관통 - 일정 시간 동안 모든 벽돌을 뚫습니다."
    ]
    screen.blit(intro, (WIDTH//2 - intro.get_width()//2, 100))
    for i, txt in enumerate(items_info):
        surf = font_small.render(txt, True, WHITE)
        screen.blit(surf, (150, 250 + i * 60))
    pygame.display.flip()
    
    selected_item = 1
    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    selected_item = int(e.unicode); waiting = False

    # 게임 변수
    level_idx, score, lives, cooldown_timer, active_timer = 0, 0, 3, 0, 0
    base_damage, pad_w_add, speed_up_interval = 1, 0, 2000
    giant_dmg, giant_dur, pierce_cd_red, pierce_dur = 2, 4000, 0, 2000
    score_mult = 1
    cheat_seq = 0 # [추가] 치트키 감지 변수
    
    # --- 발사 각도 조절용 변수 ---
    launch_angle = 0  # 0도는 위쪽
    angle_speed = 2   # 각도 회전 속도

    def init_level(idx):
        cfg = LEVELS[idx]
        return make_blocks(cfg["rows"], idx), cfg["label"], False, 5, -5

    blocks, current_label, launched, bx, by = init_level(level_idx)
    pad = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 40, 120, 15)
    ball = pygame.Rect(0, 0, 16, 16)
    last_speed_up_time = 0

    # [추가] 정밀한 좌표 계산을 위한 실수(float) 변수
    ball_fx, ball_fy = float(ball.x), float(ball.y)

    while True:
        clock.tick(FPS)
        now = pygame.time.get_ticks()
        pad.width = 120 + pad_w_add

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE and not launched:
                    # 회전하는 각도에 맞춰 초기 속도 설정
                    # launch_angle이 0이면 정중앙 위, -60~60도 사이 회전
                    rad = math.radians(launch_angle - 90)
                    speed = 7 # 초기 발사 속도
                    bx = speed * math.cos(rad)
                    by = speed * math.sin(rad)
                    launched = True
                elif e.key == pygame.K_SPACE and launched:
                    pass # 이미 발사된 경우 무시
                
                if e.key == pygame.K_e and now > cooldown_timer:
                    if selected_item == 2: active_timer, cooldown_timer = now + giant_dur, now + 10000
                    elif selected_item == 3: active_timer, cooldown_timer = now + pierce_dur, now + (15000 - pierce_cd_red)
                
                # [추가] 1 -> 2 -> 3 연속 입력 치트키
                if e.key == pygame.K_1: cheat_seq = 1
                elif e.key == pygame.K_2 and cheat_seq == 1: cheat_seq = 2
                elif e.key == pygame.K_3 and cheat_seq == 2:
                    blocks.clear() # 모든 블록 파괴 (라운드 클리어)
                    cheat_seq = 0
                elif e.key not in [pygame.K_SPACE, pygame.K_e, pygame.K_LEFT, pygame.K_RIGHT]:
                    cheat_seq = 0 # 다른 키를 누르면 치트키 초기화

        keys = pygame.key.get_pressed()
        p_speed = 12 if (selected_item == 2 and now < active_timer and score_mult == 1.5) else 8
        if keys[pygame.K_LEFT] and pad.left > 0: pad.x -= p_speed
        if keys[pygame.K_RIGHT] and pad.right < WIDTH: pad.x += p_speed

        is_giant = (selected_item == 2 and now < active_timer)
        is_piercing = (selected_item == 3 and now < active_timer)
        current_damage = giant_dmg if is_giant else base_damage
        r = 16 if is_giant else 8
        ball.size = (r*2, r*2)

        status_msg = "대기 중..."

        if not launched:
            ball.centerx, ball.bottom = pad.centerx, pad.top
            ball_fx, ball_fy = float(ball.x), float(ball.y) # 정밀 좌표 동기화
            last_speed_up_time = now
            
            # 각도 회전 로직 (-60도에서 60도 사이를 왕복)
            launch_angle += angle_speed
            if abs(launch_angle) > 60:
                angle_speed *= -1
            
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

            # [핵심 변경] 터널링 방지를 위한 서브-스텝(Sub-stepping) 물리 로직
            steps = int(max(abs(bx), abs(by)) // 5) + 1
            step_bx = bx / steps
            step_by = by / steps

            for _ in range(steps):
                ball_fx += step_bx
                ball_fy += step_by
                ball.x = int(ball_fx)
                ball.y = int(ball_fy)

                # 1. 벽 충돌 검사
                if ball.left <= 0: ball.left = 0; bx = abs(bx); step_bx = abs(step_bx); ball_fx = float(ball.x)
                if ball.right >= WIDTH: ball.right = WIDTH; bx = -abs(bx); step_bx = -abs(step_bx); ball_fx = float(ball.x)
                if ball.top <= 0: ball.top = 0; by = abs(by); step_by = abs(step_by); ball_fy = float(ball.y)

                # 2. 패들 충돌 검사
                if ball.colliderect(pad) and by > 0:
                    ball.bottom = pad.top
                    bx = int((ball.centerx - pad.centerx) / (pad.width / 2) * 7) or bx
                    by = -5; bx = 5 if bx > 0 else -5
                    step_bx, step_by = bx, by # 바뀐 속도 적용
                    ball_fx, ball_fy = float(ball.x), float(ball.y)
                    last_speed_up_time = now
                    break # 패들에 닿으면 이번 프레임 스텝 검사 종료

                # 3. 블록 충돌 검사
                hit_block_this_step = False
                for b in blocks[:]:
                    if ball.colliderect(b["rect"]):
                        if hit_sound: hit_sound.play()
                        if not is_piercing:
                            overlap = ball.clip(b["rect"])
                            if overlap.width > overlap.height:
                                if ball.centery < b["rect"].centery: ball.bottom = b["rect"].top
                                else: ball.top = b["rect"].bottom
                                by *= -1; step_by *= -1
                                ball_fy = float(ball.y)
                            else:
                                if ball.centerx < b["rect"].centerx: ball.right = b["rect"].left
                                else: ball.left = b["rect"].right
                                bx *= -1; step_bx *= -1
                                ball_fx = float(ball.x)
                        
                        if now > b["last_hit_time"] + 100:
                            b["hp"] -= current_damage
                            b["last_hit_time"] = now
                            if b["hp"] <= 0:
                                blocks.remove(b)
                                score += 10 * (2 if (is_piercing and score_mult == 2) else 1)
                        if not is_piercing:
                            hit_block_this_step = True
                            break

            if ball.top > HEIGHT:
                lives -= 1; launched = False
                if lives <= 0: main(); return

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
            cd = max(0, (cooldown_timer - now) // 1000)
            dur = max(0, (active_timer - now) // 1000)
            if dur > 0:
                screen.blit(font_small.render(f"지속 시간: {dur}초!", True, GREEN), (15, 55))
            else:
                screen.blit(font_small.render(f"쿨타임: {cd}초", True, RED if cd > 0 else WHITE), (15, 55))

        screen.blit(font.render(current_label, True, YELLOW), (WIDTH//2 - 40, 10))
        
        # --- 발사 가이드 화살표 그리기 ---
        if not launched:
            guide_len = 40
            rad = math.radians(launch_angle - 90)
            end_x = ball.centerx + guide_len * math.cos(rad)
            end_y = ball.centery + guide_len * math.sin(rad)
            pygame.draw.line(screen, YELLOW, (ball.centerx, ball.centery), (end_x, end_y), 3)

        ball_color = (150,255,255) if is_piercing else (WHITE if not is_giant else YELLOW)
        pygame.draw.ellipse(screen, ball_color, ball)
        pygame.draw.rect(screen, WHITE, pad, border_radius=5)
        pygame.display.flip()

if __name__ == "__main__": main()