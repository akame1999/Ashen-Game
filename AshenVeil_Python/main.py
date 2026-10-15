"""ASHEN VEIL - a self-contained dark-fantasy action combat sandbox.

Original, asset-free Python/Pygame prototype. Inspired by the mood of gothic
Soulslike games and the pace of action roguelites, without copied game assets.
"""
from __future__ import annotations

import math
import random
import sys
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pygame
from pygame.math import Vector2 as V2

# ------------------------------- Configuration ------------------------------
W, H = 1280, 800
FPS = 120
WORLD_W, WORLD_H = 1900, 1350
UI_H = 70
ARENA_RECT = pygame.Rect(52, 52, WORLD_W - 104, WORLD_H - 104)
BG = (13, 16, 19)
STONE = (39, 43, 45)
STONE_LIGHT = (59, 62, 60)
GOLD = (211, 173, 104)
PALE_GOLD = (247, 220, 159)
TEAL = (115, 198, 181)
RED = (196, 83, 74)
TEXT = (222, 218, 203)
MUTED = (131, 135, 132)
_GLOW_CACHE = {}
_TEXT_CACHE = OrderedDict()
_TEXT_CACHE_LIMIT = 1200

WEAPONS = {
    "Rookfang": {
        "label": "ROOKFANG LONGSWORD", "kind": "balanced", "damage": 25,
        "range": 94, "arc": 1.55, "windup": 0.075, "active": 0.14,
        "recovery": 0.18, "stamina": 18, "combo_gap": 0.56,
        "heavy_damage": 57, "heavy_range": 120, "heavy_cost": 34,
        "heavy_windup": 0.38, "heavy_active": 0.18, "skill_cost": 35,
        "skill_cd": 4.5, "skill": "RIFT STEP", "color": (196, 208, 199),
    },
    "Gravetide": {
        "label": "GRAVETIDE TWINBLADES", "kind": "fast", "damage": 15,
        "range": 77, "arc": 1.9, "windup": 0.035, "active": 0.105,
        "recovery": 0.105, "stamina": 11, "combo_gap": 0.48,
        "heavy_damage": 38, "heavy_range": 90, "heavy_cost": 27,
        "heavy_windup": 0.24, "heavy_active": 0.15, "skill_cost": 30,
        "skill_cd": 3.8, "skill": "UNDERTOW", "color": (119, 203, 190),
    },
    "Oathbreaker": {
        "label": "OATHBREAKER GREATBLADE", "kind": "heavy", "damage": 42,
        "range": 112, "arc": 1.25, "windup": 0.18, "active": 0.18,
        "recovery": 0.28, "stamina": 27, "combo_gap": 0.72,
        "heavy_damage": 88, "heavy_range": 146, "heavy_cost": 48,
        "heavy_windup": 0.54, "heavy_active": 0.22, "skill_cost": 42,
        "skill_cd": 5.3, "skill": "GROUNDSPLIT", "color": (217, 170, 105),
    },
}
WEAPON_ORDER = ["Rookfang", "Gravetide", "Oathbreaker"]

# --------------------------------- Utilities ---------------------------------
def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def angle_diff(a, b):
    return (a - b + math.pi) % (math.tau) - math.pi

def unit_angle(angle):
    return V2(math.cos(angle), math.sin(angle))

def safe_normalize(v: V2, fallback=V2(1, 0)):
    return v.normalize() if v.length_squared() > 0.0001 else V2(fallback)

def _cached_text(font, text, color):
    key = (id(font), str(text), tuple(color))
    image = _TEXT_CACHE.get(key)
    if image is not None:
        _TEXT_CACHE.move_to_end(key)
        return image
    image = font.render(str(text), True, color).convert_alpha()
    _TEXT_CACHE[key] = image
    if len(_TEXT_CACHE) > _TEXT_CACHE_LIMIT:
        _TEXT_CACHE.popitem(last=False)
    return image

def draw_text(surface, font, text, pos, color=TEXT, anchor="topleft", shadow=True):
    img = _cached_text(font, text, color)
    rect = img.get_rect()
    setattr(rect, anchor, (int(pos[0]), int(pos[1])))
    if shadow:
        sh = _cached_text(font, text, (0, 0, 0))
        sr = sh.get_rect()
        setattr(sr, anchor, (int(pos[0]) + 2, int(pos[1]) + 2))
        surface.blit(sh, sr)
    surface.blit(img, rect)
    return rect

def draw_bar(surface, rect, value, max_value, fill, back=(28, 31, 32), border=(93, 92, 80), height=None):
    pygame.draw.rect(surface, back, rect, border_radius=4)
    ratio = clamp(value / max(1, max_value), 0, 1)
    inner = rect.copy()
    inner.inflate_ip(-4, -4)
    if height is not None:
        inner.height = max(2, min(height, inner.height))
    if inner.width > 0 and inner.height > 0 and ratio > 0:
        inner.width = max(1, int(inner.width * ratio))
        pygame.draw.rect(surface, fill, inner, border_radius=3)
    pygame.draw.rect(surface, border, rect, 1, border_radius=4)

