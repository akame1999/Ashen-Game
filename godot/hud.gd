class_name Hud
extends CanvasLayer
## Dark-fantasy HUD drawn in code (960x540 space): ornate bars, portrait, hotbar with cooldowns,
## souls counter, fog-of-war minimap, hit/low-HP edges, YOU DIED screen and pause menu.

const GOLD := Color(0.72, 0.58, 0.32)
const GOLD_L := Color(0.95, 0.82, 0.52)
const GOLD_D := Color(0.30, 0.22, 0.10)
const BG := Color(0.04, 0.04, 0.07, 0.9)
const TXT := Color(0.9, 0.88, 0.82)
const CELL := 100.0
const TOTAL_CELLS := 30
const HOTBAR_ITEMS: Array = [
	["R", "Flask", 5, "flask"],
	["1", "Rookfang", 0, "weapon_1"],
	["2", "Gravetide", 7, "weapon_2"],
	["3", "Oathbreaker", 1, "weapon_3"]
]

var area_name := "Gravework Keep"
var player: Player
var room: Room
var font: Font
var canvas: Control
var _t := 0.0
var _hp_trail := 1.0
var _hp_last := 0
var _flash := 0.0
var _souls_shown := 0.0
var _souls_last := 0
var _popups: Array = []
var _explored := {}
var _last_cd := {}
var _ready_flash := {}
var _death_t := 0.0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	layer = 10
	font = load("res://assets/fonts/Cinzel-Variable.ttf")
	canvas = Control.new()
	canvas.set_anchors_preset(Control.PRESET_FULL_RECT)
	canvas.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(canvas)
	canvas.draw.connect(_paint)
	player = get_parent().get_node("Player")
	room = get_parent().get_node("Room")
	_hp_last = player.hp
	_souls_last = player.souls
	_souls_shown = float(player.souls)
	_hp_trail = float(player.hp) / player.max_hp


func _unhandled_input(e: InputEvent) -> void:
	if e is InputEventKey and e.pressed and not e.echo:
		if e.physical_keycode == KEY_ESCAPE:
			get_tree().paused = not get_tree().paused
		elif get_tree().paused and (e.physical_keycode == KEY_ENTER or e.physical_keycode == KEY_KP_ENTER):
			get_tree().paused = false
			get_tree().reload_current_scene()


func _process(delta: float) -> void:
	_t += delta
	var ratio := float(player.hp) / player.max_hp
	if _hp_trail > ratio:
		_hp_trail = maxf(ratio, _hp_trail - delta * 0.35)
	else:
		_hp_trail = ratio
	if player.hp < _hp_last:
		_flash = 0.3
	_hp_last = player.hp
	_flash = maxf(0.0, _flash - delta)
	if player.souls > _souls_last:
		_popups.append({"text": "+%d" % (player.souls - _souls_last), "t": 0.0})
	_souls_last = player.souls
	var diff := float(player.souls) - _souls_shown
	if absf(diff) > 0.5:
		_souls_shown += signf(diff) * maxf(1.0, absf(diff) * 6.0 * delta)
	else:
		_souls_shown = float(player.souls)
	for i in range(_popups.size() - 1, -1, -1):
		_popups[i]["t"] += delta
		if _popups[i]["t"] > 1.2:
			_popups.remove_at(i)
	var cell := int(floor((player.global_position.x - Room.LEVEL_LEFT) / CELL))
	for c in range(cell - 2, cell + 3):
		if c >= 0 and c < TOTAL_CELLS:
			_explored[c] = true
	for key in Player.CD_TIME:
		var cd := float(player.cd.get(key, 0.0))
		if float(_last_cd.get(key, 0.0)) > 0.0 and cd <= 0.0:
			_ready_flash[key] = 0.35
		_last_cd[key] = cd
		_ready_flash[key] = maxf(0.0, float(_ready_flash.get(key, 0.0)) - delta)
	if player.state == Player.State.DEAD:
		_death_t += delta
	else:
		_death_t = 0.0
	canvas.queue_redraw()


