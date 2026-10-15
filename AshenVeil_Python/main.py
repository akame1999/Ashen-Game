"""ASHEN VEIL — side-scrolling dark-fantasy combat prototype.

An original, asset-free 2D action-platformer inspired by the atmosphere of
Soulslike worlds and the pace of action roguelites / Metroidvania games.
All art is drawn procedurally with Pygame CE; no external assets are required.
"""
from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass
from collections import OrderedDict

import pygame
from pygame.math import Vector2

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
W, H = 1440, 810
FPS = 120
WORLD_W = 4920
FLOOR_Y = 690
GRAVITY = 2100.0
BG_TOP = (16, 21, 25)
BG_BOTTOM = (36, 39, 39)
STONE = (57, 60, 58)
STONE_LIT = (82, 81, 72)
GOLD = (213, 174, 103)
PALE_GOLD = (255, 227, 161)
TEAL = (103, 201, 183)
RED = (190, 69, 62)
PALE = (230, 224, 205)
MUTED = (142, 145, 139)
DARK = (12, 15, 16)

WEAPONS = {
    "Rookfang": {
        "title": "ROOKFANG LONGSWORD", "style": "BALANCED", "damage": 25,
        "reach": 86, "height": 54, "windup": 0.095, "active": 0.16,
        "recovery": 0.19, "stamina": 15, "combo": 0.42,
        "heavy_damage": 55, "heavy_reach": 124, "heavy_windup": 0.30,
        "heavy_active": 0.20, "heavy_recovery": 0.30, "heavy_cost": 30,
        "skill": "RIFT STEP", "skill_cd": 4.2, "skill_cost": 28,
        "color": (223, 222, 202), "arc": 1.0,
    },
    "Gravetide": {
        "title": "GRAVETIDE TWINBLADES", "style": "QUICK", "damage": 16,
        "reach": 72, "height": 52, "windup": 0.045, "active": 0.12,
        "recovery": 0.10, "stamina": 9, "combo": 0.30,
        "heavy_damage": 37, "heavy_reach": 96, "heavy_windup": 0.19,
        "heavy_active": 0.16, "heavy_recovery": 0.22, "heavy_cost": 22,
        "skill": "UNDERTOW", "skill_cd": 3.5, "skill_cost": 24,
        "color": (105, 220, 195), "arc": 1.18,
    },
    "Oathbreaker": {
        "title": "OATHBREAKER GREATSWORD", "style": "HEAVY", "damage": 42,
        "reach": 105, "height": 68, "windup": 0.18, "active": 0.22,
        "recovery": 0.29, "stamina": 23, "combo": 0.58,
        "heavy_damage": 88, "heavy_reach": 150, "heavy_windup": 0.42,
        "heavy_active": 0.24, "heavy_recovery": 0.37, "heavy_cost": 42,
        "skill": "GROUNDSPLIT", "skill_cd": 5.1, "skill_cost": 35,
        "color": (234, 177, 104), "arc": 0.78,
    },
}
WEAPON_ORDER = ["Rookfang", "Gravetide", "Oathbreaker"]
AREAS = [
    (0, 1320, "THE DROWNED MARCH", (19, 26, 31), (43, 47, 46)),
    (1320, 2850, "THE ASHEN CHAPEL", (27, 24, 24), (54, 45, 39)),
    (2850, 4050, "THE CINDER BASTION", (27, 21, 22), (59, 39, 35)),
    (4050, WORLD_W, "THE VEILED THRONE", (19, 17, 23), (43, 36, 44)),
]

_TEXT_CACHE: OrderedDict[tuple, pygame.Surface] = OrderedDict()
_TEXT_CACHE_MAX = 900


def clamp(value, low, high):
    return max(low, min(high, value))


def cached_text(font, text, color):
    key = (id(font), str(text), tuple(color))
    surf = _TEXT_CACHE.get(key)
    if surf is not None:
        _TEXT_CACHE.move_to_end(key)
        return surf
    surf = font.render(str(text), True, color).convert_alpha()
    _TEXT_CACHE[key] = surf
    if len(_TEXT_CACHE) > _TEXT_CACHE_MAX:
        _TEXT_CACHE.popitem(last=False)
    return surf


def text(surface, font, content, pos, color=PALE, anchor="topleft", shadow=True):
    img = cached_text(font, content, color)
    rect = img.get_rect()
    setattr(rect, anchor, (round(pos[0]), round(pos[1])))
    if shadow:
        shade = cached_text(font, content, (0, 0, 0))
        shadow_rect = shade.get_rect()
        setattr(shadow_rect, anchor, (round(pos[0]) + 2, round(pos[1]) + 2))
        surface.blit(shade, shadow_rect)
    surface.blit(img, rect)
    return rect


def panel(surface, rect, fill=(15, 18, 18, 238), border=(102, 88, 61), radius=9, width=1):
    layer = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(layer, fill, layer.get_rect(), border_radius=radius)
    pygame.draw.rect(layer, border, layer.get_rect(), width, border_radius=radius)
    surface.blit(layer, rect.topleft)


