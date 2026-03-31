import pygame
import sys
import math
from sprites import load_sprite

# 1. 초기화 및 창 설정
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("원형, AABB, OBB 충돌 동시 시각화")

# 색상 정의
WHITE = (255, 255, 255)
RED = (255, 0, 0)      # AABB 색상
BLUE = (0, 0, 255)     # 원형 Bounding Box 색상
GREEN = (0, 255, 0)    # OBB (회전하는 경계 상자) 색상
GRAY = (200, 200, 200) # 평상시 텍스트 색상

# 폰트 설정
font = pygame.font.SysFont(None, 40)

# ==========================================
# OBB 충돌을 위한 분리축 정리(SAT) 헬퍼 함수
# ==========================================
def get_axes(corners):
    """다각형의 각 변에 대한 수직 벡터(법선 벡터)를 구합니다."""
    axes = []
    for i in range(len(corners)):
        p1 = corners[i]
        p2 = corners[(i + 1) % len(corners)]
        edge = p2 - p1
        normal = pygame.math.Vector2(-edge.y, edge.x)
        if normal.length() > 0:
            axes.append(normal.normalize())
    return axes

def project(corners, axis):
    """주어진 축(axis)에 다각형의 꼭짓점들을 투영하여 최솟값과 최댓값을 구합니다."""
    dots = [corner.dot(axis) for corner in corners]
    return min(dots), max(dots)

def check_obb_collision(corners1, corners2):
    """두 OBB의 꼭짓점 리스트를 받아 충돌 여부를 반환합니다 (SAT 알고리즘)."""
    # 두 다각형의 모든 검사 축을 모음
    axes = get_axes(corners1) + get_axes(corners2)
    for axis in axes:
        min1, max1 = project(corners1, axis)
        min2, max2 = project(corners2, axis)
        # 단 하나의 축이라도 그림자가 겹치지 않으면 절대 충돌하지 않은 것임
        if max1 < min2 or max2 < min1:
            return False
    # 모든 축에서 겹치면 충돌임
    return True
# ==========================================

# 2. 오브젝트 생성 및 배치 함수
def create_obj(name, pos, size=None):
    img = load_sprite(name, size)
    rect = img.get_rect(center=pos)
    radius = rect.width / 2
    return {
        "base_img": img,
        "img": img,
        "rect": rect,
        "center": pos,
        "width": rect.width,
        "height": rect.height,
        "radius": radius,
        "angle": 0,
        "corners": [] # OBB 꼭짓점 저장을 위한 리스트
    }

# 각 스프라이트 배치
player = create_obj("stone", (100, 100))
player_speed = 5

static_objects = [
    create_obj("adventurer", (WIDTH // 2, HEIGHT // 2), (80, 110)),
    create_obj("rocket", (650, 150), (60, 160)),
    create_obj("sword", (150, 450), (70, 70))
]

clock = pygame.time.Clock()

while True:
    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 3. 플레이어 이동 및 회전 가속 로직
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_LEFT]:  player["rect"].x -= player_speed
    if keys[pygame.K_RIGHT]: player["rect"].x += player_speed
    if keys[pygame.K_UP]:    player["rect"].y -= player_speed
    if keys[pygame.K_DOWN]:  player["rect"].y += player_speed

    rot_speed = 5 if keys[pygame.K_z] else 1 

    # 플레이어의 OBB 모서리 좌표 계산 (플레이어는 회전하지 않으므로 AABB와 동일)
    px, py = player["rect"].center
    hw, hh = player["width"] / 2, player["height"] / 2
    player_corners = [
        pygame.math.Vector2(px - hw, py - hh),
        pygame.math.Vector2(px + hw, py - hh),
        pygame.math.Vector2(px + hw, py + hh),
        pygame.math.Vector2(px - hw, py + hh)
    ]

    # 4. 정적 오브젝트 회전 및 꼭짓점(Corners) 계산
    for obj in static_objects:
        obj["angle"] = (obj["angle"] + rot_speed) % 360
        obj["img"] = pygame.transform.rotate(obj["base_img"], obj["angle"])
        obj["rect"] = obj["img"].get_rect(center=obj["center"])

        cx, cy = obj["center"]
        ohw, ohh = obj["width"] / 2, obj["height"] / 2
        
        # 원본 중심 기준 꼭짓점
        base_corners = [
            pygame.math.Vector2(-ohw, -ohh),
            pygame.math.Vector2(ohw, -ohh),
            pygame.math.Vector2(ohw, ohh),
            pygame.math.Vector2(-ohw, ohh)
        ]
        
        # 회전 적용
        rotated_corners = []
        for corner in base_corners:
            rotated = corner.rotate(-obj["angle"]) # Pygame 회전은 반시계방향이라 - 부호 사용
            rotated_corners.append(pygame.math.Vector2(cx + rotated.x, cy + rotated.y))
        obj["corners"] = rotated_corners

    # 5. 세 가지 방식의 충돌 감지
    hit_circle = False
    hit_aabb = False
    hit_obb = False

    for obj in static_objects:
        # [1] 원형 충돌 (거리 계산)
        dx = player["rect"].centerx - obj["rect"].centerx
        dy = player["rect"].centery - obj["rect"].centery
        if (dx**2 + dy**2) < (player["radius"] + obj["radius"])**2:
            hit_circle = True
            
        # [2] AABB 충돌 (Pygame 내장 함수 사용)
        if player["rect"].colliderect(obj["rect"]):
            hit_aabb = True

        # [3] OBB 충돌 (SAT 알고리즘 사용)
        if check_obb_collision(player_corners, obj["corners"]):
            hit_obb = True

    # ==========================================
    # 6. 화면 그리기
    # ==========================================
    screen.fill(WHITE)

    # 모든 정적 오브젝트 그리기
    for obj in static_objects:
        screen.blit(obj["img"], obj["rect"])
        pygame.draw.rect(screen, RED, obj["rect"], 2) # AABB
        pygame.draw.circle(screen, BLUE, obj["rect"].center, int(obj["radius"]), 2) # Circle
        
        # OBB 다각형 그리기 (Vector2 리스트를 튜플 리스트로 변환하여 사용)
        poly_points = [(p.x, p.y) for p in obj["corners"]]
        pygame.draw.polygon(screen, GREEN, poly_points, 2)

    # 플레이어 그리기
    screen.blit(player["img"], player["rect"])
    pygame.draw.rect(screen, RED, player["rect"], 2)
    pygame.draw.circle(screen, BLUE, player["rect"].center, int(player["radius"]), 2)
    pygame.draw.polygon(screen, GREEN, [(p.x, p.y) for p in player_corners], 2)

    # 텍스트 UI 표시 (좌측 상단)
    # 충돌 시 해당 색상으로, 아닐 시 회색으로 표시하여 깜빡임을 방지합니다.
    circle_text = font.render("Circle: HIT" if hit_circle else "Circle: SAFE", True, BLUE if hit_circle else GRAY)
    aabb_text = font.render("AABB: HIT" if hit_aabb else "AABB: SAFE", True, RED if hit_aabb else GRAY)
    obb_text = font.render("OBB: HIT" if hit_obb else "OBB: SAFE", True, GREEN if hit_obb else GRAY)

    screen.blit(circle_text, (10, 10))
    screen.blit(aabb_text, (10, 50))
    screen.blit(obb_text, (10, 90))

    pygame.display.flip()
    clock.tick(60)