import pygame
import sys
import math
import random # 상점 랜덤 생성을 위해 추가

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
PURPLE = (180, 50, 255)      # 전용 능력 색상
LIGHT_GRAY = (150, 150, 150) # 공용 옵션 색상
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
        hp = 1.0 + float((rows - 1 - r) // 2 + (lv // 2))
        for c in range(BLOCK_COLS):
            x = BLOCK_MARGIN + c * (BLOCK_W + BLOCK_MARGIN)
            y = BLOCK_TOP + r * (BLOCK_H + BLOCK_MARGIN)
            blocks.append({"rect": pygame.Rect(x, y, BLOCK_W, BLOCK_H), "color": BLOCK_COLORS[r % len(BLOCK_COLORS)], "hp": hp, "last_hit_time": 0})
    return blocks

def item_shop(item_id):
    # 공용 옵션 풀
    common_pool = [
        {"id": "c_spd_up", "name": "[공용] 공 속도 0.5 증가", "desc": "공의 기본 속도가 0.5 빨라집니다.", "type": "common"},
        {"id": "c_spd_dn", "name": "[공용] 공 속도 0.5 감소", "desc": "공의 기본 속도가 0.5 느려집니다.", "type": "common"},
        {"id": "c_mini", "name": "[공용] 미니 볼 생성", "desc": "공이 20번 튕길 때마다 3번 튕기는 미니볼 등장.", "type": "common"},
        {"id": "c_dmg_up", "name": "[공용] 기본 피해량 0.5 증가", "desc": "공의 기본 파괴력이 0.5 증가합니다.", "type": "common"},
        {"id": "c_size_up", "name": "[공용] 공 크기 15% 증가", "desc": "공의 기본 크기가 15% 커집니다.", "type": "common"},
        {"id": "c_life_up", "name": "[공용] 목숨 1개 추가", "desc": "최대 목숨이 1개 늘어납니다.", "type": "common"},
        {"id": "c_score_up", "name": "[공용] 다음 라운드 점수 1.5배", "desc": "다음 라운드 동안 획득 점수가 1.5배가 됩니다.", "type": "common"}
    ]
    
    # 전용 옵션 풀
    specific_pool = []
    if item_id == 1:
        specific_pool = [
            {"id": "i1_1", "name": "[전용] 하단 방어막", "desc": "라운드당 1회 바닥으로 떨어지는 공을 튕겨냅니다.", "type": "specific"},
            {"id": "i1_2", "name": "[전용] 리듬 타격", "desc": "튕길 때마다 다음 타격 피해량이 +1 추가됩니다 (1,2 반복).", "type": "specific"},
            {"id": "i1_3", "name": "[전용] 신속한 복구", "desc": "목숨을 1개 회복하고 패들이 조금 길어집니다.", "type": "specific"}
        ]
    elif item_id == 2:
        specific_pool = [
            {"id": "i2_1", "name": "[전용] 기간틱 파워", "desc": "거대화 시 데미지가 +2 추가 증가합니다.", "type": "specific"},
            {"id": "i2_2", "name": "[전용] 에너지 효율", "desc": "거대화 지속 시간이 2초 늘어납니다.", "type": "specific"},
            {"id": "i2_3", "name": "[전용] 거대 패들", "desc": "거대화 사용 중 패들의 크기도 함께 거대해집니다.", "type": "specific"}
        ]
    elif item_id == 3:
        specific_pool = [
            {"id": "i3_1", "name": "[전용] 무한 궤도", "desc": "관통 쿨타임이 3초 감소합니다.", "type": "specific"},
            {"id": "i3_2", "name": "[전용] 연쇄 폭발", "desc": "관통 중 벽돌 파괴 시 추가 점수 배율을 얻습니다.", "type": "specific"},
            {"id": "i3_3", "name": "[전용] 날카로운 파편", "desc": "관통 유지 시간이 1초 증가합니다.", "type": "specific"}
        ]

    # 풀 병합 및 3개 랜덤 추출
    pool = specific_pool + common_pool
    choices = random.sample(pool, 3)

    while True:
        screen.fill(GRAY)
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 120))
        title = font_big.render("ROUND CLEAR!", True, YELLOW)
        subtitle = font.render("아이템 강화 선택 (랜덤 등장 / 누적 적용)", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 75))
        
        for i, choice in enumerate(choices):
            card_rect = pygame.Rect(100, 150 + i * 130, 600, 100)
            color = PURPLE if choice["type"] == "specific" else LIGHT_GRAY
            
            pygame.draw.rect(screen, (50, 50, 50), card_rect, border_radius=15)
            pygame.draw.rect(screen, color, card_rect, 2, border_radius=15)
            
            n_surf = font.render(f"{i+1}. {choice['name']}", True, color)
            d_surf = font_small.render(choice["desc"], True, WHITE)
            screen.blit(n_surf, (130, 170 + i * 130))
            screen.blit(d_surf, (130, 210 + i * 130))
        
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in [pygame.K_1, pygame.K_KP1]: return choices[0]["id"]
                if e.key in [pygame.K_2, pygame.K_KP2]: return choices[1]["id"]
                if e.key in [pygame.K_3, pygame.K_KP3]: return choices[2]["id"]