def bar(surface, rect, value, maximum, color, back=(35, 36, 34), outline=(94, 86, 70)):
    pygame.draw.rect(surface, back, rect, border_radius=5)
    inner = rect.inflate(-4, -4)
    pct = clamp(value / max(1, maximum), 0.0, 1.0)
    if pct > 0:
        inner.width = max(1, int(inner.width * pct))
        pygame.draw.rect(surface, color, inner, border_radius=4)
        shine = pygame.Rect(inner.x, inner.y, inner.width, max(2, inner.height // 3))
        pygame.draw.rect(surface, tuple(min(255, c + 22) for c in color), shine, border_radius=3)
    pygame.draw.rect(surface, outline, rect, 1, border_radius=5)


def glow(surface, point, radius, color, alpha=70):
    r = int(radius)
    if r <= 0:
        return
    layer = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(layer, (*color, int(alpha * 0.17)), (r, r), r)
    pygame.draw.circle(layer, (*color, int(alpha * 0.25)), (r, r), int(r * .68))
    pygame.draw.circle(layer, (*color, int(alpha * 0.35)), (r, r), int(r * .38))
    surface.blit(layer, (int(point[0] - r), int(point[1] - r)), special_flags=pygame.BLEND_PREMULTIPLIED)


def segment_distance_sq(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    denom = dx * dx + dy * dy
    if denom <= 0.0001:
        return (px - x1) ** 2 + (py - y1) ** 2
    t = clamp(((px - x1) * dx + (py - y1) * dy) / denom, 0.0, 1.0)
    x, y = x1 + t * dx, y1 + t * dy
    return (px - x) ** 2 + (py - y) ** 2


@dataclass
class Platform:
    x: float
    y: float
    w: float
    h: float
    kind: str = "stone"

    @property
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), round(self.w), round(self.h))


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    size: float
    color: tuple
    gravity: float = 0.0

    def update(self, dt):
        self.life -= dt
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= max(0.0, 1.0 - dt * 1.7)
        return self.life > 0

    def draw(self, surface, camera_x):
        alpha = clamp(self.life / .55, 0, 1)
        r = max(1, int(self.size * (0.35 + alpha * 0.65)))
        color = tuple(int(c * (0.38 + .62 * alpha)) for c in self.color)
        pygame.draw.circle(surface, color, (int(self.x - camera_x), int(self.y)), r)


class Enemy:
    serial = 0

    def __init__(self, x, y, kind="Hollow", hp=60):
        Enemy.serial += 1
        self.uid = Enemy.serial
        self.x, self.y = float(x), float(y)
        self.kind = kind
        self.boss = kind == "Grave Warden"
        self.archer = kind == "Ash Archer"
        self.w = 68 if self.boss else (31 if self.archer else 34)
        self.h = 82 if self.boss else (48 if self.archer else 52)
        self.hp_max = hp * (1.0 if self.boss else 1.0)
        self.hp = float(self.hp_max)
        self.vx = 0.0
        self.vy = 0.0
        self.facing = -1
        self.grounded = False
        self.state = "idle"
        self.state_time = random.uniform(0.1, 0.6)
        self.attack_cooldown = random.uniform(.2, .7)
        self.hit_flash = 0.0
        self.invuln = 0.0
        self.attack_done = False
        self.dead = False
        self.death_time = 0.0
        self.projectile_clock = random.uniform(.6, 1.4)
        self.phase = 1
        self.spawn_x = x

    @property
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.w, self.h)

    @property
    def center(self):
        return Vector2(self.x + self.w / 2, self.y + self.h / 2)

    def hurt(self, damage, direction, game):
        if self.dead or self.invuln > 0:
            return False
        self.hp = max(0, self.hp - damage)
        self.hit_flash = .12
        self.invuln = .10 if not self.boss else .06
        self.vx = direction * (175 if not self.boss else 95)
        self.vy = -115 if not self.boss else -75
        self.state = "hurt"
        self.state_time = .16 if not self.boss else .10
        for _ in range(7 if not self.boss else 12):
            game.particles.append(Particle(
                self.x + self.w / 2, self.y + self.h * .48,
                random.uniform(-150, 150), random.uniform(-210, 30),
                random.uniform(.22, .48), random.uniform(2, 5),
                (244, 115, 77) if not self.boss else (255, 177, 102), 310
            ))
        game.floating.append(FloatingText(str(int(damage)), self.x + self.w / 2, self.y - 4, GOLD))
        if self.hp <= 0:
            self.dead = True
            self.state = "dead"
            self.death_time = .42
            game.kills += 1
            reward = 35 if self.boss else (12 if self.archer else 8)
            game.souls += reward
            game.soul_charge = min(game.soul_max, game.soul_charge + (35 if self.boss else 18))
            game.screen_shake = max(game.screen_shake, 12 if self.boss else 4)
            game.burst(self.x + self.w / 2, self.y + self.h / 2, (232, 131, 78), 24 if self.boss else 12)
            if self.boss:
                game.victory = True
                game.mode = "victory"
                game.message = "THE WARDEN HAS FALLEN"
                game.message_timer = 4.0
        return True

    def update(self, game, dt):
        if self.dead:
            self.death_time -= dt
            return self.death_time > 0
        self.hit_flash = max(0.0, self.hit_flash - dt)
        self.invuln = max(0.0, self.invuln - dt)
        self.state_time -= dt
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        self.projectile_clock -= dt
        player = game.player
        p_center = player.x + player.w / 2
        e_center = self.x + self.w / 2
        diff = p_center - e_center
        dist = abs(diff)
        self.facing = 1 if diff > 0 else -1

        # Independent gravity and platform collision keeps enemies grounded too.
        old_y = self.y
        if not self.grounded:
            self.vy += GRAVITY * dt
        self.y += self.vy * dt
        self._land(game.platforms, old_y)

        if self.state == "hurt":
            self.x += self.vx * dt
            self.vx *= max(0.0, 1.0 - dt * 8)
            if self.state_time <= 0:
                self.state = "idle"
            self.x = clamp(self.x, 0, WORLD_W - self.w)
            return True

        if self.boss:
            self.phase = 2 if self.hp < self.hp_max * .50 else 1
        if self.archer:
            if dist > 300:
                self.vx = self.facing * 90
            elif dist < 190:
                self.vx = -self.facing * 80
            else:
                self.vx *= max(0.0, 1 - dt * 4)
            self.x += self.vx * dt
            if self.state not in ("shoot", "recover") and self.projectile_clock <= 0 and dist < 650:
                self.state = "shoot"
                self.state_time = .42
                self.attack_done = False
            if self.state == "shoot":
                if self.state_time <= 0 and not self.attack_done:
                    self.attack_done = True
                    bolt_x = self.x + (self.w if self.facing > 0 else -12)
                    game.projectiles.append(Projectile(bolt_x, self.y + 19, self.facing * 340, 0, "enemy", 13))
                    self.state = "recover"
                    self.state_time = .65
                    self.projectile_clock = random.uniform(1.3, 1.8)
            elif self.state == "recover" and self.state_time <= 0:
                self.state = "idle"
            self.x = clamp(self.x, 0, WORLD_W - self.w)
            return True

        # Melee enemies show a clear wind-up before the attack becomes active.
        aggro = 480 if not self.boss else 780
        attack_dist = 73 if not self.boss else (118 if self.phase == 1 else 142)
        if dist < aggro and self.state in ("idle", "move"):
            if dist > attack_dist:
                speed = 95 if not self.boss else (105 if self.phase == 1 else 155)
                if self.grounded and not self._ground_ahead(game.platforms, self.facing):
                    # Enemies hold the edge rather than blindly walking into a pit.
                    self.vx = 0
                    self.state = "idle"
                else:
                    self.vx = self.facing * speed
                    self.x += self.vx * dt
                    self.state = "move"
            elif self.attack_cooldown <= 0:
                self.state = "windup"
                self.state_time = .56 if self.boss else .40
                if self.boss and self.phase == 2:
                    self.state_time = .38
                self.attack_done = False
                self.vx = 0
            else:
                self.vx = 0
                self.state = "idle"
        else:
            self.vx *= max(0.0, 1 - dt * 5)
            if self.state not in ("windup", "attack", "recover"):
                self.state = "idle"
        if self.state == "windup" and self.state_time <= 0:
            self.state = "attack"
            self.state_time = .18 if not self.boss else (.32 if self.phase == 2 else .26)
        elif self.state == "attack":
            # Active contact window; boss has a longer and wider swipe.
            reach = 70 if not self.boss else (130 if self.phase == 2 else 110)
            if not self.attack_done:
                target = pygame.Rect(round(self.x + (self.w if self.facing > 0 else -reach)),
                                     round(self.y + 10), reach, self.h - 12)
                if target.colliderect(player.rect) and player.hurt_invuln <= 0:
                    player.take_damage(15 if not self.boss else (27 if self.phase == 2 else 22), self.facing, game)
                self.attack_done = True
            if self.state_time <= 0:
                self.state = "recover"
                self.state_time = .54 if not self.boss else .72
                self.attack_cooldown = random.uniform(.42, .72) if not self.boss else (1.05 if self.phase == 1 else .78)
        elif self.state == "recover" and self.state_time <= 0:
            self.state = "idle"
        self.x = clamp(self.x, 0, WORLD_W - self.w)
        return True

    def _ground_ahead(self, platforms, direction):
        probe_x = self.x + self.w + 14 if direction > 0 else self.x - 14
        feet = self.y + self.h
        for plat in platforms:
            if plat.x <= probe_x <= plat.x + plat.w:
                if feet - 62 <= plat.y <= feet + 24:
                    return True
        return False

    def _land(self, platforms, old_y):
        self.grounded = False
        if self.vy >= 0:
            for plat in platforms:
                horizontal_overlap = self.x + self.w > plat.x + 2 and self.x < plat.x + plat.w - 2
                crossed_top = old_y + self.h <= plat.y + 5 and self.y + self.h >= plat.y
                if horizontal_overlap and crossed_top:
                    self.y = plat.y - self.h
                    self.vy = 0
                    self.grounded = True
                    break

    def draw(self, surface, camera_x, now):
        sx = int(self.x - camera_x)
        sy = int(self.y)
        if sx < -150 or sx > W + 150:
            return
        if self.dead:
            return
        # Shadow, body silhouette and readable telegraphs.
        shadow = pygame.Rect(sx + 2, sy + self.h - 5, self.w - 4, 10)
        pygame.draw.ellipse(surface, (10, 12, 13), shadow)
        if self.state == "windup":
            pulse = 0.5 + 0.5 * math.sin(now * 22)
            color = (190, 57, 48) if pulse > .2 else (112, 39, 37)
            lead = 72 if not self.boss else 130
            yline = sy + self.h - 12
            if self.facing > 0:
                pygame.draw.polygon(surface, (*color, 35), [(sx+self.w, yline-25), (sx+self.w+lead, yline-8), (sx+self.w+lead, yline+3), (sx+self.w, yline+7)])
                pygame.draw.line(surface, color, (sx+self.w, yline), (sx+self.w+lead, yline), 3)
            else:
                pygame.draw.line(surface, color, (sx, yline), (sx-lead, yline), 3)
        if self.boss:
            cloak = [(int(sx + self.w*.10), sy+28),(int(sx+self.w*.40),sy+15),(int(sx+self.w*.70),sy+25),(int(sx+self.w*.98),sy+self.h-4),(int(sx+self.w*.06),sy+self.h-4)]
            pygame.draw.polygon(surface, (44, 28, 31), cloak)
            pygame.draw.ellipse(surface, (96, 55, 47), (sx+12,sy+6,self.w-24,45))
            pygame.draw.ellipse(surface, (224, 141, 88), (sx+22,sy+22,8,5))
            pygame.draw.ellipse(surface, (224, 141, 88), (sx+self.w-30,sy+22,8,5))
            # Crown-like silhouette.
            pygame.draw.lines(surface, (134, 107, 72), False, [(sx+13,sy+12),(sx+5,sy-2),(sx+22,sy+7),(sx+34,sy-8),(sx+43,sy+8),(sx+57,sy-3),(sx+58,sy+14)], 3)
        elif self.archer:
            pygame.draw.polygon(surface,(74,66,53),[(sx+4,sy+15),(sx+self.w-4,sy+12),(sx+self.w-2,sy+self.h-5),(sx+4,sy+self.h-5)])
            pygame.draw.circle(surface,(143,119,87),(sx+self.w//2,sy+11),12)
            pygame.draw.line(surface,(186,142,86),(sx+8,sy+18),(sx+self.w-3,sy+37),3)
            pygame.draw.line(surface,(220,201,156),(sx+self.w//2,sy+17),(sx+self.w//2+self.facing*8,sy+27),2)
        else:
            pygame.draw.polygon(surface,(79,62,56),[(sx+4,sy+13),(sx+self.w-4,sy+13),(sx+self.w-1,sy+self.h-4),(sx+1,sy+self.h-4)])
            pygame.draw.circle(surface,(151,112,80),(sx+self.w//2,sy+12),13)
            pygame.draw.line(surface,(181,154,103),(sx+10,sy+31),(sx+self.w-8,sy+39),4)
        if self.hit_flash > 0:
            pygame.draw.rect(surface,(242,226,185),self.rect.move(-round(camera_x),0),2,border_radius=4)
        hpw = self.w + (28 if self.boss else 0)
        hp_x = sx + self.w/2 - hpw/2
        hp_y = sy - (18 if self.boss else 12)
        pygame.draw.rect(surface,(27,26,24),(int(hp_x),int(hp_y),hpw,6),border_radius=3)
        if self.hp > 0:
            pygame.draw.rect(surface,(194,65,56),(int(hp_x+1),int(hp_y+1),max(1,int((hpw-2)*self.hp/self.hp_max)),4),border_radius=2)


class Projectile:
    def __init__(self, x, y, vx, vy, faction, damage, color=None):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = float(vx), float(vy)
        self.faction = faction
        self.damage = damage
        self.color = color or ((228, 102, 71) if faction == "enemy" else GOLD)
        self.life = 2.8
        self.r = 7 if faction == "enemy" else 10

    def update(self, game, dt):
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.faction == "enemy" and self.life > 0:
            if game.player.rect.collidepoint(self.x, self.y) and game.player.hurt_invuln <= 0:
                game.player.take_damage(self.damage, 1 if self.vx > 0 else -1, game)
                self.life = 0
        elif self.faction == "player":
            for enemy in game.enemies:
                if not enemy.dead and enemy.rect.collidepoint(self.x, self.y):
                    enemy.hurt(self.damage, 1 if self.vx > 0 else -1, game)
                    self.life = 0
                    break
        return self.life > 0 and -60 < self.x < WORLD_W + 60 and -100 < self.y < H + 200

    def draw(self, surface, camera_x):
        x, y = int(self.x - camera_x), int(self.y)
        glow(surface, (x, y), 17 if self.faction == "enemy" else 22, self.color, 55)
        pygame.draw.circle(surface, self.color, (x, y), self.r)
        pygame.draw.circle(surface, (255, 231, 189), (x, y), max(2, self.r//2))


class FloatingText:
    def __init__(self, content, x, y, color=GOLD):
        self.content, self.x, self.y = content, x, y
        self.color, self.life = color, .72

    def update(self, dt):
        self.life -= dt
        self.y -= 43 * dt
        return self.life > 0

    def draw(self, surface, game):
        screen_x = self.x - game.camera_x
        if -80 < screen_x < W + 80:
            text(surface, game.font_small, self.content, (screen_x, self.y), self.color, anchor="center")


class Player:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.w, self.h = 31, 56
        self.vx = self.vy = 0.0
        self.facing = 1
        self.grounded = False
        self.coyote = 0.0
        self.jump_buffer = 0.0
        self.jumps_left = 2
        self.hp_max = 130
        self.hp = 130.0
        self.stamina_max = 100
        self.stamina = 100.0
        self.soul_max = 100
        self.soul_charge = 72.0
        self.invuln = 0.0
        self.hurt_invuln = 0.0
        self.dash_time = 0.0
        self.dash_cd = 0.0
        self.attack_kind = ""
        self.attack_time = 0.0
        self.attack_duration = 0.0
        self.attack_dir = 1
        self.attack_hit = set()
        self.attack_buffer = 0.0
        self.heavy_buffer = 0.0
        self.combo = 0
        self.combo_timer = 0.0
        self.attack_cd = 0.0
        self.skill_cd = 0.0
        self.skill_timer = 0.0
        self.skill_hit = set()
        self.anim_time = 0.0
        self.dead = False
        self.souls = 0
        self.stamina_exhausted = 0.0

    @property
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.w, self.h)

    @property
    def center(self):
        return Vector2(self.x + self.w/2, self.y + self.h/2)

    def take_damage(self, amount, direction, game):
        if self.invuln > 0 or self.dead:
            return
        self.hp = max(0, self.hp - amount)
        self.invuln = .75
        self.hurt_invuln = .75
        self.vx = direction * -265
        self.vy = -330
        self.attack_kind = ""
        self.attack_time = 0
        self.attack_buffer = 0
        self.heavy_buffer = 0
        game.screen_shake = max(game.screen_shake, 9)
        game.burst(self.x + self.w/2, self.y + self.h/2, (204, 62, 56), 18)
        game.message = "WOUNDED"
        game.message_timer = .7
        if self.hp <= 0:
            self.dead = True
            game.message = "YOU HAVE FALLEN"
            game.message_timer = 99

    def begin_attack(self, kind, game):
        weapon = WEAPONS[game.weapon]
        if self.dead or self.dash_time > 0 or self.attack_cd > 0:
            return False
        if kind == "light":
            cost = weapon["stamina"]
            if self.stamina < cost:
                self.stamina_exhausted = .45
                return False
            self.stamina -= cost
            self.combo = (self.combo + 1) % (3 if game.weapon != "Gravetide" else 4)
            self.attack_duration = weapon["windup"] + weapon["active"] + weapon["recovery"]
            self.attack_cd = weapon["windup"] + weapon["active"] + weapon["recovery"]
            self.attack_time = 0
            self.attack_kind = "light"
        elif kind == "heavy":
            if self.stamina < weapon["heavy_cost"]:
                self.stamina_exhausted = .45
                return False
            self.stamina -= weapon["heavy_cost"]
            self.attack_duration = weapon["heavy_windup"] + weapon["heavy_active"] + weapon["heavy_recovery"]
            self.attack_cd = self.attack_duration
            self.attack_time = 0
            self.attack_kind = "heavy"
        elif kind == "skill":
            if self.skill_cd > 0 or self.stamina < weapon["skill_cost"]:
                return False
            self.stamina -= weapon["skill_cost"]
            self.skill_cd = weapon["skill_cd"]
            self.attack_duration = .42
            self.attack_cd = .42
            self.attack_time = 0
            self.attack_kind = "skill"
            self.skill_hit.clear()
            if game.weapon == "Rookfang":
                self.vx = self.facing * 720
                self.invuln = max(self.invuln, .22)
                self.skill_timer = .22
            elif game.weapon == "Gravetide":
                self.vx = self.facing * 390
                self.skill_timer = .24
            else:
                self.skill_timer = .32
        self.attack_dir = self.facing
        self.attack_hit.clear()
        self.attack_buffer = 0
        self.heavy_buffer = 0
        self.combo_timer = weapon["combo"]
        self.anim_time = 0
        return True

    def update(self, game, dt, keys):
        self.anim_time += dt
        self.invuln = max(0.0, self.invuln - dt)
        self.hurt_invuln = max(0.0, self.hurt_invuln - dt)
        self.dash_cd = max(0.0, self.dash_cd - dt)
        self.skill_cd = max(0.0, self.skill_cd - dt)
        self.attack_cd = max(0.0, self.attack_cd - dt)
        if not self.attack_kind:
            self.attack_buffer = max(0.0, self.attack_buffer - dt)
            self.heavy_buffer = max(0.0, self.heavy_buffer - dt)
        self.combo_timer = max(0.0, self.combo_timer - dt)
        self.stamina_exhausted = max(0.0, self.stamina_exhausted - dt)
        if self.combo_timer <= 0 and not self.attack_kind:
            self.combo = 0
        if self.grounded and self.dash_time <= 0:
            self.coyote = .12
            self.jumps_left = 2
        else:
            self.coyote = max(0.0, self.coyote - dt)
        self.jump_buffer = max(0.0, self.jump_buffer - dt)
        self.skill_timer = max(0.0, self.skill_timer - dt)

        move = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        if move and self.dash_time <= 0:
            self.facing = 1 if move > 0 else -1
        if self.dash_time <= 0:
            target_speed = move * (320 if not self.attack_kind else 270)
            accel = 2350 if move else 2600
            self.vx += clamp(target_speed - self.vx, -accel * dt, accel * dt)
            if not move and abs(self.vx) < 10:
                self.vx = 0
        else:
            self.dash_time = max(0.0, self.dash_time - dt)
            self.vx = self.facing * 680
            if self.dash_time <= 0:
                self.vx = self.facing * 285

        if self.grounded and self.vy > 0:
            self.vy = 0
        if self.dash_time <= 0:
            self.vy = min(1000, self.vy + GRAVITY * dt)
        else:
            self.vy = 0

        # Horizontal collision with the world bounds; platform collision is resolved vertically.
        old_x = self.x
        self.x += self.vx * dt
        self.x = clamp(self.x, 0, WORLD_W - self.w)
        # Prevent walking through cliff-side blockers (solid walls) only.
        self._resolve_horizontal(game.platforms, old_x)

        old_y = self.y
        self.y += self.vy * dt
        self.grounded = False
        if self.vy >= 0:
            for plat in game.platforms:
                if self.x + self.w > plat.x + 3 and self.x < plat.x + plat.w - 3:
                    old_bottom = old_y + self.h
                    new_bottom = self.y + self.h
                    if old_bottom <= plat.y + 4 and new_bottom >= plat.y and self.vy >= 0:
                        self.y = plat.y - self.h
                        self.vy = 0
                        self.grounded = True
        elif self.vy < 0:
            # Ceilings are solid, tops are one-way platforms.
            old_top = old_y
            new_top = self.y
            for plat in game.platforms:
                if self.x + self.w > plat.x + 3 and self.x < plat.x + plat.w - 3:
                    if old_top >= plat.y + plat.h - 3 and new_top <= plat.y + plat.h:
                        self.y = plat.y + plat.h
                        self.vy = 0

        if self.jump_buffer > 0 and (self.coyote > 0 or self.jumps_left > 0):
            if self.coyote > 0:
                self.vy = -720
                self.jumps_left = max(0, self.jumps_left - 1)
            else:
                self.vy = -680
                self.jumps_left -= 1
            self.grounded = False
            self.coyote = 0
            self.jump_buffer = 0
            game.burst(self.x + self.w/2, self.y + self.h, (151, 151, 133), 4)

        # Attacks update independently from movement; active swings can hit once per target.
        if self.attack_kind:
            self.attack_time += dt
            self._attack_hits(game)
            if self.attack_time >= self.attack_duration:
                self.attack_kind = ""
                self.attack_time = 0
        else:
            # Heavy inputs have priority, and taps remain queued until recovery ends.
            mouse_held = game.mouse_buttons[0]
            if self.heavy_buffer > 0 and self.attack_cd <= 0:
                self.begin_attack("heavy", game)
            elif (self.attack_buffer > 0 or mouse_held) and self.attack_cd <= 0:
                self.begin_attack("light", game)

        if self.grounded and not self.attack_kind:
            self.stamina = min(self.stamina_max, self.stamina + 31 * dt)
        else:
            self.stamina = min(self.stamina_max, self.stamina + 15 * dt)

        # Checkpoint-aware fall recovery.
        if self.y > H + 330:
            self.x = game.checkpoint_x
            self.y = FLOOR_Y - self.h - 2
            self.vx = self.vy = 0
            self.hp = max(25, self.hp - 25)
            self.invuln = self.hurt_invuln = 1.0
            game.screen_shake = 8

    def _resolve_horizontal(self, platforms, old_x):
        # These are world-edge rails, and only platforms marked "wall" block sideways.
        new_rect = self.rect
        for p in platforms:
            if p.kind != "wall":
                continue
            pr = p.rect
            if new_rect.colliderect(pr):
                if self.vx > 0 and old_x + self.w <= p.x:
                    self.x = p.x - self.w
                elif self.vx < 0 and old_x >= p.x + p.w:
                    self.x = p.x + p.w

    def _attack_hits(self, game):
        weapon = WEAPONS[game.weapon]
        t = self.attack_time
        kind = self.attack_kind
        if kind == "light":
            start, active = weapon["windup"], weapon["active"]
            reach, height = weapon["reach"], weapon["height"]
            damage = weapon["damage"] * (1.0 + .12 * self.combo)
        elif kind == "heavy":
            start, active = weapon["heavy_windup"], weapon["heavy_active"]
            reach, height = weapon["heavy_reach"], weapon["height"] + 14
            damage = weapon["heavy_damage"]
        else:
            start, active = .07, .23 if game.weapon != "Oathbreaker" else .27
            reach, height = weapon["reach"] * (1.6 if game.weapon == "Rookfang" else 1.45), weapon["height"] + 18
            damage = weapon["damage"] * (2.2 if game.weapon != "Oathbreaker" else 1.8)
        if not (start <= t <= start + active):
            return
        center_y = self.y + self.h * .55
        if kind == "skill" and game.weapon == "Oathbreaker":
            reach *= 1.2
            center_y += 12
        x1 = self.x + self.w/2 + self.attack_dir * 9
        x2 = x1 + self.attack_dir * reach
        # Melee hit scan tests target center to the full segment, not a single instant.
        for enemy in game.enemies:
            if enemy.dead or enemy.uid in self.attack_hit:
                continue
            ec = enemy.center
            vertical_ok = abs(ec.y - center_y) <= height * .72 + enemy.h * .22
            horizontal_ok = (ec.x - x1) * self.attack_dir >= -9 and (ec.x - x1) * self.attack_dir <= reach + enemy.w * .5
            segment_ok = segment_distance_sq(ec.x, ec.y, x1, center_y, x2, center_y) <= (height * .46 + enemy.w * .12) ** 2
            if vertical_ok and horizontal_ok and segment_ok:
                if enemy.hurt(damage, self.attack_dir, game):
                    self.attack_hit.add(enemy.uid)
                    game.screen_shake = max(game.screen_shake, 5 if kind == "heavy" else 2)
                    game.burst(ec.x, ec.y, weapon["color"], 7)
        # Visual slash lines are collected while the active state is running.
        if kind == "skill" and game.weapon == "Rookfang" and self.skill_timer > 0:
            self.vx = self.attack_dir * 620
        if kind == "skill" and game.weapon == "Oathbreaker" and self.grounded:
            game.shockwave = max(game.shockwave, .20)

    def draw(self, surface, camera_x, game):
        sx, sy = int(self.x-camera_x), int(self.y)
        if sx < -120 or sx > W + 120:
            return
        # Ground shadow.
        pygame.draw.ellipse(surface, (10, 12, 13), (sx-4, sy+self.h-5, self.w+8, 10))
        flicker = math.sin(self.anim_time * 8) * 1.1
        # Cloak silhouette and torso.
        cloak = [(sx+5, sy+15), (sx+self.w-4, sy+13), (sx+self.w+2, sy+self.h-3), (sx-2, sy+self.h-3)]
        pygame.draw.polygon(surface, (26, 31, 34), cloak)
        pygame.draw.polygon(surface, (61, 59, 50), [(sx+8,sy+18),(sx+self.w-5,sy+18),(sx+self.w-5,sy+43),(sx+7,sy+43)])
        # Shoulder plates.
        pygame.draw.circle(surface, (92, 83, 64), (sx+8, sy+23), 6)
        pygame.draw.circle(surface, (92, 83, 64), (sx+self.w-7, sy+23), 6)
        # Head and luminous visor.
        pygame.draw.ellipse(surface, (128, 113, 83), (sx+7, sy+1, self.w-14, 26))
        visor_y = sy + 12 + int(flicker)
        pygame.draw.line(surface, (246, 199, 110), (sx+11, visor_y), (sx+self.w-9, visor_y), 4)
        pygame.draw.line(surface, (255, 240, 188), (sx+13, visor_y), (sx+self.w-13, visor_y), 1)
        # Weapon on idle and distinctive attack sweeps during active frames.
        weapon = WEAPONS[game.weapon]
        if self.attack_kind:
            t = self.attack_time
            active_start = weapon["windup"] if self.attack_kind == "light" else weapon["heavy_windup"] if self.attack_kind == "heavy" else .07
            active_dur = weapon["active"] if self.attack_kind == "light" else weapon["heavy_active"] if self.attack_kind == "heavy" else .23
            phase = clamp((t-active_start)/max(.01,active_dur),0,1)
            if active_start <= t <= active_start + active_dur:
                arc_r = weapon["reach"] * (1.15 if self.attack_kind == "heavy" else 1.0)
                base_x = sx + self.w/2 + self.attack_dir * 8
                base_y = sy + self.h*.52
                for k in range(4):
                    f = k/3
                    end_x = base_x + self.attack_dir * arc_r * (.45 + .55*phase) 
                    end_y = base_y + math.sin((phase+f)*math.pi) * (36 + 8*k) - 10*k
                    col = tuple(max(0,int(c*(.40+.18*k))) for c in weapon["color"])
                    start_point = (int(base_x), int(base_y))
                    end_point = (int(end_x), int(end_y))
                    pygame.draw.line(surface, col, start_point, end_point, max(1,5-k))
                    pygame.draw.line(surface, tuple(min(255,c+28) for c in col), start_point, end_point, 1)
        else:
            hand = (sx + (self.w-2 if self.facing > 0 else 2), sy+32)
            reach = 34 if game.weapon != "Oathbreaker" else 41
            end = (hand[0] + self.facing*reach, hand[1] + 2)
            pygame.draw.line(surface, (98,76,55), hand, end, 5 if game.weapon == "Oathbreaker" else 3)
            pygame.draw.line(surface, weapon["color"], (hand[0],hand[1]-1), (end[0],end[1]-1), 3 if game.weapon != "Gravetide" else 2)
            pygame.draw.circle(surface, (250,223,161), end, 2)
        if self.invuln > .02 and int(self.invuln*22)%2 == 0:
            pygame.draw.ellipse(surface, (235,225,186), (sx-4,sy-3,self.w+8,self.h+6),2)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("ASHEN VEIL | 2D Dark-Fantasy Metroidvania")
        self.window = pygame.display.set_mode((W, H), pygame.RESIZABLE)
        self.canvas = pygame.Surface((W, H)).convert()
        self.world_layer = pygame.Surface((W, H), pygame.SRCALPHA)
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont("georgia", 58, bold=True)
        self.font_h1 = pygame.font.SysFont("georgia", 27, bold=True)
        self.font_ui = pygame.font.SysFont("consolas", 16, bold=True)
        self.font_small = pygame.font.SysFont("consolas", 13)
        self.font_tiny = pygame.font.SysFont("consolas", 11)
        self.running = True
        self.mode = "title"
        self.paused = False
        self.weapon = "Rookfang"
        self.build_world()
        self.player = Player(120, FLOOR_Y-58)
        self.camera_x = 0.0
        self.enemies = []
        self.projectiles = []
        self.particles = []
        self.floating = []
        self.spawn_enemies()
        self.souls = 0
        self.kills = 0
        self.checkpoint_x = 120.0
        self.checkpoints = [False, False, False]
        self.screen_shake = 0.0
        self.shockwave = 0.0
        self.message = ""
        self.message_timer = 0.0
        self.victory = False
        self.mouse_buttons = (False, False, False)
        self.mouse_pos = (W//2,H//2)
        self.light_tap = False
        self.heavy_tap = False
        self.jump_tap = False
        self.skill_tap = False
        self.soul_tap = False
        self.restart_tap = False
        self.fullscreen = False
        self.elapsed = 0.0
        self.fps_value = FPS
        self.decor = self.build_decor()

    def build_world(self):
        self.platforms = []
        # Platforms and floor segments form one traversable side-scrolling route.
        floors = [(-80, 0, 770), (875, 0, 555), (1500, 0, 1060), (2660, 0, 1040), (3770, 0, 1230)]
        # y coordinate, x coordinate, width, height; gaps must be jumped.
        for x, _unused, width in floors:
            y = FLOOR_Y if x not in (875, 2660, 3770) else (FLOOR_Y+4 if x == 2660 else FLOOR_Y)
            self.platforms.append(Platform(x, y, width, 160, "floor"))
        self.platforms += [
            Platform(188, 584, 172, 18), Platform(452, 505, 166, 18), Platform(650, 612, 112, 18),
            Platform(936, 566, 215, 18), Platform(1188, 488, 186, 18), Platform(1392, 595, 126, 18),
            Platform(1616, 580, 194, 18), Platform(1854, 503, 192, 18), Platform(2070, 570, 145, 18),
            Platform(2326, 465, 206, 18), Platform(2490, 583, 145, 18),
            Platform(2715, 574, 192, 18), Platform(2938, 500, 184, 18), Platform(3160, 420, 170, 18),
            Platform(3350, 568, 160, 18), Platform(3575, 475, 196, 18), Platform(3826, 575, 175, 18),
            Platform(4044, 493, 190, 18), Platform(4290, 560, 160, 18), Platform(4490, 488, 190, 18),
        ]
        # Arena pillars are scenery only, never invisible walls.
        self.world_width = WORLD_W

    def build_decor(self):
        rng = random.Random(8142)
        deco = {"towers":[],"chains":[],"candles":[],"runes":[],"embers":[]}
        x=-100
        while x < WORLD_W+400:
            deco["towers"].append((x, rng.randint(210,410), rng.randint(70,150), rng.randint(90,240), rng.choice([(29,32,34),(36,34,35),(31,35,38)])))
            x += rng.randint(220,420)
        for _ in range(16):
            deco["chains"].append((rng.randint(80,WORLD_W-80),rng.randint(70,400),rng.randint(50,170)))
        for x in [95, 410, 740, 1035, 1350, 1690, 1985, 2285, 2600, 2910, 3210, 3520, 3860, 4180, 4510, 4780]:
            deco["candles"].append((x, FLOOR_Y-6))
        for _ in range(56):
            deco["embers"].append([rng.uniform(0,WORLD_W),rng.uniform(100,H-90),rng.uniform(-9,9),rng.uniform(4,20),rng.uniform(0,math.tau)])
        return deco

    def spawn_enemies(self):
        self.enemies = [
            Enemy(485, FLOOR_Y-52, "Hollow", 54), Enemy(1030, FLOOR_Y-52,"Hollow",66),
            Enemy(1218, FLOOR_Y-48,"Ash Archer",40), Enemy(1715,FLOOR_Y-52,"Hollow",68),
            Enemy(2020,FLOOR_Y-52,"Hollow",68), Enemy(2440,FLOOR_Y-52,"Ash Archer",46),
            Enemy(2775,FLOOR_Y+4-52,"Hollow",75), Enemy(2990,FLOOR_Y+4-52,"Hollow",78),
            Enemy(3500,FLOOR_Y-52,"Ash Archer",52), Enemy(3890,FLOOR_Y-52,"Hollow",86),
            Enemy(4350,FLOOR_Y-82,"Grave Warden",440),
        ]

    def reset(self):
        self.build_world()
        self.player = Player(120, FLOOR_Y-58)
        self.camera_x = 0.0
        self.spawn_enemies()
        self.projectiles.clear()
        self.particles.clear()
        self.floating.clear()
        self.souls = 0
        self.kills = 0
        self.checkpoint_x = 120.0
        self.checkpoints = [False, False, False]
        self.screen_shake = 0.0
        self.shockwave = 0.0
        self.message = ""
        self.message_timer = 0
        self.victory = False
        self.mode = "play"
        self.paused = False
        self.weapon = "Rookfang"

    def burst(self, x, y, color, amount=10):
        for _ in range(amount):
            a = random.uniform(0,math.tau)
            speed = random.uniform(35,240)
            self.particles.append(Particle(x,y,math.cos(a)*speed,math.sin(a)*speed,random.uniform(.20,.60),random.uniform(1.5,4.4),color,random.uniform(30,290)))

    def change_weapon(self, idx):
        self.weapon = WEAPON_ORDER[idx]
        self.message = WEAPONS[self.weapon]["title"]
        self.message_timer = 1.0
        self.burst(self.player.x+self.player.w/2,self.player.y+self.player.h/2,WEAPONS[self.weapon]["color"],6)

    def handle_events(self):
        self.light_tap = self.heavy_tap = self.jump_tap = False
        self.skill_tap = self.soul_tap = self.restart_tap = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.window = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.mode == "play":
                        self.paused = not self.paused
                    elif self.mode in ("dead","victory"):
                        self.mode = "title"
                if event.key == pygame.K_F11:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.window = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
                    else:
                        self.window = pygame.display.set_mode((W,H), pygame.RESIZABLE)
                if self.mode == "title" and event.key in (pygame.K_RETURN,pygame.K_SPACE):
                    self.reset()
                elif self.mode in ("dead","victory") and event.key in (pygame.K_r,pygame.K_RETURN,pygame.K_SPACE):
                    self.reset()
                    self.restart_tap = True
                elif self.mode == "play" and not self.paused:
                    if event.key in (pygame.K_w,pygame.K_UP,pygame.K_SPACE):
                        self.jump_tap = True
                    elif event.key == pygame.K_1: self.change_weapon(0)
                    elif event.key == pygame.K_2: self.change_weapon(1)
                    elif event.key == pygame.K_3: self.change_weapon(2)
                    elif event.key == pygame.K_e: self.skill_tap = True
                    elif event.key == pygame.K_q: self.soul_tap = True
                    elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        self.try_dash()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.light_tap = True
                elif event.button == 3:
                    self.heavy_tap = True
                if self.mode == "title":
                    self.reset()
                elif self.mode in ("dead","victory"):
                    self.reset()
                elif self.paused and event.button == 1:
                    self.paused = False
            elif event.type == pygame.MOUSEMOTION:
                pass
        buttons = pygame.mouse.get_pressed(3)
        self.mouse_buttons = buttons
        mx,my = pygame.mouse.get_pos()
        window_w,window_h = self.window.get_size()
        if window_w > 0 and window_h > 0:
            self.mouse_pos = (mx * W / window_w, my * H / window_h)
        if self.mode == "play" and not self.paused:
            player = self.player
            if self.light_tap:
                player.attack_buffer = .22
                # Mouse-side aiming is deliberate; when cursor is close, retain movement-facing.
                world_mouse_x = self.mouse_pos[0] + self.camera_x
                if abs(world_mouse_x - (player.x+player.w/2)) > 16:
                    player.facing = 1 if world_mouse_x > player.x+player.w/2 else -1
            if self.heavy_tap:
                player.heavy_buffer = .28
                world_mouse_x = self.mouse_pos[0] + self.camera_x
                if abs(world_mouse_x - (player.x+player.w/2)) > 16:
                    player.facing = 1 if world_mouse_x > player.x+player.w/2 else -1
            if self.jump_tap:
                player.jump_buffer = .16
            if self.skill_tap:
                player.begin_attack("skill",self)
            if self.soul_tap:
                self.soul_burst()

    def try_dash(self):
        if self.mode != "play" or self.paused:
            return
        p = self.player
        if p.dash_cd <= 0 and p.stamina >= 22 and not p.dead:
            p.stamina -= 22
            p.dash_time = .20
            p.dash_cd = .65
            p.invuln = max(p.invuln,.22)
            p.hurt_invuln = max(p.hurt_invuln,.22)
            p.attack_kind = ""
            p.attack_cd = max(0,p.attack_cd-.12)
            self.burst(p.x+p.w/2,p.y+p.h*.7,(176,180,161),7)

    def soul_burst(self):
        p=self.player
        if p.soul_charge < 45 or p.dead:
            self.message="SOUL CHARGE INSUFFICIENT"
            self.message_timer=.8
            return
        p.soul_charge-=45
        center_x=p.x+p.w/2+p.facing*50
        center_y=p.y+p.h/2
        self.burst(center_x,center_y,(245,196,106),35)
        self.screen_shake=max(self.screen_shake,7)
        # Grounded shockwave travels forward; generous radius vertically for platform combat.
        for enemy in self.enemies:
            if enemy.dead: continue
            dx=enemy.center.x-center_x
            dy=abs(enemy.center.y-center_y)
            if dx*p.facing>=-40 and dx*p.facing<=300 and dy<115:
                enemy.hurt(54 if not enemy.boss else 70,p.facing,self)
        for direction in (-1,1):
            self.projectiles.append(Projectile(center_x,center_y,p.facing*direction*520,0,"player",28,(255,213,119)))

    def update(self, dt):
        self.elapsed += dt
        self.message_timer=max(0,self.message_timer-dt)
        self.shockwave=max(0,self.shockwave-dt)
        if self.mode != "play" or self.paused:
            return
        keys=pygame.key.get_pressed()
        self.player.update(self,dt,keys)
        if self.player.dead:
            self.mode="dead"
            return
        # Checkpoint shrines give a forgiving respawn in the connected world.
        for i, cp_x in enumerate((1280, 2700, 3820)):
            if not self.checkpoints[i] and self.player.x >= cp_x:
                self.checkpoints[i]=True
                self.checkpoint_x=cp_x+30
                self.player.hp=min(self.player.hp_max,self.player.hp+42)
                self.player.stamina=self.player.stamina_max
                self.message="VEIL SHRINE — CHECKPOINT RESTORED"
                self.message_timer=2.2
                self.burst(cp_x,FLOOR_Y-22,GOLD,26)
        self.enemies=[e for e in self.enemies if e.update(self,dt)]
        self.projectiles=[p for p in self.projectiles if p.update(self,dt)]
        self.particles=[p for p in self.particles if p.update(dt)]
        self.floating=[f for f in self.floating if f.update(dt)]
        # Keep camera just behind the player; easing makes direction changes smooth.
        target=clamp(self.player.x - W*.40,0,WORLD_W-W)
        self.camera_x += (target-self.camera_x)*min(1,dt*7.5)
        if abs(self.screen_shake)>0.1:
            self.screen_shake=max(0,self.screen_shake-dt*26)
        # Ambient embers drift independently to add depth without expensive post-processing.
        for ember in self.decor["embers"]:
            ember[1]-=ember[3]*dt
            ember[4]+=dt
            ember[0]+=math.sin(ember[4]*1.7)*ember[2]*dt
            if ember[1]<100:
                ember[1]=H-85
                ember[0]=random.uniform(max(0,self.camera_x),min(WORLD_W,self.camera_x+W))

    def area_at(self,x):
        for left,right,name,top,bottom in AREAS:
            if left<=x<right:
                return left,right,name,top,bottom
        return AREAS[-1]

    def draw_background(self,surface):
        left,right,name,top,bottom=self.area_at(self.camera_x+W*.42)
        # Vertical gradient keeps distant sky readable rather than crushing the palette to black.
        for y in range(0,H,3):
            f=y/H
            c=tuple(int(top[i]*(1-f)+bottom[i]*f) for i in range(3))
            pygame.draw.rect(surface,c,(0,y,W,3))
        # Distant moon / veil sun.
        moon_x=int(W*.74 - (self.camera_x*.08)%W*.3)
        moon_y=145
        glow(surface,(moon_x,moon_y),100,(196,137,87),28)
        pygame.draw.circle(surface,(110,91,76),(moon_x,moon_y),48)
        pygame.draw.circle(surface,(177,140,98),(moon_x-7,moon_y-6),42,2)
        pygame.draw.circle(surface,(74,69,65),(moon_x+13,moon_y-10),36)
        # Parallax castle silhouettes.
        for tx, ty, tw, th, color in self.decor["towers"]:
            sx=int(tx-self.camera_x*.28)
            if sx < -tw-20 or sx>W+20: continue
            rect=pygame.Rect(sx,ty,tw,th)
            pygame.draw.rect(surface,color,rect)
            pygame.draw.polygon(surface,color,[(sx-10,ty+12),(int(sx+tw*.22),ty-14),(int(sx+tw*.52),ty+12),(int(sx+tw*.82),ty-21),(sx+tw+8,ty+12)])
            for wx in range(sx+14,sx+tw-7,25):
                if 0<=wx<W:
                    pygame.draw.rect(surface,(107,78,59),(wx,ty+45,5,15))
        # Architecture ribs and hanging chains.
        for cx,cy,length in self.decor["chains"]:
            sx=int(cx-self.camera_x*.48)
            if -10<sx<W+10:
                pygame.draw.line(surface,(47,47,43),(sx,0),(sx,cy+length),2)
                for k in range(12,cy+length,18):
                    pygame.draw.line(surface,(59,54,47),(sx-3,k),(sx+3,k+5),1)
        # Room boundary markers and titles.
        for boundary in (1320,2850,4050):
            sx=int(boundary-self.camera_x)
            if -30<sx<W+30:
                pygame.draw.line(surface,(103,78,51),(sx,105),(sx,610),2)
                pygame.draw.circle(surface,GOLD,(sx,105),4)
        for ember in self.decor["embers"]:
            sx=int(ember[0]-self.camera_x*.82)
            if 0<=sx<W and 100<ember[1]<H-65:
                a=80+int((math.sin(ember[4]*3)+1)*50)
                col=(min(255,124+a//3),min(220,78+a//3),min(150,52+a//6))
                pygame.draw.circle(surface,col,(sx,int(ember[1])),1 if a<140 else 2)

    def draw_world(self,surface):
        camera=self.camera_x
        # Back haze behind architecture.
        for i in range(6):
            y=500+i*30
            col=(42+i*2,43+i*1,41+i)
            pygame.draw.line(surface,col,(0,y),(W,y),1)
        # Ground and stone platforms with top highlights and distinct front faces.
        for plat in self.platforms:
            sx=int(plat.x-camera)
            if sx+plat.w < -10 or sx>W+10: continue
            r=pygame.Rect(sx,int(plat.y),int(plat.w),int(plat.h))
            if plat.kind=="floor":
                pygame.draw.rect(surface,(40,43,41),r)
                pygame.draw.rect(surface,(79,78,69),(r.x,r.y,r.w,5))
                pygame.draw.line(surface,(99,91,75),(r.x,r.y+4),(r.right,r.y+4),1)
                # Tile seams are spaced in world coordinates so they remain stable as camera scrolls.
                start=(int(plat.x//56)*56)
                for wx in range(start,int(plat.x+plat.w),56):
                    px=int(wx-camera)
                    if sx<=px<=sx+plat.w:
                        pygame.draw.line(surface,(26,30,30),(px,r.y+7),(px,r.bottom),2)
                        pygame.draw.line(surface,(51,53,49),(px+1,r.y+7),(px+1,r.bottom),1)
                for row_y in range(int(plat.y+38),int(plat.y+plat.h),36):
                    pygame.draw.line(surface,(30,33,32),(r.x,row_y),(r.right,row_y),1)
            else:
                pygame.draw.rect(surface,(24,27,28),(r.x,r.y+6,r.w,r.h))
                pygame.draw.rect(surface,(57,59,56),r)
                pygame.draw.line(surface,(138,119,86),(r.x,r.y),(r.right,r.y),2)
                pygame.draw.line(surface,(88,83,70),(r.x+3,r.y+5),(r.right-2,r.y+5),1)
                for xx in range(r.x+22,r.right,38):
                    pygame.draw.line(surface,(37,41,40),(xx,r.y+6),(xx,r.bottom),1)
        # Decorative columns, roots, rubble.
        for wx in (330, 760, 1030, 1475, 1960, 2260, 2550, 3010, 3280, 3690, 3940, 4170, 4650):
            sx=int(wx-camera)
            if -60<sx<W+60:
                floor_y=FLOOR_Y if wx<2660 or wx>=3770 else FLOOR_Y+4
                pygame.draw.rect(surface,(26,29,30),(sx-20,floor_y-120,40,120))
                pygame.draw.rect(surface,(62,60,53),(sx-27,floor_y-124,54,10))
                pygame.draw.line(surface,(100,88,65),(sx-17,floor_y-118),(sx-17,floor_y-8),2)
        # Torches and checkpoint shrines.
        for wx,wy in self.decor["candles"]:
            sx=int(wx-camera)
            if -25<sx<W+25:
                glow(surface,(sx,wy-28),42,(236,142,66),53)
                pygame.draw.rect(surface,(82,64,46),(sx-4,wy-21,8,20))
                flame_y=wy-28+math.sin(self.elapsed*12+wx)*2
                pygame.draw.ellipse(surface,(255,161,72),(sx-4,int(flame_y-8),8,14))
                pygame.draw.ellipse(surface,(255,229,164),(sx-2,int(flame_y-6),4,9))
        for i,cp_x in enumerate((1280,2700,3820)):
            sx=int(cp_x-camera)
            if -50<sx<W+50:
                glow(surface,(sx,FLOOR_Y-28),66,GOLD,55 if self.checkpoints[i] else 23)
                pygame.draw.polygon(surface,(95,83,62),[(sx,FLOOR_Y-83),(sx+25,FLOOR_Y-48),(sx,FLOOR_Y-12),(sx-25,FLOOR_Y-48)])
                pygame.draw.polygon(surface,(48,54,52),[(sx,FLOOR_Y-72),(sx+15,FLOOR_Y-48),(sx,FLOOR_Y-24),(sx-15,FLOOR_Y-48)])
                pygame.draw.circle(surface,PALE_GOLD if self.checkpoints[i] else (110,102,79),(sx,FLOOR_Y-49),6)
        # Low floor fog bands.
        fog=pygame.Surface((W,105),pygame.SRCALPHA)
        for i in range(8):
            alpha=max(2,18-i*2)
            pygame.draw.ellipse(fog,(127,132,122,alpha),(-100+i*110,35+i*5,W+200-i*90,54-i*3))
        surface.blit(fog,(0,H-150))

    def draw_weapon_hint(self,surface):
        r=pygame.Rect(W-278,H-100,250,70)
        panel(surface,r,(14,17,17,240),(91,82,63),8)
        weapon=WEAPONS[self.weapon]
        text(surface,self.font_tiny,"WEAPON ART  [E]",(r.x+15,r.y+10),MUTED)
        text(surface,self.font_ui,weapon["skill"],(r.x+15,r.y+32),weapon["color"])
        if self.player.skill_cd>0:
            text(surface,self.font_tiny,f"{self.player.skill_cd:0.1f}s",(r.right-16,r.y+35),MUTED,anchor="topright")
        else:
            text(surface,self.font_tiny,"READY",(r.right-16,r.y+35),TEAL,anchor="topright")

    def draw_hud(self,surface):
        p=self.player
        # Vitality/stamina card.
        r=pygame.Rect(24,20,354,102)
        panel(surface,r)
        text(surface,self.font_tiny,"ASHEN WANDERER   /   VEILBOUND",(r.x+15,r.y+12),GOLD)
        bar(surface,pygame.Rect(r.x+16,r.y+34,214,13),p.hp,p.hp_max,RED)
        text(surface,self.font_ui,f"{int(p.hp):03d} / {p.hp_max}",(r.x+245,r.y+30),PALE)
        text(surface,self.font_tiny,"VITALITY",(r.x+16,r.y+49),MUTED)
        bar(surface,pygame.Rect(r.x+16,r.y+73,214,9),p.stamina,p.stamina_max,(150,173,110))
        text(surface,self.font_tiny,"STAMINA",(r.x+16,r.y+84),MUTED)
        bar(surface,pygame.Rect(r.x+245,r.y+75,82,8),p.soul_charge,p.soul_max,GOLD)
        text(surface,self.font_tiny,"SOUL",(r.x+245,r.y+87),MUTED)
        # Area / currency block.
        r2=pygame.Rect(W-236,20,212,80)
        panel(surface,r2)
        text(surface,self.font_tiny,"SOULS",(r2.x+15,r2.y+13),MUTED)
        text(surface,self.font_h1,f"{self.souls:04d}",(r2.x+68,r2.y+10),PALE_GOLD)
        text(surface,self.font_tiny,"DEPTH",(r2.x+15,r2.y+49),MUTED)
        depth=1 if self.player.x<1320 else 2 if self.player.x<2850 else 3 if self.player.x<4050 else 4
        text(surface,self.font_ui,f"{depth:02d}",(r2.x+68,r2.y+46),GOLD)
        # Progress track instead of an unhelpful minimap: visible route, shrines and boss marker.
        track=pygame.Rect(W//2-210,28,420,18)
        panel(surface,pygame.Rect(track.x-12,track.y-8,track.w+24,34),(13,16,16,228),(67,65,56),7)
        pygame.draw.line(surface,(81,77,66),(track.x+7,track.centery),(track.right-7,track.centery),4)
        prog=clamp(self.player.x/WORLD_W,0,1)
        pygame.draw.line(surface,GOLD,(track.x+7,track.centery),(track.x+7+int((track.w-14)*prog),track.centery),4)
        for cp in (1280,2700,3820):
            px=track.x+7+int((track.w-14)*cp/WORLD_W)
            pygame.draw.circle(surface,TEAL if self.player.x>=cp else (107,96,76),(px,track.centery),4)
        bossx=track.x+7+int((track.w-14)*4350/WORLD_W)
        pygame.draw.polygon(surface,RED,[(bossx,track.y-4),(bossx+5,track.y+1),(bossx,track.y+6),(bossx-5,track.y+1)])
        # Boss panel.
        boss=next((e for e in self.enemies if e.boss and not e.dead),None)
        if boss:
            text(surface,self.font_tiny,"GRAVE WARDEN  ·  THE UNBURIED",(W//2,58),GOLD,anchor="midtop")
            bar(surface,pygame.Rect(W//2-230,82,460,19),boss.hp,boss.hp_max,(177,58,50),(36,25,25),(116,76,59))
            if boss.phase==2:
                text(surface,self.font_tiny,"ENRAGED",(W//2+240,84),(255,116,92),anchor="topleft")
        # Weapon cards bottom-left.
        cards=[(24, H-102, 168),(202,H-102,168),(380,H-102,184)]
        for idx,(name,rect_data) in enumerate(zip(WEAPON_ORDER,cards)):
            x,y,w=rect_data
            selected=self.weapon==name
            rect=pygame.Rect(x,y,w,74)
            panel(surface,rect,(28,29,27,245) if selected else (16,19,19,235),GOLD if selected else (59,63,60),7,2 if selected else 1)
            text(surface,self.font_tiny,f"[{idx+1}]  {name.upper()}",(x+11,y+10),GOLD if selected else MUTED)
            text(surface,self.font_ui,WEAPONS[name]["style"],(x+11,y+37),WEAPONS[name]["color"] if selected else PALE)
        # Controls footer.
        footer=pygame.Rect(578,H-37,500,26)
        panel(surface,footer,(11,14,15,225),(48,52,50),6)
        text(surface,self.font_tiny,"A/D MOVE  ·  SPACE JUMP  ·  LMB ATTACK  ·  RMB HEAVY  ·  SHIFT DODGE  ·  E SKILL  ·  Q BURST",(footer.centerx,footer.centery),PALE,anchor="center",shadow=False)
        self.draw_weapon_hint(surface)
        # Area label fades at each transition.
        _,_,area_name,_,_=self.area_at(self.player.x)
        text(surface,self.font_tiny,area_name,(W/2,H-67),GOLD,anchor="center")
        if self.message_timer>0 and self.message:
            alpha=min(1,self.message_timer*1.6)
            color=tuple(int(c*alpha) for c in GOLD)
            text(surface,self.font_ui,self.message,(W/2,155),color,anchor="center")
        text(surface,self.font_tiny,f"{int(self.clock.get_fps()):03d} FPS",(W-20,H-18),MUTED,anchor="topright",shadow=False)

    def draw_title(self,surface):
        self.draw_background(surface)
        self.draw_world(surface)
        # Dark vignette to frame title without darkening gameplay.
        shade=pygame.Surface((W,H),pygame.SRCALPHA)
        pygame.draw.rect(shade,(4,6,8,142),(0,0,W,H))
        surface.blit(shade,(0,0))
        cx=W//2
        pygame.draw.circle(surface,(83,69,49),(cx,218),77,2)
        pygame.draw.circle(surface,(35,39,38),(cx,218),65,1)
        pygame.draw.polygon(surface,GOLD,[(cx,171),(cx+28,216),(cx,265),(cx-28,216)],2)
        pygame.draw.line(surface,GOLD,(cx,182),(cx,252),2)
        text(surface,self.font_title,"ASHEN VEIL",(cx,322),PALE_GOLD,anchor="center")
        text(surface,self.font_h1,"A fallen kingdom. One last ember.",(cx,372),MUTED,anchor="center")
        pygame.draw.line(surface,(90,72,48),(cx-220,414),(cx+220,414),1)
        text(surface,self.font_h1,"2D DARK-FANTASY METROIDVANIA",(cx,446),PALE,anchor="center")
        text(surface,self.font_ui,"EXPLORE THE RUINS  ·  MASTER YOUR WEAPON  ·  SURVIVE THE VEIL",(cx,482),MUTED,anchor="center")
        btn=pygame.Rect(cx-145,540,290,58)
        panel(surface,btn,(55,47,34,245),GOLD,7,2)
        text(surface,self.font_h1,"ENTER THE RUINS",(cx,btn.centery),PALE_GOLD,anchor="center")
        text(surface,self.font_ui,"ENTER / CLICK TO BEGIN",(cx,620),MUTED,anchor="center")
        text(surface,self.font_small,"A / D MOVE     SPACE JUMP     LMB ATTACK     SHIFT DODGE",(cx,675),MUTED,anchor="center")

    def draw_overlay(self,surface,title,subtitle,extra):
        shade=pygame.Surface((W,H),pygame.SRCALPHA)
        shade.fill((8,8,10,202))
        surface.blit(shade,(0,0))
        text(surface,self.font_title,title,(W//2,300),PALE_GOLD if title!="YOU HAVE FALLEN" else (218,117,96),anchor="center")
        text(surface,self.font_h1,subtitle,(W//2,365),PALE,anchor="center")
        text(surface,self.font_ui,extra,(W//2,425),GOLD,anchor="center")
        text(surface,self.font_ui,"R / ENTER — TRY AGAIN     ESC — TITLE",(W//2,492),MUTED,anchor="center")

    def render(self):
        surface=self.canvas
        if self.mode=="title":
            self.draw_title(surface)
        else:
            self.draw_background(surface)
            shake_x=random.randint(-int(self.screen_shake),int(self.screen_shake)) if self.screen_shake>1 else 0
            # Camera translation is applied through an offset surface so every side-scroller entity aligns.
            world_layer=self.world_layer
            world_layer.fill((0,0,0,0))
            if shake_x:
                old_camera=self.camera_x
                self.camera_x=old_camera-shake_x
            self.draw_world(world_layer)
            for projectile in self.projectiles:
                projectile.draw(world_layer,self.camera_x)
            for particle in self.particles:
                particle.draw(world_layer,self.camera_x)
            for enemy in self.enemies:
                enemy.draw(world_layer,self.camera_x,self.elapsed)
            self.player.draw(world_layer,self.camera_x,self)
            for ft in self.floating:
                ft.draw(world_layer,self)
            if shake_x:
                self.camera_x=old_camera
            surface.blit(world_layer,(0,0))
            self.draw_hud(surface)
            if self.paused:
                self.draw_overlay(surface,"PAUSED","The veil holds its breath.","ESC / CLICK TO RESUME")
            elif self.mode=="dead":
                self.draw_overlay(surface,"YOU HAVE FALLEN",f"{self.kills} SLAIN  ·  {self.souls} SOULS CARRIED","The veil remembers every failure.")
            elif self.victory or self.mode=="victory":
                self.draw_overlay(surface,"THE VEIL IS BROKEN",f"{self.kills} SLAIN  ·  {self.souls} SOULS CLAIMED","The kingdom breathes again. For now.")
        window_size=self.window.get_size()
        scaled=pygame.transform.scale(surface,window_size)
        self.window.blit(scaled,(0,0))
        pygame.display.flip()

    def run(self):
        while self.running:
            dt=min(self.clock.tick(FPS)/1000.0,.033)
            self.fps_value=self.clock.get_fps()
            self.handle_events()
            self.update(dt)
            self.render()
        pygame.quit()


def main():
    Game().run()


if __name__=="__main__":
    main()