# ---------- drawing helpers ----------
func _text(s: String, pos: Vector2, size: int, col := TXT, width := -1.0, align := HORIZONTAL_ALIGNMENT_LEFT) -> void:
	canvas.draw_string(font, pos + Vector2(1, 1), s, align, width, size, Color(0, 0, 0, 0.8 * col.a))
	canvas.draw_string(font, pos, s, align, width, size, col)


func _vignette(col: Color, depth := 90.0) -> void:
	var w := canvas.size.x
	var h := canvas.size.y
	var c0 := Color(col.r, col.g, col.b, 0.0)
	var cols := PackedColorArray([col, col, c0, c0])
	canvas.draw_polygon(PackedVector2Array([Vector2(0, 0), Vector2(w, 0), Vector2(w, depth), Vector2(0, depth)]), cols)
	canvas.draw_polygon(PackedVector2Array([Vector2(0, h), Vector2(w, h), Vector2(w, h - depth), Vector2(0, h - depth)]), cols)
	canvas.draw_polygon(PackedVector2Array([Vector2(0, 0), Vector2(0, h), Vector2(depth, h), Vector2(depth, 0)]), cols)
	canvas.draw_polygon(PackedVector2Array([Vector2(w, 0), Vector2(w, h), Vector2(w - depth, h), Vector2(w - depth, 0)]), cols)


func _stud(c: Vector2, r: float, col: Color) -> void:
	canvas.draw_colored_polygon(PackedVector2Array([c + Vector2(0, -r), c + Vector2(r, 0), c + Vector2(0, r), c + Vector2(-r, 0)]), col)


func _frame(r: Rect2) -> void:
	canvas.draw_rect(r.grow(3.0), GOLD_D)
	canvas.draw_rect(r, BG)
	canvas.draw_rect(r.grow(1.0), GOLD, false, 1.0)
	for corner in [r.position, Vector2(r.end.x, r.position.y), Vector2(r.position.x, r.end.y), r.end]:
		_stud(corner, 3.0, GOLD_L)


func _bar(rect: Rect2, ratio: float, trail: float, c_main: Color, c_light: Color, ticks := 0, pulse := 0.0) -> void:
	var x := rect.position.x
	var y := rect.position.y
	var w := rect.size.x
	var h := rect.size.y
	var tip := h * 0.55
	var outline := PackedVector2Array([Vector2(x - 1, y - 1), Vector2(x + w + 1, y - 1), Vector2(x + w + tip + 1, y + h / 2.0), Vector2(x + w + 1, y + h + 1), Vector2(x - 1, y + h + 1)])
	canvas.draw_colored_polygon(outline, GOLD_D)
	canvas.draw_colored_polygon(PackedVector2Array([Vector2(x, y), Vector2(x + w, y), Vector2(x + w + tip - 1, y + h / 2.0), Vector2(x + w, y + h), Vector2(x, y + h)]), BG)
	if trail > ratio:
		canvas.draw_rect(Rect2(x + w * ratio, y, w * (trail - ratio), h), Color(0.95, 0.85, 0.8, 0.55))
	var fw := w * clampf(ratio, 0.0, 1.0)
	if fw > 0.5:
		var m := c_main.lerp(c_light, pulse)
		canvas.draw_rect(Rect2(x, y, fw, h), m)
		canvas.draw_rect(Rect2(x, y, fw, h * 0.4), Color(c_light.r, c_light.g, c_light.b, 0.75))
		canvas.draw_rect(Rect2(x, y + h * 0.75, fw, h * 0.25), Color(0, 0, 0, 0.25))
		if ratio >= 0.999:
			canvas.draw_colored_polygon(PackedVector2Array([Vector2(x + w, y), Vector2(x + w + tip - 1, y + h / 2.0), Vector2(x + w, y + h)]), m)
	for i in range(1, ticks):
		var tx := x + w * i / ticks
		canvas.draw_line(Vector2(tx, y), Vector2(tx, y + h), Color(0, 0, 0, 0.35), 1.0)
	var line := outline.duplicate()
	line.append(outline[0])
	canvas.draw_polyline(line, GOLD, 1.0)