def game_over_screen(score):
    while True:
        overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.set_alpha(180); overlay.fill((0, 0, 0))
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
    screen.fill(GRAY)
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, 150))
    screen.blit(font_big.render("ITEM SELECT", True, YELLOW), (WIDTH//2 - 150, 50))
    items_info = [("1. [패시브] 속도 조절", "공의 위치에 따라 속도가 자동 조절됩니다."), ("2. [액티브] 거대화", "[E키] 공이 커지며 파괴력이 상승합니다."), ("3. [액티브] 관통", "[E키] 모든 벽돌을 관통하여 지나갑니다.")]
    for i, (title, desc) in enumerate(items_info):
        card = pygame.Rect(100, 180 + i * 110, 600, 90)
        pygame.draw.rect(screen, (50, 50, 70), card, border_radius=10)
        pygame.draw.rect(screen, BLUE, card, 2, border_radius=10)
        screen.blit(font.render(title, True, WHITE), (130, 200 + i * 110))
        screen.blit(font_small.render(desc, True, (200, 200, 200)), (130, 235 + i * 110))
    pygame.display.flip()
    
    selected_item = 1
    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key in [pygame.K_1, pygame.K_2, pygame.K_3]: selected_item = int(e.unicode); waiting = False

    # --- 신규 및 기존 변수 통합 관리 ---
    level_idx, score, lives, cooldown_timer, active_timer = 0, 0, 3, 0, 0
    base_damage, pad_w_add, speed_up_interval = 1.0, 0, 2000
    giant_dmg, giant_dur, pierce_cd_red, pierce_dur = 2.0, 4000, 0, 2000
    score_mult = 1.0
    cheat_seq, launch_angle, angle_speed = 0, 0, 2
    
    # 신규 시스템 전용 변수
    base_speed_mod = 0.0
    base_radius_mult = 1.0
    score_bonus_rounds = 0
    miniball_active = False
    bounce_count = 0
    miniballs = []
    
    bottom_shield_active = False
    bottom_shield_used = False
    rhythm_damage_active = False
    rhythm_state = 0
    giant_paddle_active = False
    pierce_score_bonus = 0.0

    def init_level(idx):
        cfg = LEVELS[idx % len(LEVELS)]
        return make_blocks(cfg["rows"], idx), cfg["label"], False, 5, -5

    blocks, current_label, launched, bx, by = init_level(level_idx)
    pad = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 40, 120, 15)
    ball = pygame.Rect(0, 0, 16, 16)
    last_speed_up_time = 0
    ball_fx, ball_fy = float(ball.x), float(ball.y)

    # 튕김을 감지하여 리듬/미니볼 등을 발동시키는 헬퍼 함수
    def register_bounce():
        nonlocal bounce_count, rhythm_state
        bounce_count += 1
        if rhythm_damage_active and selected_item == 1:
            rhythm_state = 1 if rhythm_state == 0 else 0
        if miniball_active and bounce_count % 20 == 0:
            rad = math.radians(random.randint(-60, 60) - 90)
            spd = 7 + base_speed_mod
            miniballs.append({
                "rect": pygame.Rect(ball.centerx, ball.centery, 8, 8),
                "fx": float(ball.centerx), "fy": float(ball.centery),
                "bx": spd * math.cos(rad), "by": spd * math.sin(rad),
                "bounces_left": 3
            })

    while True:
        clock.tick(FPS)
        now = pygame.time.get_ticks()
        
        # 거대 패들 능력 적용
        is_giant = (selected_item == 2 and now < active_timer)
        pad.width = 120 + pad_w_add
        if is_giant and giant_paddle_active:
            pad.width = int(pad.width * 1.5)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE and not launched:
                    rad = math.radians(launch_angle - 90)
                    spd = 7 + base_speed_mod
                    bx, by, launched = spd * math.cos(rad), spd * math.sin(rad), True
                if e.key == pygame.K_e and now > cooldown_timer:
                    if selected_item == 2: active_timer, cooldown_timer = now + giant_dur, now + 10000
                    elif selected_item == 3: active_timer, cooldown_timer = now + pierce_dur, now + (15000 - pierce_cd_red)
                if e.key == pygame.K_1: cheat_seq = 1
                elif e.key == pygame.K_2 and cheat_seq == 1: cheat_seq = 2
                elif e.key == pygame.K_3 and cheat_seq == 2: blocks.clear(); cheat_seq = 0

        keys = pygame.key.get_pressed()
        p_speed = 12 if is_giant else 8
        if keys[pygame.K_LEFT] and pad.left > 0: pad.x -= p_speed
        if keys[pygame.K_RIGHT] and pad.right < WIDTH: pad.x += p_speed

        is_piercing = (selected_item == 3 and now < active_timer)
        current_round_mult = 1.5 if score_bonus_rounds > 0 else 1.0
        
        # 관통 모드 시 데미지 1 고정 및 점수 배율 적용
        if is_piercing:
            current_damage = 1.0
            current_score_mult = score_mult * current_round_mult * (1.5 + pierce_score_bonus)
        else:
            current_damage = (giant_dmg if is_giant else base_damage)
            if rhythm_damage_active and selected_item == 1:
                current_damage += rhythm_state
            current_score_mult = score_mult * current_round_mult

        r = (16 if is_giant else 8) * base_radius_mult
        ball.size = (int(r*2), int(r*2))

        if not launched:
            ball.centerx, ball.bottom = pad.centerx, pad.top
            ball_fx, ball_fy = float(ball.x), float(ball.y)
            launch_angle += angle_speed
            if abs(launch_angle) > 60: angle_speed *= -1
            status_msg = "스페이스바로 발사!"
        else:
            if selected_item == 1:
                target_spd = (8 + base_speed_mod) if ball.centery < HEIGHT // 2 else (4 + base_speed_mod)
                bx = target_spd if bx > 0 else -target_spd
                by = target_spd if by > 0 else -target_spd
                status_msg = "자동 속도 제어 중"
            else:
                status_msg = "공 이동 중"
                if now - last_speed_up_time > speed_up_interval:
                    bx *= 1.15; by *= 1.15; last_speed_up_time = now

            # --- [물리 로직 보호구역] 터널링 방지 서브스텝 ---
            steps = int(max(abs(bx), abs(by)) // 5) + 1
            step_bx, step_by = bx / steps, by / steps
            for _ in range(steps):
                ball_fx += step_bx; ball_fy += step_by
                ball.x, ball.y = int(ball_fx), int(ball_fy)
                
                # 벽 충돌
                if ball.left <= 0: ball.left = 0; bx = abs(bx); step_bx = abs(step_bx); ball_fx = float(ball.x); register_bounce()
                if ball.right >= WIDTH: ball.right = WIDTH; bx = -abs(bx); step_bx = -abs(step_bx); ball_fx = float(ball.x); register_bounce()
                if ball.top <= 0: ball.top = 0; by = abs(by); step_by = abs(step_by); ball_fy = float(ball.y); register_bounce()
                
                # 패들 충돌
                if ball.colliderect(pad) and by > 0:
                    ball.bottom = pad.top
                    bx = (ball.centerx - pad.centerx) / (pad.width / 2) * 7
                    by = -abs(by); step_bx, step_by = bx, by
                    ball_fx, ball_fy = float(ball.x), float(ball.y)
                    last_speed_up_time = now
                    register_bounce()
                    break
                
                # 블록 충돌
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
                                score += int(10 * current_score_mult)
                        if not is_piercing: 
                            register_bounce()
                            break

            # 하단 방어막 및 낙하 처리
            if ball.top > HEIGHT:
                if bottom_shield_active and not bottom_shield_used:
                    ball.bottom = HEIGHT
                    by = -abs(by); step_by = -abs(step_by); ball_fy = float(ball.y)
                    bottom_shield_used = True
                    register_bounce()
                else:
                    lives -= 1; launched = False
                    bottom_shield_used = False # 새로 발사 시 쉴드 초기화
                    if lives <= 0:
                        if game_over_screen(score): main(); return

        # 미니볼 물리 처리
        for mb in miniballs[:]:
            mb["fx"] += mb["bx"]; mb["fy"] += mb["by"]
            mb["rect"].x, mb["rect"].y = int(mb["fx"]), int(mb["fy"])
            mb_bounced = False
            
            if mb["rect"].left <= 0: mb["rect"].left = 0; mb["bx"] *= -1; mb_bounced = True
            if mb["rect"].right >= WIDTH: mb["rect"].right = WIDTH; mb["bx"] *= -1; mb_bounced = True
            if mb["rect"].top <= 0: mb["rect"].top = 0; mb["by"] *= -1; mb_bounced = True
            if mb["rect"].colliderect(pad) and mb["by"] > 0:
                mb["rect"].bottom = pad.top
                mb["bx"] = (mb["rect"].centerx - pad.centerx) / (pad.width / 2) * 7
                mb["by"] = -abs(mb["by"]); mb_bounced = True
                
            for b in blocks[:]:
                if mb["rect"].colliderect(b["rect"]):
                    b["hp"] -= 1.0 # 미니볼은 데미지 1 고정
                    if b["hp"] <= 0:
                        blocks.remove(b)
                        score += int(10 * current_score_mult)
                    mb["by"] *= -1; mb_bounced = True
                    break
                    
            if mb_bounced:
                mb["bounces_left"] -= 1
                if mb["bounces_left"] <= 0: miniballs.remove(mb)
            elif mb["rect"].top > HEIGHT:
                miniballs.remove(mb)

        if not blocks:
            # 보너스 라운드 상태 차감
            if score_bonus_rounds > 0: score_bonus_rounds -= 1
            bottom_shield_used = False # 라운드 클리어 시 쉴드 충전

            up_choice = item_shop(selected_item)
            # 공용 업그레이드
            if up_choice == "c_spd_up": base_speed_mod += 0.5
            elif up_choice == "c_spd_dn": base_speed_mod -= 0.5
            elif up_choice == "c_mini": miniball_active = True
            elif up_choice == "c_dmg_up": base_damage += 0.5
            elif up_choice == "c_size_up": base_radius_mult *= 1.15
            elif up_choice == "c_life_up": lives += 1
            elif up_choice == "c_score_up": score_bonus_rounds += 1
            # 전용 업그레이드
            elif up_choice == "i1_1": bottom_shield_active = True
            elif up_choice == "i1_2": rhythm_damage_active = True
            elif up_choice == "i1_3": lives += 1; pad_w_add += 20
            elif up_choice == "i2_1": giant_dmg += 2.0
            elif up_choice == "i2_2": giant_dur += 2000
            elif up_choice == "i2_3": giant_paddle_active = True
            elif up_choice == "i3_1": pierce_cd_red += 3000
            elif up_choice == "i3_2": pierce_score_bonus += 1.0
            elif up_choice == "i3_3": pierce_dur += 1000
            
            level_idx += 1
            blocks, current_label, launched, bx, by = init_level(level_idx)

        # 화면 렌더링
        screen.fill(GRAY)
        
        # 하단 쉴드 라인 그리기
        if bottom_shield_active and not bottom_shield_used:
            pygame.draw.line(screen, PURPLE, (0, HEIGHT-2), (WIDTH, HEIGHT-2), 4)

        for b in blocks:
            pygame.draw.rect(screen, b["color"], b["rect"], border_radius=3)
            # 체력이 소수점일 수 있으므로 깔끔하게 포맷팅
            hp_txt = font_small.render(f"{b['hp']:g}", True, WHITE)
            screen.blit(hp_txt, hp_txt.get_rect(center=b["rect"].center))
            
        pygame.draw.rect(screen, (20, 20, 20), (0, 0, WIDTH, 80))
        dmg_str = f"{current_damage:g}" + (" (관통 고정)" if is_piercing else "")
        screen.blit(font_small.render(f"점수: {score}  데미지: {dmg_str}  목숨: {lives}", True, WHITE), (15, 10))
        screen.blit(font_small.render(f"장착: {['속도조절', '거대화', '관통'][selected_item-1]}", True, (0, 255, 255)), (15, 35))
        
        if selected_item == 1:
            rhythm_str = " (리듬 타격 ON)" if rhythm_damage_active else ""
            screen.blit(font_small.render(f"패시브 활성 중{rhythm_str}", True, GREEN), (15, 55))
        else:
            cd, dur = max(0, (cooldown_timer - now) // 1000), max(0, (active_timer - now) // 1000)
            msg = f"지속: {dur}s" if dur > 0 else f"쿨타임: {cd}s"
            screen.blit(font_small.render(msg, True, GREEN if dur > 0 else WHITE), (15, 55))
            
        if score_bonus_rounds > 0:
            screen.blit(font_small.render(f"[점수 1.5배 버프 활성화]", True, YELLOW), (200, 35))
            
        screen.blit(font.render(current_label, True, YELLOW), (WIDTH//2 - 40, 10))
        
        if not launched:
            rad = math.radians(launch_angle - 90)
            for i in range(1, 12):
                pygame.draw.circle(screen, YELLOW, (int(ball.centerx + i * 25 * math.cos(rad)), int(ball.centery + i * 25 * math.sin(rad))), 3)
                
        # 미니볼 그리기
        for mb in miniballs:
            pygame.draw.ellipse(screen, (200, 255, 255), mb["rect"])
            
        pygame.draw.ellipse(screen, (150,255,255) if is_piercing else (WHITE if not is_giant else YELLOW), ball)
        pygame.draw.rect(screen, WHITE, pad, border_radius=5)
        pygame.display.flip()

if __name__ == "__main__": main()