def blit_glow(surface, pos, radius, color, alpha=70):
    r = max(2, int(radius))
    a_bucket = max(0, min(248, int(alpha / 8) * 8))
    key = (r, tuple(color), a_bucket)
    layer = _GLOW_CACHE.get(key)
    if layer is None:
        layer = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        cx = cy = r * 2
        for rr, aa in [(r, a_bucket // 2), (int(r * .7), a_bucket), (int(r * .42), min(255, a_bucket * 2))]:
            pygame.draw.circle(layer, (*color, aa), (cx, cy), max(1, rr))
        _GLOW_CACHE[key] = layer
    cx = cy = r * 2
    surface.blit(layer, (int(pos[0] - cx), int(pos[1] - cy)), special_flags=pygame.BLEND_RGBA_ADD)

# --------------------------------- Particles ---------------------------------
@dataclass
class Particle:
    pos: V2
    vel: V2
    life: float
    max_life: float
    color: tuple[int, int, int]
    radius: float = 3
    drag: float = 2.0
    glow: bool = False

    def update(self, dt):
        self.life -= dt
        self.pos += self.vel * dt
        self.vel *= max(0, 1 - self.drag * dt)
        return self.life > 0

    def draw(self, surface, camera):
        p = self.pos - camera
        if not (-20 < p.x < W + 20 and -20 < p.y < H + 20):
            return
        k = clamp(self.life / max(.001, self.max_life), 0, 1)
        r = max(1, int(self.radius * (.25 + .75 * k)))
        color = tuple(int(c * (.4 + .6 * k)) for c in self.color)
        if self.glow:
            blit_glow(surface, p, r * 3, color, int(24 * k))
        pygame.draw.circle(surface, color, (int(p.x), int(p.y)), r)

# --------------------------------- Combatant ---------------------------------
@dataclass
class Player:
    pos: V2
    vel: V2 = field(default_factory=lambda: V2())
    radius: float = 17
    hp: float = 130
    max_hp: float = 130
    stamina: float = 100
    max_stamina: float = 100
    souls: int = 0
    weapon: str = "Rookfang"
    facing: float = 0.0
    attack_timer: float = 0.0
    attack_phase: str = "idle"
    attack_kind: str = "light"
    attack_id: int = 0
    combo: int = 0
    combo_timer: float = 0.0
    hit_ids: set = field(default_factory=set)
    attack_angle: float = 0.0
    heavy_charge: float = 0.0
    heavy_held: bool = False
    dodge_timer: float = 0.0
    dodge_cd: float = 0.0
    dodge_dir: V2 = field(default_factory=lambda: V2(1, 0))
    skill_cd: float = 0.0
    invuln: float = 0.0
    hurt_flash: float = 0.0
    dead: bool = False

    def update(self, dt, game):
        self.combo_timer = max(0, self.combo_timer - dt)
        self.dodge_timer = max(0, self.dodge_timer - dt)
        self.dodge_cd = max(0, self.dodge_cd - dt)
        self.skill_cd = max(0, self.skill_cd - dt)
        self.invuln = max(0, self.invuln - dt)
        self.hurt_flash = max(0, self.hurt_flash - dt)
        # Stamina only refills after a short exertion delay.
        if self.attack_phase == "idle" and self.dodge_timer <= 0 and not self.heavy_held:
            self.stamina = min(self.max_stamina, self.stamina + 24 * dt)
        if self.combo_timer <= 0 and self.attack_phase == "idle":
            self.combo = 0
    def start_attack(self, angle, heavy=False):
        w = WEAPONS[self.weapon]
        if self.attack_phase != "idle" or self.dodge_timer > 0 or self.dead:
            return False
        cost = w["heavy_cost"] if heavy else w["stamina"]
        if self.stamina < cost:
            return False
        self.stamina -= cost
        self.attack_kind = "heavy" if heavy else "light"
        if not heavy:
            self.combo = (self.combo % 3) + 1 if self.combo_timer > 0 else 1
            self.combo_timer = w["combo_gap"]
        else:
            self.combo = 0
            self.combo_timer = 0
        self.attack_id += 1
        self.hit_ids.clear()
        self.attack_angle = angle
        self.facing = angle
        self.attack_phase = "windup"
        self.attack_timer = w["heavy_windup"] if heavy else w["windup"]
        return True

    def begin_dodge(self, direction):
        if self.dodge_cd > 0 or self.stamina < 22 or self.dead:
            return False
        self.stamina -= 22
        self.dodge_dir = safe_normalize(direction, unit_angle(self.facing))
        self.dodge_timer = .24
        self.dodge_cd = .48
        self.invuln = .28
        self.attack_phase = "idle"
        self.attack_timer = 0
        self.heavy_held = False
        self.vel = self.dodge_dir * 630
        return True

# ---------------------------------- Enemies ----------------------------------
ENEMY_DATA = {
    "Hollow": {"hp": 58, "speed": 88, "damage": 16, "range": 40, "windup": .48, "cooldown": .85, "radius": 16, "color": (117, 113, 103), "souls": 12},
    "Ravager": {"hp": 76, "speed": 116, "damage": 21, "range": 43, "windup": .35, "cooldown": .75, "radius": 15, "color": (171, 88, 72), "souls": 16},
    "Cinder Adept": {"hp": 52, "speed": 57, "damage": 13, "range": 245, "windup": .72, "cooldown": 1.65, "radius": 15, "color": (181, 126, 68), "souls": 18},
    "Grave Warden": {"hp": 460, "speed": 66, "damage": 29, "range": 75, "windup": .70, "cooldown": 1.0, "radius": 34, "color": (155, 82, 73), "souls": 180},
}

@dataclass
class Enemy:
    pos: V2
    kind: str
    uid: int
    hp: float = 0
    max_hp: float = 0
    radius: float = 16
    state: str = "approach"
    state_timer: float = 0
    cooldown: float = 0
    facing: float = 0
    hit_flash: float = 0
    stagger: float = 0
    dead: bool = False
    attack_serial: int = 0
    side: float = 1

    def __post_init__(self):
        d = ENEMY_DATA[self.kind]
        self.hp = self.max_hp = d["hp"]
        self.radius = d["radius"]
        self.cooldown = random.uniform(.25, 1.0)
        self.side = random.choice([-1, 1])

    def update(self, dt, game):
        if self.dead:
            return
        d = ENEMY_DATA[self.kind]
        self.hit_flash = max(0, self.hit_flash - dt)
        self.stagger = max(0, self.stagger - dt)
        self.cooldown = max(0, self.cooldown - dt)
        to_player = game.player.pos - self.pos
        dist = to_player.length()
        # Lock direction once a windup begins so the telegraph is dodgeable.
        if self.state != "windup":
            self.facing = math.atan2(to_player.y, to_player.x) if dist else self.facing
        if self.stagger > 0:
            self.pos += safe_normalize(-to_player) * (self.stagger * 110 * dt)
            return
        if self.state == "windup":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = "attack"
                self.state_timer = .16 if self.kind != "Grave Warden" else .25
                self.attack_serial += 1
                if self.kind == "Cinder Adept":
                    direction = unit_angle(self.facing)
                    game.projectiles.append(Projectile(self.pos + direction * 20, direction * 340, 11, d["damage"], "enemy", (224, 125, 76), 3.2))
                else:
                    self._do_melee(game, d, dist)
        elif self.state == "attack":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = "approach"
                self.cooldown = d["cooldown"] * random.uniform(.9, 1.15)
        elif dist <= d["range"] + game.player.radius + self.radius and self.cooldown <= 0:
            self.state = "windup"
            self.state_timer = d["windup"]
        else:
            # Adept kites when too close; melee units circle a little, then commit.
            direction = safe_normalize(to_player)
            if self.kind == "Cinder Adept" and dist < 150:
                direction = -direction + V2(-direction.y, direction.x) * .34 * self.side
            elif dist < 165:
                direction = direction + V2(-direction.y, direction.x) * .22 * self.side
                direction = safe_normalize(direction)
            speed = d["speed"] * (1.08 if self.kind == "Ravager" else 1)
            self.pos += direction * speed * dt
            self.pos = game.resolve_world_collisions(self.pos, self.radius)

    def _do_melee(self, game, d, dist):
        p = game.player
        if dist <= d["range"] + self.radius + p.radius:
            diff = angle_diff(math.atan2(p.pos.y - self.pos.y, p.pos.x - self.pos.x), self.facing)
            if abs(diff) < (1.0 if self.kind != "Grave Warden" else 1.2):
                if p.invuln <= 0 and p.dodge_timer <= 0:
                    game.damage_player(d["damage"], self.pos)
        game.spawn_slash(self.pos, self.facing, d["range"] + 18, (RED[0], RED[1], RED[2]), .17, .7)

@dataclass
class Projectile:
    pos: V2
    vel: V2
    radius: float
    damage: int
    owner: str
    color: tuple[int, int, int]
    life: float = 2.8
    dead: bool = False

    def update(self, dt, game):
        self.life -= dt
        self.pos += self.vel * dt
        if self.life <= 0 or game.out_of_bounds(self.pos, 30):
            self.dead = True
            return
        if self.owner == "enemy" and (self.pos - game.player.pos).length() < self.radius + game.player.radius:
            if game.player.invuln <= 0 and game.player.dodge_timer <= 0:
                game.damage_player(self.damage, self.pos)
            game.burst(self.pos, self.color, 8, 180)
            self.dead = True
        elif self.owner == "player":
            for enemy in game.enemies:
                if not enemy.dead and (self.pos - enemy.pos).length() < self.radius + enemy.radius:
                    game.damage_enemy(enemy, self.damage, self.vel)
                    game.burst(self.pos, self.color, 9, 180)
                    self.dead = True
                    break

# ---------------------------------- Game -------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("ASHEN VEIL  |  Combat Sandbox")
        self.screen = pygame.display.set_mode((W, H), pygame.RESIZABLE | pygame.DOUBLEBUF)
        self.canvas = pygame.Surface((W, H)).convert()
        self.clock = pygame.time.Clock()
        self.font_s = pygame.font.SysFont("consolas", 14)
        self.font_m = pygame.font.SysFont("segoe ui", 17)
        self.font_b = pygame.font.SysFont("segoe ui", 24, bold=True)
        self.font_title = pygame.font.SysFont("georgia", 50, bold=False)
        self.font_subtitle = pygame.font.SysFont("georgia", 16, italic=True)
        self.font_smallcaps = pygame.font.SysFont("consolas", 11, bold=True)
        self.running = True
        self.state = "title"
        self.new_run()
        self.background = self.make_world()
        self.vignette = self.make_vignette()
        # Reuse effect surfaces instead of allocating a full-screen layer every frame.
        self.hurt_overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        self.flash_overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        self.overlay_layer = pygame.Surface((W, H), pygame.SRCALPHA)
        self.dodge_ghosts = []
        for alpha in (62, 44, 28):
            ghost = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.ellipse(ghost, (120, 205, 188, alpha), (8, 8, 44, 44))
            self.dodge_ghosts.append(ghost)
        self.heavy_pending = False
        self.heavy_pending_ttl = 0.0
        self.fog_band = pygame.Surface((W, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(self.fog_band, (120, 135, 129, 8), (0, 4, W, 24))
        self.decor_time = 0
        self.shake = 0
        self.flash = 0
        self.hitstop = 0
        self.total_time = 0
        self.message = ""
        self.message_timer = 0
        self.last_input = pygame.time.get_ticks() / 1000
        self.prev_mouse = pygame.mouse.get_pos()
        self.left_was_down = False
        self.right_was_down = False
        self.attack_buffer = 0.0
        self.debug = False
        self.state = "title"

    def new_run(self):
        self.player = Player(V2(WORLD_W * .5, WORLD_H * .52))
        self.enemies: list[Enemy] = []
        self.projectiles: list[Projectile] = []
        self.particles: list[Particle] = []
        self.floating_texts = []
        self.attack_buffer = 0.0
        self.left_was_down = False
        self.right_was_down = False
        self.heavy_pending = False
        self.heavy_pending_ttl = 0.0
        self.obstacles: list[pygame.Rect] = []
        self.world_props = []
        self.wave = 1
        self.kills = 0
        self.elapsed = 0
        self.shake = 0
        self.flash = 0
        self.hitstop = 0
        self.enemy_seq = 0
        self.wave_wait = 1.0
        self.boss_defeated = False
        self.generate_obstacles()
        self.spawn_wave(1)
        self.state = "playing"

    def generate_obstacles(self):
        # Fixed, authored pillar layout leaves several readable combat lanes.
        cx, cy = WORLD_W // 2, WORLD_H // 2
        positions = [(-300,-205), (-300,205), (300,-205), (300,205), (-500,0), (500,0), (0,-320), (0,320)]
        for dx, dy in positions:
            r = 32
            self.obstacles.append(pygame.Rect(cx + dx-r, cy + dy-r, r*2, r*2))
            self.world_props.append((V2(cx+dx, cy+dy), r))
        # Low broken stone clusters near the outer lanes.
        for dx,dy,ww,hh in [(-600,-260,110,30),(600,-260,110,30),(-600,260,110,30),(600,260,110,30)]:
            self.obstacles.append(pygame.Rect(cx+dx-ww//2, cy+dy-hh//2, ww, hh))

    def make_world(self):
        surf = pygame.Surface((WORLD_W, WORLD_H)).convert()
        surf.fill((22, 27, 29))
        # Large floor slabs with irregular alternating values.
        tile = 92
        rng = random.Random(217)
        for y in range(0, WORLD_H, tile):
            for x in range(0, WORLD_W, tile):
                v = rng.randint(-3, 4)
                c = (35+v, 40+v, 41+v)
                pygame.draw.rect(surf, c, (x+1, y+1, tile-2, tile-2))
                pygame.draw.line(surf, (39+v, 43+v, 43+v), (x+3, y+3), (x+tile-4, y+3), 1)
                if rng.random() < .22:
                    px,py=x+rng.randint(8,tile-8),y+rng.randint(8,tile-8)
                    pygame.draw.line(surf, (25,30,31), (px,py), (px+rng.randint(-24,24),py+rng.randint(8,28)), 1)
                if rng.random() < .14:
                    pygame.draw.circle(surf, (32,37,38), (x+rng.randint(8,tile-8), y+rng.randint(8,tile-8)), rng.randint(2,5))
        # Arena boundary and old inner ring.
        pygame.draw.rect(surf, (12, 16, 18), ARENA_RECT, 20)
        pygame.draw.rect(surf, (75, 69, 58), ARENA_RECT, 5)
        inner = pygame.Rect(WORLD_W//2-420, WORLD_H//2-300, 840, 600)
        pygame.draw.rect(surf, (55, 53, 47), inner, 2, border_radius=3)
        # Faded chalk circles and old sigils.
        center = (WORLD_W//2, WORLD_H//2)
        for rad, wid in [(158,3),(166,1),(244,1)]:
            pygame.draw.circle(surf, (68, 70, 62), center, rad, wid)
        for i in range(12):
            a=i*math.tau/12
            p1=(int(center[0]+math.cos(a)*165),int(center[1]+math.sin(a)*165))
            p2=(int(center[0]+math.cos(a)*210),int(center[1]+math.sin(a)*210))
            pygame.draw.line(surf,(76,70,57),p1,p2,2)
            p3=(int(center[0]+math.cos(a)*244),int(center[1]+math.sin(a)*244))
            pygame.draw.circle(surf,(103,85,57),p3,4,1)
        # Worn carved border corner decorations.
        for x,y in [(ARENA_RECT.left,ARENA_RECT.top),(ARENA_RECT.right,ARENA_RECT.top),(ARENA_RECT.left,ARENA_RECT.bottom),(ARENA_RECT.right,ARENA_RECT.bottom)]:
            pygame.draw.circle(surf,(95,76,55),(x,y),18,3)
        # Obstacle shadows and stonework are drawn over the floor on the world canvas.
        for rect in self.obstacles:
            if rect.width > 70:
                pygame.draw.rect(surf,(17,20,21),rect.move(8,10),border_radius=5)
                pygame.draw.rect(surf,(55,57,55),rect,border_radius=4)
                pygame.draw.rect(surf,(83,82,75),rect,2,border_radius=4)
                pygame.draw.line(surf,(96,91,78),rect.topleft,(rect.right-5,rect.top+3),2)
            else:
                cx,cy=rect.center
                pygame.draw.ellipse(surf,(16,20,21),(rect.x-10,rect.y+8,rect.width+20,rect.height+15))
                pygame.draw.circle(surf,(49,53,52),(cx,cy),rect.width//2+4)
                pygame.draw.circle(surf,(78,77,69),(cx,cy),rect.width//2+4,3)
                pygame.draw.circle(surf,(35,40,40),(cx-4,cy-4),rect.width//2-5)
                pygame.draw.line(surf,(91,85,72),(cx-15,cy-12),(cx+3,cy+4),2)
        # Torch basins anchored on walls.
        self.torches = [V2(ARENA_RECT.left+10, ARENA_RECT.top+110), V2(ARENA_RECT.right-10, ARENA_RECT.top+110),
                        V2(ARENA_RECT.left+10, ARENA_RECT.bottom-110), V2(ARENA_RECT.right-10, ARENA_RECT.bottom-110),
                        V2(WORLD_W*.5, ARENA_RECT.top+12), V2(WORLD_W*.5, ARENA_RECT.bottom-12)]
        for p in self.torches:
            pygame.draw.circle(surf,(16,20,21),(int(p.x),int(p.y)),20)
            pygame.draw.circle(surf,(80,62,43),(int(p.x),int(p.y)),14,2)
        return surf

    def make_vignette(self):
        surf = pygame.Surface((W, H), pygame.SRCALPHA)
        # Smooth dark edges using nested transparent rectangles.
        for i in range(0, 170, 5):
            alpha = int((i / 170) ** 2 * 6)
            pygame.draw.rect(surf, (0,0,0,alpha), (i,i,W-2*i,H-2*i), 5)
        return surf

    def spawn_wave(self, wave):
        self.wave = wave
        self.wave_wait = 0
        self.message = ["THE RUIN STIRS", "ASH REMEMBERS", "NO REST FOR THE HOLLOW", "THE BELLS HAVE FALLEN"][ (wave-1) % 4 ]
        self.message_timer = 2.2
        n = min(3 + wave, 8)
        if wave % 3 == 0:
            self.spawn_enemy("Grave Warden", self.random_spawn_pos())
            n = max(2, n-3)
            self.message = "THE GRAVE WARDEN"
            self.message_timer = 3.0
        kinds = ["Hollow"] * 5 + (["Ravager"] * min(1 + wave//2, 4)) + (["Cinder Adept"] * min(wave//2, 3))
        for _ in range(n):
            self.spawn_enemy(random.choice(kinds), self.random_spawn_pos())

    def random_spawn_pos(self):
        # Spawn around the live combat camera, not only at the far outer walls.
        # This keeps encounters on-screen and gives the player readable approach time.
        center = V2(self.player.pos)
        cam = self.camera()
        left = max(ARENA_RECT.left + 70, cam.x + 95)
        right = min(ARENA_RECT.right - 70, cam.x + W - 95)
        top = max(ARENA_RECT.top + 70, cam.y + 80)
        bottom = min(ARENA_RECT.bottom - 70, cam.y + H - 80)
        for _ in range(140):
            angle = random.random() * math.tau
            radius = random.uniform(300, 455)
            pos = V2(center.x + math.cos(angle) * radius,
                     center.y + math.sin(angle) * radius * .72)
            pos.x = clamp(pos.x, left, right)
            pos.y = clamp(pos.y, top, bottom)
            if ((pos-center).length() > 220 and not self.circle_hits_obstacle(pos, 42)):
                return pos
        # Safe fallback close enough to be visible but outside melee range.
        candidates = [V2(clamp(center.x + dx, left, right), clamp(center.y + dy, top, bottom))
                      for dx, dy in ((360, 0), (-360, 0), (0, 280), (0, -280))]
        for pos in candidates:
            if not self.circle_hits_obstacle(pos, 42):
                return pos
        return V2(clamp(center.x + 320, ARENA_RECT.left+80, ARENA_RECT.right-80),
                  clamp(center.y, ARENA_RECT.top+80, ARENA_RECT.bottom-80))

    def spawn_enemy(self, kind, pos):
        self.enemy_seq += 1
        self.enemies.append(Enemy(V2(pos), kind, self.enemy_seq))

    def circle_hits_obstacle(self, pos, radius):
        for r in self.obstacles:
            nearest = V2(clamp(pos.x, r.left, r.right), clamp(pos.y, r.top, r.bottom))
            if (pos-nearest).length_squared() < radius*radius:
                return True
        return False

    def resolve_world_collisions(self, pos, radius):
        pos = V2(pos)
        pos.x = clamp(pos.x, ARENA_RECT.left+radius+3, ARENA_RECT.right-radius-3)
        pos.y = clamp(pos.y, ARENA_RECT.top+radius+3, ARENA_RECT.bottom-radius-3)
        for r in self.obstacles:
            nearest = V2(clamp(pos.x, r.left, r.right), clamp(pos.y, r.top, r.bottom))
            delta = pos-nearest
            if delta.length_squared() < radius*radius:
                if delta.length_squared() < .001:
                    choices = [V2(pos.x-r.left,0),V2(r.right-pos.x,0),V2(0,pos.y-r.top),V2(0,r.bottom-pos.y)]
                    delta = min(choices,key=lambda x:x.length_squared())
                pos += safe_normalize(delta) * (radius - max(.001, delta.length()) + .5)
        return pos

    def out_of_bounds(self, p, margin=0):
        return p.x < ARENA_RECT.left+margin or p.x > ARENA_RECT.right-margin or p.y < ARENA_RECT.top+margin or p.y > ARENA_RECT.bottom-margin

    def viewport_rect(self):
        """Aspect-correct letterboxed game viewport inside a resizable window."""
        sw, sh = self.screen.get_size()
        scale = min(sw / W, sh / H)
        vw, vh = max(1, int(W * scale)), max(1, int(H * scale))
        return pygame.Rect((sw - vw) // 2, (sh - vh) // 2, vw, vh)

    def window_to_canvas(self, screen_pos):
        viewport = self.viewport_rect()
        if not viewport.collidepoint(screen_pos):
            return None
        return V2((screen_pos[0] - viewport.x) * W / viewport.width,
                  (screen_pos[1] - viewport.y) * H / viewport.height)

    def screen_to_world(self, screen_pos):
        cam = self.camera()
        return V2(screen_pos) + cam

    def camera(self):
        p = self.player.pos
        return V2(clamp(p.x-W/2, 0, WORLD_W-W), clamp(p.y-H/2, 0, WORLD_H-H))

    def burst(self, pos, color, count=12, speed=190):
        # Bound live particles to keep frame time stable during large hit bursts.
        if len(self.particles) > 520:
            self.particles = self.particles[-420:]
        for _ in range(count):
            a=random.random()*math.tau
            sp=random.uniform(speed*.25,speed)
            life=random.uniform(.18,.55)
            self.particles.append(Particle(V2(pos),unit_angle(a)*sp,life,life,color,random.uniform(1.3,3.8),random.uniform(1.2,3.8),True))

    def spawn_slash(self, pos, angle, reach, color, life=.18, width=1.0):
        # slash trail is represented by fast, bright particles along the blade path
        for i in range(7):
            t=i/6
            a=angle + (t-.5)*1.25
            p=pos+unit_angle(a)*reach*random.uniform(.56,.99)
            v=unit_angle(a+random.uniform(-.4,.4))*random.uniform(40,125)
            self.particles.append(Particle(p,v,life,life,color,random.uniform(1,2.7),3,True))

    def damage_player(self, amount, source):
        p=self.player
        if p.invuln > 0 or p.dead:
            return
        p.hp=max(0,p.hp-amount)
        p.hurt_flash=.25
        p.invuln=.35
        p.vel += safe_normalize(p.pos-source)*210
        self.shake=max(self.shake,8)
        self.flash=max(self.flash,.12)
        self.burst(p.pos,(197,76,68),18,220)
        if p.hp <= 0:
            p.dead=True
            self.state="gameover"

    def damage_enemy(self, enemy, amount, impulse=V2(0,0)):
        if enemy.dead:
            return
        enemy.hp-=amount
        enemy.hit_flash=.13
        enemy.stagger=.12 if enemy.kind != "Grave Warden" else .035
        enemy.pos += safe_normalize(impulse)*16
        self.burst(enemy.pos, (217, 192, 142) if enemy.kind=="Grave Warden" else (185,168,131), 8, 160)
        self.shake=max(self.shake,3 if amount<40 else 7)
        self.hitstop=max(self.hitstop,.035 if amount<40 else .065)
        self.spawn_floating_text(enemy.pos, str(int(amount)), PALE_GOLD if amount >= 40 else TEXT, 1.0)
        if enemy.hp <= 0:
            enemy.dead=True
            self.kills+=1
            self.player.souls+=ENEMY_DATA[enemy.kind]["souls"]
            self.burst(enemy.pos, (194,146,89), 24 if enemy.kind=="Grave Warden" else 15, 240)
            self.spawn_floating_text(enemy.pos, "+"+str(ENEMY_DATA[enemy.kind]["souls"]), GOLD, 0.85)
            if enemy.kind == "Grave Warden":
                self.player.hp=min(self.player.max_hp,self.player.hp+22)
                self.player.stamina=min(self.player.max_stamina,self.player.stamina+35)
                self.boss_defeated=True
                self.message="THE WARDEN FALLS"
                self.message_timer=2.5

    def spawn_floating_text(self, pos, text, color, life=.8):
        self.floating_texts.append({"pos":V2(pos),"text":text,"color":color,"life":life,"max":life})

    def start_skill(self):
        p=self.player
        w=WEAPONS[p.weapon]
        if p.skill_cd>0 or p.stamina<w["skill_cost"] or p.dead or p.dodge_timer>0:
            return
        p.stamina-=w["skill_cost"]
        p.skill_cd=w["skill_cd"]
        angle=p.facing
        if p.weapon=="Rookfang":
            direction=unit_angle(angle)
            p.pos=self.resolve_world_collisions(p.pos+direction*100, p.radius)
            p.invuln=max(p.invuln,.22)
            self.spawn_slash(p.pos,angle,130,(187,220,209),.25,1)
            self.damage_arc(angle,125,1.2,53,115)
            self.burst(p.pos,(148,216,202),16,220)
        elif p.weapon=="Gravetide":
            self.damage_arc(angle,115,math.tau,36,104)
            self.spawn_slash(p.pos,angle,95,(117,218,199),.28,1)
            self.burst(p.pos,(84,191,175),22,260)
        else:
            self.damage_arc(angle,150,1.65,68,150)
            self.spawn_slash(p.pos,angle,150,(223,174,104),.33,1)
            self.burst(p.pos,(223,174,104),25,290)
        self.shake=max(self.shake,6)
        self.message=w["skill"]
        self.message_timer=.8

    def damage_arc(self, angle, reach, arc, damage, knockback):
        for e in self.enemies:
            if e.dead: continue
            d=e.pos-self.player.pos
            dist=d.length()
            if dist <= reach+e.radius and (arc>=math.tau-0.01 or abs(angle_diff(math.atan2(d.y,d.x),angle))<=arc*.5):
                self.damage_enemy(e,damage,d)
                e.stagger=max(e.stagger,.19)
                e.pos=self.resolve_world_collisions(e.pos+safe_normalize(d)*knockback*.12,e.radius)

    def _update_attack(self, dt):
        p = self.player
        if p.attack_phase == "idle":
            return
        w = WEAPONS[p.weapon]
        phase_before = p.attack_phase
        p.attack_timer -= dt
        if phase_before == "windup" and p.attack_timer <= 0:
            p.attack_phase = "active"
            p.attack_timer = w["heavy_active"] if p.attack_kind == "heavy" else w["active"]
            self.perform_swing(visuals=True)
        elif phase_before == "active":
            # Keep checking contact throughout the active frames. Previously the hitbox
            # was sampled once, on a single frame, so a moving enemy or moving player
            # could make an apparently accurate swing deal no damage.
            self.perform_swing(visuals=False)
            if p.attack_timer <= 0:
                p.attack_phase = "recovery"
                p.attack_timer = w["recovery"] * (1.2 if p.weapon == "Oathbreaker" and p.attack_kind == "heavy" else 1)
        elif phase_before == "recovery" and p.attack_timer <= 0:
            p.attack_phase = "idle"
            p.attack_timer = 0

    def perform_swing(self, visuals=True):
        p = self.player
        w = WEAPONS[p.weapon]
        heavy = p.attack_kind == "heavy"
        combo = p.combo if not heavy else 0
        reach = w["heavy_range"] if heavy else w["range"] * (1.04 if combo == 3 else 1)
        damage = w["heavy_damage"] if heavy else w["damage"] * (1.18 if combo == 3 else 1)
        arc = w["arc"] * (1.15 if combo == 2 else .92 if combo == 3 else 1)
        forward = unit_angle(p.attack_angle)
        if visuals:
            self.spawn_slash(p.pos + forward * 12, p.attack_angle, reach, w["color"], .22 if not heavy else .31, 1)
            self.burst(p.pos + forward * reach * .72, w["color"], 7 if not heavy else 12, 145)
        for e in self.enemies:
            if e.dead or e.uid in p.hit_ids:
                continue
            delta = e.pos - p.pos
            dist = delta.length()
            if dist > reach + e.radius:
                continue
            # Capsule-like contact tolerance: retain the weapon's directional cone,
            # but account for the target's radius at the edge and at point-blank range.
            if dist > p.radius + e.radius + 10:
                target_angle = math.atan2(delta.y, delta.x)
                diff = abs(angle_diff(target_angle, p.attack_angle))
                target_margin = math.asin(clamp(e.radius / max(dist, e.radius), 0, .94))
                if diff > arc * .5 + target_margin * .58:
                    continue
            p.hit_ids.add(e.uid)
            impulse = forward * (230 if heavy else 145)
            self.damage_enemy(e, damage, impulse)
        if visuals:
            self.shake = max(self.shake, 5 if heavy else 2.5)
            self.hitstop = max(self.hitstop, .045 if heavy else .022)

    def handle_inputs(self, dt):
        p = self.player
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed(3)
        raw_mouse = pygame.mouse.get_pos()
        mpos = self.window_to_canvas(raw_mouse)

        if self.state != "playing":
            self.left_was_down = mouse[0]
            self.right_was_down = mouse[2]
            return

        # Update facing only for points inside the rendered game viewport.
        if mpos is not None:
            world_mouse = self.screen_to_world(mpos)
            aim = world_mouse - p.pos
            if aim.length_squared() > 5:
                p.facing = math.atan2(aim.y, aim.x)

        move = V2((1 if keys[pygame.K_d] or keys[pygame.K_RIGHT] else 0) -
                  (1 if keys[pygame.K_a] or keys[pygame.K_LEFT] else 0),
                  (1 if keys[pygame.K_s] or keys[pygame.K_DOWN] else 0) -
                  (1 if keys[pygame.K_w] or keys[pygame.K_UP] else 0))
        if move.length_squared() > 0:
            move = move.normalize()

        # Light attacks retain nearly full movement, while heavy attacks commit more.
        speed = 242
        if p.attack_phase == "windup":
            speed *= .94 if p.attack_kind == "light" else .76
        elif p.attack_phase == "active":
            speed *= .98 if p.attack_kind == "light" else .78
        elif p.attack_phase == "recovery":
            speed *= .90 if p.attack_kind == "light" else .68
        if p.dodge_timer > 0:
            move = p.dodge_dir
            speed = 630
        target_velocity = move * speed
        if p.dodge_timer <= 0:
            p.vel.x += (target_velocity.x - p.vel.x) * min(1, dt * 15)
            p.vel.y += (target_velocity.y - p.vel.y) * min(1, dt * 15)
        p.pos = self.resolve_world_collisions(p.pos + p.vel * dt, p.radius)
        if p.dodge_timer <= 0:
            p.vel *= max(0, 1 - dt * 10)

        # Keyboard actions are edge-triggered so holding a key doesn't repeatedly spend resources.
        for event in self.frame_events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT):
                    self.try_dodge(move)
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    idx = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}[event.key]
                    self.switch_weapon(WEAPON_ORDER[idx])
                elif event.key == pygame.K_e:
                    self.start_skill()
                elif event.key == pygame.K_q:
                    if p.souls >= 35:
                        p.souls -= 35
                        self.damage_arc(p.facing, 125, math.tau, 44, 120)
                        self.burst(p.pos, (131, 201, 189), 32, 270)
                        self.shake = max(self.shake, 6)
                        self.message = "SOUL BURST"
                        self.message_timer = .8
                elif event.key == pygame.K_TAB:
                    self.debug = not self.debug

        left_pressed = any(ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 for ev in self.frame_events)
        right_pressed = any(ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 3 for ev in self.frame_events)
        right_released = any(ev.type == pygame.MOUSEBUTTONUP and ev.button == 3 for ev in self.frame_events)

        # Buffered attack input is event-driven (captures quick clicks) and persists
        # through the full current attack/recovery. This fixes taps lost during combos.
        if left_pressed:
            self.attack_buffer = max(self.attack_buffer, .75)
        if mouse[0]:
            # Holding is also supported for repeat combos once recovery ends.
            self.attack_buffer = max(self.attack_buffer, .14)
        elif self.attack_buffer > 0 and p.attack_phase == "idle" and p.dodge_timer <= 0:
            self.attack_buffer = max(0.0, self.attack_buffer - dt)

        # Heavy attacks can be charged during a light recovery and queued for the first
        # legal frame after release. Event capture prevents missed right-button edges.
        if right_pressed and not p.dead:
            p.heavy_held = True
            p.heavy_charge = 0.0
        if mouse[2] and p.heavy_held:
            p.heavy_charge = min(1.25, p.heavy_charge + dt)
        should_release_heavy = right_released or (not mouse[2] and self.right_was_down)
        if should_release_heavy and p.heavy_held:
            if p.heavy_charge >= .12:
                self.heavy_pending = True
                self.heavy_pending_ttl = 1.6
            p.heavy_held = False
            p.heavy_charge = 0.0

        if self.heavy_pending and p.attack_phase == "idle" and p.dodge_timer <= 0:
            if p.start_attack(p.facing, True):
                self.heavy_pending = False
                self.heavy_pending_ttl = 0.0
            elif self.heavy_pending_ttl > 0:
                self.heavy_pending_ttl = max(0.0, self.heavy_pending_ttl - dt)
                if self.heavy_pending_ttl == 0:
                    self.heavy_pending = False
        elif self.attack_buffer > 0 and p.attack_phase == "idle" and p.dodge_timer <= 0 and not p.heavy_held and not self.heavy_pending:
            if p.start_attack(p.facing, False):
                self.attack_buffer = 0.0

        self.left_was_down = bool(mouse[0])
        self.right_was_down = bool(mouse[2])

    def try_dodge(self, move):
        if move.length_squared()==0:
            move=unit_angle(self.player.facing+math.pi)
        if self.player.begin_dodge(move):
            self.burst(self.player.pos,(131,176,167),7,125)

    def switch_weapon(self, weapon):
        p=self.player
        if p.weapon==weapon: return
        p.weapon=weapon
        p.attack_phase="idle";p.attack_timer=0;p.combo=0;p.combo_timer=0;p.heavy_held=False
        p.stamina=max(0,p.stamina-4)
        self.message=WEAPONS[weapon]["label"]
        self.message_timer=1.1

    def update(self, dt):
        self.decor_time+=dt
        self.elapsed+=dt if self.state=="playing" else 0
        self.message_timer=max(0,self.message_timer-dt)
        self.shake=max(0,self.shake-dt*25)
        self.flash=max(0,self.flash-dt)
        self.hitstop=max(0,self.hitstop-dt)
        if self.state!="playing":
            return
        self.player.update(dt,self)
        self._update_attack(dt)
        for e in self.enemies: e.update(dt,self)
        for pr in self.projectiles: pr.update(dt,self)
        for pt in self.particles: pt.update(dt)
        self.particles=[pt for pt in self.particles if pt.life>0]
        self.projectiles=[pr for pr in self.projectiles if not pr.dead]
        self.enemies=[e for e in self.enemies if not e.dead]
        for ft in self.floating_texts:
            ft["life"]-=dt;ft["pos"].y-=24*dt
        self.floating_texts=[ft for ft in self.floating_texts if ft["life"]>0]
        if not self.enemies:
            if self.wave_wait==0:
                self.wave_wait=1.9
                self.player.hp=min(self.player.max_hp,self.player.hp+9)
                self.player.stamina=min(self.player.max_stamina,self.player.stamina+32)
                self.message="THE VEIL SETTLES  ·  +9 VITALITY"
                self.message_timer=1.8
            else:
                self.wave_wait-=dt
                if self.wave_wait<=0:
                    self.spawn_wave(self.wave+1)
        # Ambience, drifting ash and torch motes.
        if len(self.particles) < 500 and random.random() < dt * 11:
            cam = self.camera()
            # Spawn ambient motes around the visible camera, not randomly across the whole world.
            sx = random.uniform(cam.x - 25, cam.x + W + 25)
            sy = random.uniform(cam.y - 25, cam.y + H + 25)
            col = random.choice([(105, 126, 120), (145, 105, 72), (119, 124, 108)])
            self.particles.append(Particle(V2(sx, sy), V2(random.uniform(-7, 8), random.uniform(-20, -4)), random.uniform(2.5, 5), 5, col, random.uniform(1, 2), .1, False))

    def draw_player(self, surface, camera):
        p=self.player; s=p.pos-camera
        x,y=int(s.x),int(s.y)
        if p.dodge_timer > 0:
            for i, ghost in enumerate(self.dodge_ghosts):
                off = -p.dodge_dir * (i + 1) * 13
                surface.blit(ghost, (int(x - 30 + off.x), int(y - 30 + off.y)))
        # Ground shadow.
        pygame.draw.ellipse(surface,(9,12,13),(x-25,y+6,50,20))
        # Dark cloak silhouette.
        cloak = (59, 64, 64) if p.hurt_flash<=0 else (139, 58, 49)
        pygame.draw.ellipse(surface,(17,20,21),(x-20,y-10,40,42))
        pygame.draw.ellipse(surface,cloak,(x-17,y-13,34,38))
        pygame.draw.polygon(surface,(39,45,46),[(x-15,y+5),(x-20,y+22),(x+16,y+23),(x+14,y+4)])
        # Shoulder plates and hood.
        pygame.draw.circle(surface,(92,91,78),(x-11,y-3),7)
        pygame.draw.circle(surface,(84,86,79),(x+10,y-4),7)
        pygame.draw.circle(surface,(23,27,28),(x,y-12),12)
        pygame.draw.circle(surface,(132,121,95),(x,y-13),11,2)
        # Narrow eyes / visor.
        eye=unit_angle(p.facing)
        eye_pos=V2(x,y-13)+eye*6
        blit_glow(surface, eye_pos, 7, (225, 177, 92), 34)
        pygame.draw.line(surface,(236,195,116),(int(eye_pos.x-eye.y*3),int(eye_pos.y+eye.x*3)),(int(eye_pos.x+eye.y*3),int(eye_pos.y-eye.x*3)),2)
        # Weapon in hand, matching the equipped kit.
        d=unit_angle(p.facing); side=V2(-d.y,d.x)
        hand=V2(x,y)+d*10+side*5
        if p.weapon=="Gravetide":
            for sign in (-1,1):
                base=hand+side*sign*5
                tip=base+d*36+side*sign*10
                blit_glow(surface, tip, 10, (117, 218, 199), 36)
                pygame.draw.line(surface,(84,61,44),(int(base.x),int(base.y)),(int(base.x+d.x*11),int(base.y+d.y*11)),4)
                pygame.draw.line(surface,(156,218,204),(int(base.x+d.x*8),int(base.y+d.y*8)),(int(tip.x),int(tip.y)),4)
                pygame.draw.circle(surface,(212,207,180),(int(tip.x),int(tip.y)),2)
        else:
            length=37 if p.weapon=="Rookfang" else 49
            tip=hand+d*length
            col=WEAPONS[p.weapon]["color"]
            blit_glow(surface, tip, 12 if p.weapon=="Rookfang" else 16, col, 48)
            pygame.draw.line(surface,(86,61,42),(int(hand.x),int(hand.y)),(int(hand.x+d.x*10),int(hand.y+d.y*10)),5)
            pygame.draw.line(surface,col,(int(hand.x+d.x*7),int(hand.y+d.y*7)),(int(tip.x),int(tip.y)),4 if p.weapon=="Rookfang" else 7)
            pygame.draw.line(surface,(255,237,190),(int(tip.x),int(tip.y)),(int(tip.x+d.x*7),int(tip.y+d.y*7)),2)
        # Attack arcs: angle-driven blade arc with taper and additive sparks.
        if p.attack_phase in ("windup","active","recovery"):
            w=WEAPONS[p.weapon]
            heavy=p.attack_kind=="heavy"
            progress=1-p.attack_timer/max(.001,(w["heavy_windup"]+w["heavy_active"]+w["recovery"] if heavy else w["windup"]+w["active"]+w["recovery"]))
            reach=w["heavy_range"] if heavy else w["range"]
            arc=w["arc"]*(1.15 if p.combo==2 else .92 if p.combo==3 else 1)
            if p.attack_phase=="active":
                intensity=1.0
            elif p.attack_phase=="windup": intensity=.46
            else: intensity=.30
            start=p.attack_angle-arc*.5;end=p.attack_angle+arc*.5
            pts=[]
            steps=18
            for i in range(steps+1):
                a=start+(end-start)*i/steps
                r=reach*(.56+.44*math.sin(math.pi*i/steps))
                pts.append((int(x+math.cos(a)*r),int(y+math.sin(a)*r)))
            if len(pts)>1:
                col=WEAPONS[p.weapon]["color"]
                if p.attack_phase == "active":
                    glow_pos = V2(x, y) + unit_angle(p.attack_angle) * reach * .66
                    blit_glow(surface, glow_pos, 36 if not heavy else 47, col, 39 if not heavy else 56)
                for j in range(3):
                    shade = tuple(int(c * intensity * (1-j*.15)) for c in col)
                    pygame.draw.lines(surface, shade, False, pts, max(1,7-j*2))
        if p.invuln>0 and p.dodge_timer<=0 and int(self.decor_time*25)%2==0:
            pygame.draw.circle(surface,(157,220,205),(x,y),24,1)
        if p.heavy_held:
            radius=int(12+22*min(1,p.heavy_charge/1.1))
            pygame.draw.circle(surface,(GOLD),(x,y),radius,1)

    def draw_enemy(self, surface, enemy, camera):
        s=enemy.pos-camera;x,y=int(s.x),int(s.y);d=ENEMY_DATA[enemy.kind]
        if not (-80<x<W+80 and -80<y<H+80):return
        is_boss=enemy.kind=="Grave Warden"
        radius=enemy.radius
        # Cast shadow and body silhouette.        pygame.draw.ellipse(surface,(9,12,13),(x-radius-8,int(y+radius*.38),radius*2+16, max(8,int(radius*.72))))
        body=d["color"] if enemy.hit_flash<=0 else (245,220,180)
        if is_boss:
            pygame.draw.ellipse(surface,(37,30,30),(x-38,y-30,76,78))
            pygame.draw.polygon(surface,(55,37,37),[(x-29,y-8),(x-47,y+21),(x-16,y+30),(x+23,y+30),(x+46,y+14),(x+27,y-10)])
            pygame.draw.circle(surface,body,(x,y-10),25)
            pygame.draw.circle(surface,(74,52,47),(x,y-10),29,3)
            pygame.draw.polygon(surface,(109,82,64),[(x-18,y-28),(x-33,y-47),(x-7,y-35),(x,y-29),(x+14,y-45),(x+17,y-23)])
            pygame.draw.line(surface,(232,148,112),(x-11,y-13),(x-3,y-12),3)
            pygame.draw.line(surface,(232,148,112),(x+5,y-12),(x+13,y-13),3)
            # Huge cleaver.
            a=enemy.facing+0.45
            p1=V2(x,y)+unit_angle(a)*18; p2=V2(x,y)+unit_angle(a)*51
            p3=p2+unit_angle(a+1.15)*21
            pygame.draw.line(surface,(77,57,45),(int(p1.x),int(p1.y)),(int(p2.x),int(p2.y)),7)
            pygame.draw.line(surface,(156,152,132),(int(p2.x),int(p2.y)),(int(p3.x),int(p3.y)),8)
        elif enemy.kind=="Cinder Adept":
            pygame.draw.ellipse(surface,(43,39,34),(x-18,y-13,36,38))
            pygame.draw.polygon(surface,body,[(x,y-radius-3),(x+radius,y+radius),(x-radius,y+radius)])
            pygame.draw.circle(surface,(37,35,31),(x,y-5),10)
            pygame.draw.circle(surface,(232,132,77),(int(x+math.cos(enemy.facing)*6),int(y-5+math.sin(enemy.facing)*6)),3)
            pygame.draw.line(surface,(116,81,53),(x+8,y+2),(int(x+math.cos(enemy.facing)*27),int(y+math.sin(enemy.facing)*27)),4)
        else:
            # Ragged hollow body and hood.
            pygame.draw.ellipse(surface,(49,48,44),(x-18,y-8,36,31))
            pygame.draw.polygon(surface,body,[(x-14,y+1),(x-19,y+18),(x-8,y+14),(x-2,y+24),(x+5,y+14),(x+17,y+21),(x+15,y-1)])
            pygame.draw.circle(surface,(48,43,39),(x,y-8),12)
            pygame.draw.polygon(surface,(72,65,57),[(x-13,y-6),(x,y-24),(x+13,y-6)])
            eye=V2(x,y-8)+unit_angle(enemy.facing)*7
            pygame.draw.circle(surface,(223,115,73), (int(eye.x),int(eye.y)),2)
            pygame.draw.line(surface,(109,94,76),(x+5,y+2),(int(x+math.cos(enemy.facing)*24),int(y+math.sin(enemy.facing)*24)),4)
        # Readable telegraph: ring plus directional danger wedge.
        if enemy.state=="windup":
            r=radius+13+3*math.sin(self.decor_time*22)
            pygame.draw.circle(surface,(179,78,65),(x,y),int(r),2)
            end=V2(x,y)+unit_angle(enemy.facing)*(radius+34)
            pygame.draw.line(surface,(221,101,81),(x,y),(int(end.x),int(end.y)),3)
            pygame.draw.circle(surface,(241,139,102),(int(end.x),int(end.y)),4)
        if enemy.hp<enemy.max_hp or is_boss:
            bw=70 if is_boss else 42; bh=6
            rect=pygame.Rect(x-bw//2,y-radius-20,bw,bh)
            pygame.draw.rect(surface,(19,21,21),rect,border_radius=2)
            inn=rect.inflate(-2,-2);inn.width=max(0,int(inn.width*clamp(enemy.hp/enemy.max_hp,0,1)))
            if inn.width: pygame.draw.rect(surface,(190,75,63) if not is_boss else (203,76,64),inn,border_radius=2)

    def draw_projectile(self, surface, pr, camera):
        p=pr.pos-camera
        if pr.owner=="enemy":
            blit_glow(surface,p,18,pr.color,65)
        pygame.draw.circle(surface,pr.color,(int(p.x),int(p.y)),int(pr.radius))
        pygame.draw.circle(surface,(255,218,163),(int(p.x),int(p.y)),max(2,int(pr.radius*.42)))
        trail=p-safe_normalize(pr.vel)*16
        pygame.draw.line(surface,(*pr.color,), (int(trail.x),int(trail.y)),(int(p.x),int(p.y)),3)

    def draw_hud(self, surface):
        p=self.player
        # Upper-left health plate.
        panel=pygame.Rect(22,18,330,100)
        pygame.draw.rect(surface,(15,18,19),(panel.x+3,panel.y+4,panel.width,panel.height),border_radius=8)
        pygame.draw.rect(surface,(30,34,34),panel,border_radius=8)
        pygame.draw.rect(surface,(100,87,66),panel,1,border_radius=8)
        draw_text(surface,self.font_smallcaps,"ASHEN VOW  /  WANDERER",(panel.x+16,panel.y+10),GOLD)
        draw_text(surface,self.font_s,f"{int(max(0,p.hp)):03d} / {int(p.max_hp)}",(panel.right-16,panel.y+31),TEXT,"topright")
        draw_bar(surface,pygame.Rect(panel.x+16,panel.y+31,206,13),p.hp,p.max_hp,(175,66,61),border=(93,65,59))
        draw_text(surface,self.font_s,"VITALITY",(panel.x+16,panel.y+47),MUTED)
        draw_bar(surface,pygame.Rect(panel.x+16,panel.y+65,206,10),p.stamina,p.max_stamina,(165,174,113),border=(74,82,61))
        draw_text(surface,self.font_s,"STAMINA",(panel.x+16,panel.y+78),MUTED)
        # Soul counter and wave plate.
        right=pygame.Rect(W-238,18,216,72)
        pygame.draw.rect(surface,(22,25,25),right,border_radius=7);pygame.draw.rect(surface,(86,80,63),right,1,border_radius=7)
        draw_text(surface,self.font_smallcaps,"DESCENT",(right.x+14,right.y+10),MUTED)
        draw_text(surface,self.font_b,f"{self.wave:02d}",(right.x+82,right.y+6),GOLD)
        draw_text(surface,self.font_smallcaps,"SOULS",(right.x+128,right.y+10),MUTED)
        draw_text(surface,self.font_m,f"{p.souls:04d}",(right.x+128,right.y+30),PALE_GOLD)
        # Weapon plate / controls along bottom.
        bottom=pygame.Rect(22,H-132,500,68)
        pygame.draw.rect(surface,(16,19,20),bottom,border_radius=7);pygame.draw.rect(surface,(81,79,67),bottom,1,border_radius=7)
        for i,name in enumerate(WEAPON_ORDER):
            r=pygame.Rect(bottom.x+10+i*160,bottom.y+9,150,49)
            selected=p.weapon==name
            bg=(49,45,35) if selected else (27,31,31)
            border=GOLD if selected else (57,63,61)
            pygame.draw.rect(surface,bg,r,border_radius=5);pygame.draw.rect(surface,border,r,1,border_radius=5)
            draw_text(surface,self.font_smallcaps,f"[{i+1}]",(r.x+9,r.y+8),GOLD if selected else MUTED)
            label={"Rookfang":"ROOKFANG","Gravetide":"GRAVETIDE","Oathbreaker":"OATHBREAKER"}[name]
            draw_text(surface,self.font_smallcaps,label,(r.x+36,r.y+8),TEXT if selected else MUTED)
            draw_text(surface,self.font_s,["Balanced","Twin blades","Greatblade"][i],(r.x+36,r.y+26),WEAPONS[name]["color"] if selected else MUTED)
        # Skill status lower right.
        skill=WEAPONS[p.weapon]
        plate=pygame.Rect(W-295,H-132,273,69)
        pygame.draw.rect(surface,(16,19,20),plate,border_radius=7);pygame.draw.rect(surface,(83,80,66),plate,1,border_radius=7)
        draw_text(surface,self.font_smallcaps,"WEAPON ART  [E]",(plate.x+12,plate.y+9),MUTED)
        cd=p.skill_cd
        draw_text(surface,self.font_m,skill["skill"],(plate.x+12,plate.y+26),skill["color"] if cd<=0 else MUTED)
        if cd>0:
            draw_text(surface,self.font_s,f"{cd:.1f}s",(plate.right-13,plate.y+27),MUTED,"topright")
        else:
            draw_text(surface,self.font_smallcaps,"READY",(plate.right-13,plate.y+29),TEAL,"topright")
        # Boss bar top-middle.
        boss=next((e for e in self.enemies if e.kind=="Grave Warden"),None)
        if boss:
            bw=420;rr=pygame.Rect(W//2-bw//2,24,bw,23)
            draw_text(surface,self.font_smallcaps,"GRAVE WARDEN  ·  THE UNBURIED",(W//2,7),PALE_GOLD,"midtop")
            draw_bar(surface,rr,boss.hp,boss.max_hp,(161,54,49),border=(129,87,64))
        # Dedicated footer makes controls readable without overlapping the weapon cards.
        controls = pygame.Rect(W//2-300, H-43, 600, 25)
        pygame.draw.rect(surface, (15, 19, 20), controls, border_radius=6)
        pygame.draw.rect(surface, (65, 68, 61), controls, 1, border_radius=6)
        draw_text(surface, self.font_smallcaps,
                  "WASD MOVE  ·  LMB ATTACK  ·  RMB HEAVY  ·  SPACE DODGE  ·  E SKILL  ·  Q BURST",
                  controls.center, (177, 181, 168), "center", False)
        # Small performance readout, useful while tuning effects on different PCs.
        draw_text(surface, self.font_smallcaps, f"{int(self.clock.get_fps()):03d} FPS",
                  (W-18, H-16), (137, 146, 138), "bottomright", False)
        if p.heavy_held:
            text="CHARGING HEAVY"
            draw_text(surface,self.font_smallcaps,text,(W//2,H-118),GOLD,"midbottom")
            pygame.draw.rect(surface,(32,30,25),(W//2-90,H-109,180,5),border_radius=2)
            pygame.draw.rect(surface,GOLD,(W//2-90,H-109,int(180*min(1,p.heavy_charge/1.05)),5),border_radius=2)

    def draw_reticle(self, surface):
        # Keep cursor and hit direction aligned even with a non-16:10 resizable window.
        logical = self.window_to_canvas(pygame.mouse.get_pos())
        if logical is None:
            return
        mx, my = int(logical.x), int(logical.y)
        if not (0 <= mx < W and 0 <= my < H):
            return
        color = (219, 190, 127) if self.state == "playing" else (130, 126, 108)
        pygame.draw.circle(surface, color, (mx, my), 8, 1)
        pygame.draw.circle(surface, color, (mx, my), 2)
        pygame.draw.line(surface, color, (mx-13, my), (mx-5, my), 1)
        pygame.draw.line(surface, color, (mx+5, my), (mx+13, my), 1)
        pygame.draw.line(surface, color, (mx, my-13), (mx, my-5), 1)
        pygame.draw.line(surface, color, (mx, my+5), (mx, my+13), 1)

    def draw_minimap(self,surface):
        x,y= W-174, 108
        rect=pygame.Rect(x,y,152,100)
        pygame.draw.rect(surface,(14,17,18),(rect.x+3,rect.y+3,rect.width,rect.height),border_radius=5)
        pygame.draw.rect(surface,(28,33,33),rect,border_radius=5);pygame.draw.rect(surface,(82,83,72),rect,1,border_radius=5)
        scale_x=(rect.width-10)/WORLD_W;scale_y=(rect.height-10)/WORLD_H
        for o in self.obstacles:
            rr=pygame.Rect(rect.x+5+int(o.x*scale_x),rect.y+5+int(o.y*scale_y),max(2,int(o.width*scale_x)),max(2,int(o.height*scale_y)))
            pygame.draw.rect(surface,(72,74,68),rr)
        for e in self.enemies:
            q=(rect.x+5+int(e.pos.x*scale_x),rect.y+5+int(e.pos.y*scale_y))
            pygame.draw.circle(surface,(221,93,72) if e.kind!="Grave Warden" else (255,188,109),q,3 if e.kind!="Grave Warden" else 5)
        p=self.player.pos
        q=(rect.x+5+int(p.x*scale_x),rect.y+5+int(p.y*scale_y))
        pygame.draw.circle(surface,(190,221,204),q,4)
        pygame.draw.circle(surface,(228,223,184),q,7,1)

    def draw_overlay(self):
        s=self.canvas
        if self.state=="title":
            self.overlay_layer.fill((4,7,8,166));s.blit(self.overlay_layer,(0,0))
            # emblem
            cx,cy=W//2,215
            pygame.draw.circle(s,(106,84,57),(cx,cy),71,2)
            pygame.draw.circle(s,(53,62,58),(cx,cy),58,1)
            pygame.draw.polygon(s,(174,139,84),[(cx,cy-49),(cx+14,cy-7),(cx+41,cy+18),(cx,cy+49),(cx-39,cy+18),(cx-14,cy-7)],2)
            pygame.draw.line(s,(205,170,110),(cx,cy-50),(cx,cy+51),2)
            draw_text(s,self.font_title,"ASHEN VEIL",(W//2,309),PALE_GOLD,"midtop",False)
            draw_text(s,self.font_subtitle,"A fallen kingdom. One last ember.",(W//2,371),(166,166,151),"midtop",False)
            pygame.draw.line(s,(111,91,62),(W//2-180,415),(W//2+180,415),1)
            draw_text(s,self.font_m,"DARK FANTASY COMBAT SANDBOX",(W//2,441),TEXT,"midtop",False)
            draw_text(s,self.font_s,"TEST YOUR WEAPON. LEARN THE TIMING. SURVIVE THE DESCENT.",(W//2,472),MUTED,"midtop",False)
            btn=pygame.Rect(W//2-115,535,230,49)
            pygame.draw.rect(s,(56,48,34),btn,border_radius=4);pygame.draw.rect(s,GOLD,btn,1,border_radius=4)
            draw_text(s,self.font_m,"ENTER THE RUINS",btn.center,PALE_GOLD,"center",False)
            draw_text(s,self.font_s,"ENTER  /  CLICK TO BEGIN",(W//2,603),MUTED,"midtop",False)
            draw_text(s,self.font_s,"WASD MOVE   ·   LMB ATTACK   ·   RMB CHARGED HEAVY   ·   SPACE DODGE",(W//2,H-44), (121,127,119),"midtop",False)
        elif self.state=="paused":
            self.overlay_layer.fill((3,5,6,178));s.blit(self.overlay_layer,(0,0))
            draw_text(s,self.font_title,"PAUSED",(W//2,286),PALE_GOLD,"midtop",False)
            draw_text(s,self.font_m,"THE RUINS WILL WAIT FOR NO ONE",(W//2,354),MUTED,"midtop",False)
            draw_text(s,self.font_m,"ESC  RESUME     R  RESTART     Q  RETURN TO TITLE",(W//2,425),TEXT,"midtop",False)
        elif self.state=="gameover":
            self.overlay_layer.fill((11, 3, 5, 148))
            s.blit(self.overlay_layer, (0, 0))
            panel = pygame.Rect(W//2-340, 226, 680, 326)
            pygame.draw.rect(s, (19, 15, 16), panel, border_radius=12)
            pygame.draw.rect(s, (121, 76, 61), panel, 1, border_radius=12)
            pygame.draw.line(s, (117, 73, 58), (panel.x+100, panel.y+20), (panel.right-100, panel.y+20), 1)
            draw_text(s,self.font_title,"YOU HAVE FALLEN",(W//2,270),(225,130,104),"midtop",False)
            draw_text(s,self.font_m,f"DESCENT {self.wave:02d}   ·   {self.kills} SLAIN",(W//2,350),TEXT,"midtop",False)
            draw_text(s,self.font_m,f"{self.player.souls:04d} SOULS CARRIED",(W//2,382),GOLD,"midtop",False)
            btn = pygame.Rect(W//2-110, 432, 220, 43)
            pygame.draw.rect(s, (48, 34, 29), btn, border_radius=5)
            pygame.draw.rect(s, (148, 95, 69), btn, 1, border_radius=5)
            draw_text(s,self.font_m,"R  ·  RISE AGAIN",btn.center,PALE_GOLD,"center",False)
            draw_text(s,self.font_s,"The veil does not forgive. It only remembers.",(W//2,492),MUTED,"midtop",False)
        if self.message_timer>0 and self.state=="playing":
            a=int(255*min(1,self.message_timer/.6))
            label = _cached_text(self.font_m, self.message, PALE_GOLD).copy()
            label.set_alpha(a)
            r=label.get_rect(center=(W//2,145))
            s.blit(label,r)
            pygame.draw.line(s,(105,85,57),(W//2-95,161),(W//2+95,161),1)

    def render(self):
        self.canvas.fill(BG)
        cam=self.camera()
        off=V2(random.uniform(-self.shake,self.shake),random.uniform(-self.shake,self.shake)) if self.shake>0.1 else V2()
        # Scrollable world and subtle torch pools.
        self.canvas.blit(self.background,(-int(cam.x+off.x),-int(cam.y+off.y)))
        # Low, cached amber light on the central engraved seal lifts the floor
        # values without washing out the dark-fantasy palette.
        seal_pos = V2(WORLD_W * .5, WORLD_H * .52) - cam - off
        blit_glow(self.canvas, seal_pos, 184, (159, 120, 68), 21)
        blit_glow(self.canvas, seal_pos, 92, (177, 137, 78), 14)
        for p in self.torches:
            q=p-cam-off
            if -70<q.x<W+70 and -70<q.y<H+70:
                blit_glow(self.canvas,q,66,(226,146,76),42+int(10*math.sin(self.decor_time*5+q.x)))
                pygame.draw.polygon(self.canvas,(255,184,94),[(int(q.x),int(q.y-10)),(int(q.x-5),int(q.y+3)),(int(q.x+2),int(q.y+7)),(int(q.x+7),int(q.y-2))])
        # Atmospheric floor wisps drift across camera view.
        for j in range(7):
            yy=int((j*137+self.decor_time*7)%H)
            self.canvas.blit(self.fog_band,(int(20*math.sin(self.decor_time*.2+j)),yy))
        for pr in self.projectiles:self.draw_projectile(self.canvas,pr,cam+off)
        for e in sorted(self.enemies,key=lambda q:q.pos.y):self.draw_enemy(self.canvas,e,cam+off)
        self.draw_player(self.canvas,cam+off)
        for pt in self.particles:pt.draw(self.canvas,cam+off)
        # floating combat text
        for ft in self.floating_texts:
            pos=ft["pos"]-cam
            alpha=int(255*clamp(ft["life"]/ft["max"],0,1))
            img = _cached_text(self.font_s, ft["text"], ft["color"]).copy()
            img.set_alpha(alpha)
            self.canvas.blit(img,img.get_rect(center=(int(pos.x),int(pos.y))))
        # vignette & subtle hurt edge flash
        self.canvas.blit(self.vignette, (0, 0))
        if self.player.hurt_flash > 0:
            alpha = int(34 * self.player.hurt_flash / .25)
            self.hurt_overlay.fill((118, 22, 18, alpha))
            self.canvas.blit(self.hurt_overlay, (0, 0))
        if self.flash > 0:
            alpha = int(20 * self.flash / .12)
            self.flash_overlay.fill((255, 228, 185, alpha))
            self.canvas.blit(self.flash_overlay, (0, 0))
        if self.state in ("playing", "paused"):
            self.draw_minimap(self.canvas)
            self.draw_hud(self.canvas)
            self.draw_reticle(self.canvas)
        self.draw_overlay()
        # Preserve the original 16:10 design aspect instead of stretching the HUD
        # and distorting mouse aim on maximized/widescreen monitors.
        self.screen.fill((5, 7, 8))
        viewport = self.viewport_rect()
        scaled = pygame.transform.smoothscale(self.canvas, viewport.size)
        self.screen.blit(scaled, viewport.topleft)
        pygame.display.flip()

    def process_events(self):
        self.frame_events=[]
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                self.running=False
            elif event.type==pygame.VIDEORESIZE:
                self.screen=pygame.display.set_mode(event.size,pygame.RESIZABLE|pygame.DOUBLEBUF)
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    if self.state=="playing":self.state="paused"
                    elif self.state=="paused":self.state="playing"
                    elif self.state=="title":self.running=False
                if self.state=="title" and event.key in (pygame.K_RETURN,pygame.K_SPACE):self.new_run()
                elif self.state=="paused":
                    if event.key==pygame.K_r:self.new_run()
                    elif event.key==pygame.K_q:self.state="title"
                elif self.state=="gameover" and event.key==pygame.K_r:self.new_run()
            elif event.type==pygame.MOUSEBUTTONDOWN:
                if self.state=="title" and event.button==1:
                    self.new_run()
                    # Consume the menu click so it cannot also enqueue a combat attack.
                    continue
            self.frame_events.append(event)

    def run(self):
        self.floating_texts=[]
        while self.running:
            dt=min(self.clock.tick(FPS)/1000,0.033)
            self.process_events()
            if self.state=="playing":
                self.handle_inputs(dt)
                if self.hitstop>0:
                    # Retain input polling but momentarily freeze simulated time.
                    update_dt=dt*.12
                else:update_dt=dt
                self.update(update_dt)
            else:
                self.update(dt)
            self.render()
        pygame.quit()


def main():
    Game().run()

if __name__ == "__main__":
    main()