# ---------- main paint ----------
func _paint() -> void:
	var ratio := float(player.hp) / player.max_hp
	if _flash > 0.0:
		_vignette(Color(0.8, 0.05, 0.05, 0.5 * _flash / 0.3))
	if ratio < 0.3 and player.state != Player.State.DEAD:
		_vignette(Color(0.7, 0.03, 0.05, (0.18 + 0.12 * sin(_t * 5.0)) * (0.3 - ratio) / 0.3 + 0.05), 70.0)
	_paint_top_left(ratio)
	_paint_hotbar()
	_paint_souls()
	_paint_minimap()
	if _t < 14.0:
		var a := clampf((14.0 - _t) / 2.0, 0.0, 1.0)
		_text("A / D  move   ·   Space  jump (x2)   ·   J  attack   ·   Esc  pause", Vector2(180, 118), 12, Color(0.85, 0.82, 0.75, 0.8 * a), 600.0, HORIZONTAL_ALIGNMENT_CENTER)
	if _death_t > 0.0:
		var a := clampf(_death_t / 1.2, 0.0, 1.0)
		canvas.draw_rect(Rect2(Vector2.ZERO, canvas.size), Color(0, 0, 0, 0.55 * a))
		_text("YOU DIED", Vector2(canvas.size.x / 2.0 - 250.0, 290), 56, Color(0.72, 0.08, 0.1, a), 500.0, HORIZONTAL_ALIGNMENT_CENTER)
	if get_tree().paused:
		_paint_pause()


func _paint_top_left(ratio: float) -> void:
	var c := Vector2(40, 40)
	canvas.draw_circle(c, 31, Color(0, 0, 0, 0.5))
	canvas.draw_circle(c, 29, GOLD_D)
	canvas.draw_arc(c, 28.5, 0, TAU, 48, GOLD, 2.0)
	canvas.draw_circle(c, 25, BG)
	canvas.draw_arc(c, 25, 0, TAU, 48, GOLD_D, 1.0)
	for i in 8:
		_stud(c + Vector2(29, 0).rotated(i * TAU / 8.0), 2.6, GOLD_L if i % 2 == 0 else GOLD)
	canvas.draw_circle(c + Vector2(0, -2), 12, Color(0.16, 0.16, 0.22))
	canvas.draw_circle(c + Vector2(1, -1), 7, Color(0.80, 0.69, 0.61))
	canvas.draw_arc(c + Vector2(0, -2), 12, PI, TAU, 16, Color(0.3, 0.3, 0.4), 1.0)
	canvas.draw_colored_polygon(PackedVector2Array([c + Vector2(-8, 4), c + Vector2(8, 4), c + Vector2(13, 18), c + Vector2(-13, 18)]), Color(0.5, 0.1, 0.14))
	var b := c + Vector2(22, 22)
	canvas.draw_circle(b, 11, GOLD_D)
	canvas.draw_circle(b, 9, BG)
	canvas.draw_arc(b, 10, 0, TAU, 24, GOLD, 1.5)
	_text(str(player.level), b + Vector2(-8, 5), 14, GOLD_L, 16.0, HORIZONTAL_ALIGNMENT_CENTER)
	_text("Ashen Veil", Vector2(82, 20), 15, TXT)
	canvas.draw_line(Vector2(82, 23), Vector2(190, 23), Color(GOLD.r, GOLD.g, GOLD.b, 0.6), 1.0)
	var hp_rect := Rect2(82, 28, 240, 14)
	var pulse := 0.0
	if ratio < 0.3:
		pulse = 0.5 + 0.5 * sin(_t * 6.0)
	_bar(hp_rect, ratio, _hp_trail, Color(0.62, 0.10, 0.12), Color(0.90, 0.25, 0.22), player.max_hp / 40, pulse)
	_text("%d / %d" % [player.hp, player.max_hp], hp_rect.position + Vector2(0, 12), 11, TXT, hp_rect.size.x - 6.0, HORIZONTAL_ALIGNMENT_RIGHT)
	var fp_rect := Rect2(82, 48, 190, 10)
	_bar(fp_rect, player.fp / player.max_fp, player.fp / player.max_fp, Color(0.10, 0.32, 0.65), Color(0.32, 0.62, 0.95), 0)
	_text("%d / %d" % [int(player.fp), int(player.max_fp)], fp_rect.position + Vector2(0, 9), 10, TXT, fp_rect.size.x - 6.0, HORIZONTAL_ALIGNMENT_RIGHT)

	var abilities := [
		{"key": "Q", "action": "soul_burst", "fp": 40.0, "icon": 4},
		{"key": "", "action": "focus", "fp": 0.0, "icon": 6},
		{"key": "E", "action": "skill", "fp": 20.0, "icon": 3}
	]
	for i in abilities.size():
		var ab: Dictionary = abilities[i]
		var ab_pos := Vector2(82 + i * 36, 66)
		var ab_r := Rect2(ab_pos, Vector2(26, 26))
		_frame(ab_r)
		_icon(int(ab["icon"]), ab_pos + Vector2(13, 13))
		var akey: String = ab["action"]
		if akey in Player.CD_TIME:
			var cd := float(player.cd.get(akey, 0.0))
			var frac := cd / float(Player.CD_TIME[akey])
			if frac > 0.0:
				canvas.draw_rect(Rect2(ab_pos.x, ab_pos.y + 26.0 * (1.0 - frac), 26.0, 26.0 * frac), Color(0, 0, 0, 0.65))
				var s := "%d" % ceili(cd) if cd >= 1.0 else "%.1f" % cd
				_text(s, ab_pos + Vector2(0, 18), 11, GOLD_L, 26.0, HORIZONTAL_ALIGNMENT_CENTER)
			if float(ab["fp"]) > player.fp:
				canvas.draw_rect(ab_r, Color(0.04, 0.08, 0.28, 0.6))
			var fl: float = float(_ready_flash.get(akey, 0.0))
			if fl > 0.0:
				canvas.draw_rect(ab_r, Color(1, 1, 1, 0.5 * fl / 0.35))
		if ab["key"] != "":
			var ab_badge := Rect2(ab_pos.x + 4, ab_pos.y + 28, 18, 11)
			canvas.draw_rect(ab_badge, BG)
			canvas.draw_rect(ab_badge, GOLD, false, 1.0)
			_text(ab["key"], ab_badge.position + Vector2(0, 9), 9, GOLD_L, ab_badge.size.x, HORIZONTAL_ALIGNMENT_CENTER)


func _paint_hotbar() -> void:
	for i in HOTBAR_ITEMS.size():
		var d: Array = HOTBAR_ITEMS[i]
		var pos := Vector2(24 + i * 54, 540 - 74)
		var r := Rect2(pos, Vector2(40, 40))
		_frame(r)
		_icon(int(d[2]), pos + Vector2(20, 20))
		var is_weapon: bool = (i >= 1)
		var is_active: bool = is_weapon and (player.current_weapon_idx == (i - 1))
		if is_active:
			canvas.draw_rect(r.grow(2.0), GOLD_L, false, 2.0)
			for corner in [r.position + Vector2(-2, -2), Vector2(r.end.x + 2, r.position.y - 2), Vector2(r.position.x - 2, r.end.y + 2), r.end + Vector2(2, 2)]:
				_stud(corner, 3.5, GOLD_L)
		elif int(d[2]) == 5:
			_text(str(player.flasks), pos + Vector2(24, 38), 12, GOLD_L, 16.0, HORIZONTAL_ALIGNMENT_RIGHT)
			if player.flasks == 0 or player.hp >= player.max_hp:
				canvas.draw_rect(r, Color(0, 0, 0, 0.45))
		var badge := Rect2(pos.x + 10, pos.y + 43, 20, 11)
		canvas.draw_rect(badge, BG)
		canvas.draw_rect(badge, GOLD_L if is_active else GOLD, false, 1.0)
		_text(str(d[0]), Vector2(badge.position.x, badge.position.y + 9), 9, GOLD_L, badge.size.x, HORIZONTAL_ALIGNMENT_CENTER)


func _icon(kind: int, c: Vector2) -> void:
	match kind:
		0: # Rookfang Longsword
			canvas.draw_line(c + Vector2(-12, 12), c + Vector2(12, -12), Color(0.9, 0.92, 0.98), 2.5)
			canvas.draw_line(c + Vector2(-10, 4), c + Vector2(-4, 10), GOLD_L, 2.5)
			canvas.draw_circle(c + Vector2(-11, 11), 2.0, GOLD_L)
		1: # Oathbreaker Greatsword
			canvas.draw_line(c + Vector2(-11, 13), c + Vector2(13, -11), Color(0.85, 0.75, 0.55), 4.5)
			canvas.draw_line(c + Vector2(-10, 12), c + Vector2(12, -10), Color(0.95, 0.9, 0.8), 2.0)
			canvas.draw_line(c + Vector2(-10, 2), c + Vector2(-2, 10), GOLD, 3.5)
		2: # Dodge
			canvas.draw_circle(c + Vector2(2, -9), 4, Color(0.8, 0.82, 0.9))
			canvas.draw_line(c + Vector2(2, -5), c + Vector2(-3, 6), Color(0.8, 0.82, 0.9), 3.0)
			canvas.draw_line(c + Vector2(-13, -2), c + Vector2(-5, -2), Color(0.5, 0.6, 0.8), 2.0)
			canvas.draw_line(c + Vector2(-3, 6), c + Vector2(5, 13), Color(0.8, 0.82, 0.9), 3.0)
		3: # Skill (radiant ruby star diamond)
			canvas.draw_colored_polygon(PackedVector2Array([c + Vector2(0, -11), c + Vector2(8, 0), c + Vector2(0, 11), c + Vector2(-8, 0)]), Color(0.95, 0.22, 0.32))
			canvas.draw_line(c + Vector2(0, -11), c + Vector2(0, 11), Color(1, 0.8, 0.8), 1.0)
			canvas.draw_line(c + Vector2(-8, 0), c + Vector2(8, 0), Color(1, 0.8, 0.8), 1.0)
		4: # Soul burst (fiery radiant cross flare)
			for a in 4:
				canvas.draw_line(c, c + Vector2(11, 0).rotated(a * PI / 2.0), Color(1.0, 0.65, 0.2), 2.5)
			canvas.draw_circle(c, 4, Color(1.0, 0.95, 0.7))
		5: # Flask (curved vial with elixir)
			var empty := player.flasks == 0
			canvas.draw_circle(c + Vector2(0, 4), 9, Color(0.35, 0.35, 0.38) if empty else Color(0.85, 0.12, 0.18))
			canvas.draw_circle(c + Vector2(-3, 1), 2.5, Color(1, 0.7, 0.7, 0.85))
			canvas.draw_rect(Rect2(c + Vector2(-3, -10), Vector2(6, 7)), Color(0.75, 0.8, 0.9))
			canvas.draw_rect(Rect2(c + Vector2(-4, -13), Vector2(8, 3)), GOLD)
		6: # Focus orb (mystic blue energy orb)
			canvas.draw_circle(c, 8, Color(0.12, 0.35, 0.75))
			canvas.draw_circle(c + Vector2(-2, -2), 3, Color(0.45, 0.75, 1.0))
			canvas.draw_arc(c, 10, 0, TAU, 24, Color(0.3, 0.65, 0.95, 0.7), 1.2)
		7: # Gravetide Twinblades
			canvas.draw_line(c + Vector2(-11, -8), c + Vector2(7, 10), Color(0.45, 0.88, 0.85), 2.5)
			canvas.draw_line(c + Vector2(11, -8), c + Vector2(-7, 10), Color(0.45, 0.88, 0.85), 2.5)
			canvas.draw_circle(c + Vector2(-9, -9), 1.5, GOLD_L)
			canvas.draw_circle(c + Vector2(9, -9), 1.5, GOLD_L)
		_:
			canvas.draw_circle(c, 5, GOLD)

func _paint_souls() -> void:
	var p := Vector2(792, 504)
	_frame(Rect2(p, Vector2(148, 26)))
	var f := 1.0 + 0.08 * sin(_t * 12.0)
	var fc := p + Vector2(18, 13)
	canvas.draw_colored_polygon(PackedVector2Array([fc + Vector2(0, -9) * f, fc + Vector2(7, 3), fc + Vector2(0, 9), fc + Vector2(-7, 3)]), Color(1.0, 0.62, 0.2))
	canvas.draw_colored_polygon(PackedVector2Array([fc + Vector2(0, -3) * f, fc + Vector2(3.5, 3), fc + Vector2(0, 6), fc + Vector2(-3.5, 3)]), Color(1.0, 0.9, 0.55))
	_text("%04d" % int(_souls_shown), p + Vector2(34, 20), 19, Color(0.95, 0.88, 0.7), 104.0, HORIZONTAL_ALIGNMENT_RIGHT)
	for pop in _popups:
		var t: float = pop["t"]
		_text(str(pop["text"]), p + Vector2(34, -4 - t * 26.0), 14, Color(1.0, 0.85, 0.45, 1.0 - t / 1.2), 104.0, HORIZONTAL_ALIGNMENT_RIGHT)


func _paint_minimap() -> void:
	var r := Rect2(796, 22, 148, 66)
	_frame(r)
	_text(room.region_name if room and room.region_name != "" else area_name, Vector2(r.position.x, r.end.y + 14), 11, TXT, r.size.x, HORIZONTAL_ALIGNMENT_RIGHT)
	var sx := (r.size.x - 8.0) / (Room.LEVEL_RIGHT - Room.LEVEL_LEFT)
	var map := func(wx: float, wy: float) -> Vector2:
		return Vector2(r.position.x + 4.0 + (wx - Room.LEVEL_LEFT) * sx, r.position.y + 8.0 + (wy - 250.0) * 0.26)
	for c in _explored:
		var a: Vector2 = map.call(Room.LEVEL_LEFT + c * CELL, Room.FLOOR_Y)
		canvas.draw_rect(Rect2(a, Vector2(CELL * sx + 0.5, 4)), Color(0.28, 0.36, 0.55))
	for pl in Room.PLATFORMS:
		if _explored.has(int((pl[0] + pl[2] * 16.0 - Room.LEVEL_LEFT) / CELL)):
			var a: Vector2 = map.call(pl[0], pl[1])
			canvas.draw_rect(Rect2(a, Vector2(pl[2] * Room.TILE * sx, 3)), Color(0.35, 0.45, 0.68))
	for tx in Room.TORCH_X:
		if _explored.has(int((tx - Room.LEVEL_LEFT) / CELL)):
			var t: Vector2 = map.call(float(tx), Room.FLOOR_Y - 8.0)
			canvas.draw_rect(Rect2(t, Vector2(2, 2)), Color(1.0, 0.6, 0.2))
	var pp: Vector2 = map.call(player.global_position.x, player.global_position.y - 10.0)
	canvas.draw_circle(pp, 3.0 + 0.8 * sin(_t * 6.0), Color(1, 0.9, 0.6, 0.45))
	canvas.draw_circle(pp, 2.0, Color(1, 1, 1))
	_text("%d%%" % int(_explored.size() * 100.0 / TOTAL_CELLS), Vector2(r.end.x - 34, r.end.y - 3), 10, GOLD_L, 30.0, HORIZONTAL_ALIGNMENT_RIGHT)


func _paint_pause() -> void:
	var sz := canvas.size
	canvas.draw_rect(Rect2(Vector2.ZERO, sz), Color(0, 0, 0, 0.62))
	var r := Rect2(sz.x / 2.0 - 190.0, 110, 380, 320)
	_frame(r)
	_text("PAUSED", Vector2(r.position.x, 168), 30, GOLD_L, r.size.x, HORIZONTAL_ALIGNMENT_CENTER)
	canvas.draw_line(Vector2(r.position.x + 40, 180), Vector2(r.end.x - 40, 180), GOLD, 1.0)
	var lines := [["Esc", "Resume"], ["Enter", "Restart"], ["A / D", "Move"], ["Space", "Jump (double jump in air)"], ["Shift", "Dodge roll"],
		["J / LMB", "Attack / combo"], ["K / RMB", "Heavy attack"], ["1 / 2 / 3", "Switch weapons (Rookfang / Gravetide / Oathbreaker)"],
		["E", "Weapon Skill (20 FP)"], ["Q", "Soul Burst (40 FP)"], ["R", "Healing flask"]]
	for i in lines.size():
		var y := 210.0 + i * 20.0
		_text(str(lines[i][0]), Vector2(r.position.x + 36, y), 13, GOLD_L)
		_text(str(lines[i][1]), Vector2(r.position.x + 140, y), 13, TXT)
