class_name Hud
extends CanvasLayer
## Dark-fantasy HUD drawn in code (960x540 space): portrait + level, HP/FP bars, hotbar, souls, minimap.

const GOLD := Color(0.69, 0.55, 0.30)
const GOLD_D := Color(0.30, 0.22, 0.10)
const BG := Color(0.04, 0.04, 0.07, 0.88)
const TXT := Color(0.88, 0.86, 0.80)
const SLOTS := [["LMB", "Attack", 0], ["RMB", "Heavy", 1], ["Shift", "Dodge", 2], ["E", "Skill", 3], ["Q", "Soul Burst", 4]]

var area_name := "Ruined Kingdom"
var player: Player
var room: Room
var font: Font
var canvas: Control


func _ready() -> void:
	layer = 10
	font = load("res://assets/fonts/Cinzel-Variable.ttf")
	canvas = Control.new()
	canvas.set_anchors_preset(Control.PRESET_FULL_RECT)
	canvas.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(canvas)
	canvas.draw.connect(_paint)
	player = get_parent().get_node("Player")
	room = get_parent().get_node("Room")


func _process(_delta: float) -> void:
	canvas.queue_redraw()


func _text(s: String, pos: Vector2, size: int, col := TXT, width := -1.0, align := HORIZONTAL_ALIGNMENT_LEFT) -> void:
	canvas.draw_string(font, pos + Vector2(1, 1), s, align, width, size, Color(0, 0, 0, 0.8))
	canvas.draw_string(font, pos, s, align, width, size, col)


func _bar(rect: Rect2, ratio: float, c_main: Color, c_light: Color) -> void:
	canvas.draw_rect(rect.grow(2.0), GOLD_D)
	canvas.draw_rect(rect, BG)
	var fill := Rect2(rect.position, Vector2(rect.size.x * clampf(ratio, 0.0, 1.0), rect.size.y))
	canvas.draw_rect(fill, c_main)
	canvas.draw_rect(Rect2(fill.position, Vector2(fill.size.x, fill.size.y * 0.4)), c_light)
	canvas.draw_rect(rect.grow(1.0), GOLD, false, 1.0)


func _paint() -> void:
	_paint_top_left()
	_paint_hotbar()
	_paint_souls()
	_paint_minimap()


func _paint_top_left() -> void:
	var c := Vector2(38, 38)
	canvas.draw_circle(c, 27, GOLD_D)
	canvas.draw_arc(c, 26, 0, TAU, 40, GOLD, 2.0)
	canvas.draw_circle(c, 23, BG)
	canvas.draw_circle(c + Vector2(0, -2), 11, Color(0.18, 0.18, 0.24))                  # hood
	canvas.draw_circle(c + Vector2(1, -1), 7, Color(0.80, 0.69, 0.61))                   # face
	canvas.draw_colored_polygon(PackedVector2Array([c + Vector2(-8, 4), c + Vector2(8, 4), c + Vector2(12, 16), c + Vector2(-12, 16)]), Color(0.45, 0.10, 0.14))
	canvas.draw_circle(c + Vector2(20, 20), 10, GOLD_D)
	canvas.draw_circle(c + Vector2(20, 20), 8, BG)
	canvas.draw_arc(c + Vector2(20, 20), 9, 0, TAU, 24, GOLD, 1.0)
	_text(str(player.level), c + Vector2(15, 25), 13, TXT, 10.0, HORIZONTAL_ALIGNMENT_CENTER)
	_text("Ashen Veil", Vector2(76, 16), 15, TXT)
	var hp_rect := Rect2(76, 24, 250, 13)
	_bar(hp_rect, float(player.hp) / player.max_hp, Color(0.62, 0.10, 0.12), Color(0.85, 0.22, 0.2))
	_text("%d / %d" % [player.hp, player.max_hp], hp_rect.position + Vector2(0, 11), 11, TXT, hp_rect.size.x - 6.0, HORIZONTAL_ALIGNMENT_RIGHT)
	var fp_rect := Rect2(76, 44, 200, 10)
	_bar(fp_rect, player.fp / player.max_fp, Color(0.10, 0.32, 0.65), Color(0.30, 0.60, 0.92))
	_text("%d / %d" % [int(player.fp), int(player.max_fp)], fp_rect.position + Vector2(0, 9), 10, TXT, fp_rect.size.x - 6.0, HORIZONTAL_ALIGNMENT_RIGHT)


func _paint_hotbar() -> void:
	for i in SLOTS.size():
		var pos := Vector2(20 + i * 56, 540 - 74)
		var r := Rect2(pos, Vector2(38, 38))
		canvas.draw_rect(r.grow(2.0), GOLD_D)
		canvas.draw_rect(r, BG)
		canvas.draw_rect(r.grow(1.0), GOLD, false, 1.0)
		_icon(SLOTS[i][2], pos + Vector2(19, 19))
		_text(SLOTS[i][0], pos + Vector2(-16, 52), 10, GOLD, 70.0, HORIZONTAL_ALIGNMENT_CENTER)
		_text(SLOTS[i][1], pos + Vector2(-16, 63), 10, TXT, 70.0, HORIZONTAL_ALIGNMENT_CENTER)


func _icon(kind: int, c: Vector2) -> void:
	match kind:
		0:
			canvas.draw_line(c + Vector2(-10, 11), c + Vector2(10, -11), Color(0.85, 0.88, 0.95), 3.0)
			canvas.draw_line(c + Vector2(-9, 3), c + Vector2(-3, 9), GOLD, 3.0)
		1:
			canvas.draw_arc(c + Vector2(-2, 2), 11, -2.4, 0.5, 18, Color(0.35, 0.65, 0.95), 4.0)
		2:
			canvas.draw_circle(c + Vector2(2, -8), 4, Color(0.8, 0.82, 0.9))
			canvas.draw_line(c + Vector2(2, -4), c + Vector2(-3, 6), Color(0.8, 0.82, 0.9), 3.0)
			canvas.draw_line(c + Vector2(-12, -2), c + Vector2(-5, -2), Color(0.5, 0.6, 0.8), 2.0)
			canvas.draw_line(c + Vector2(-3, 6), c + Vector2(5, 12), Color(0.8, 0.82, 0.9), 3.0)
		3:
			canvas.draw_colored_polygon(PackedVector2Array([c + Vector2(0, -12), c + Vector2(9, 0), c + Vector2(0, 12), c + Vector2(-9, 0)]), Color(0.85, 0.2, 0.3))
			canvas.draw_line(c + Vector2(0, -12), c + Vector2(0, 12), Color(1, 0.7, 0.7), 1.0)
		_:
			for a in 4:
				canvas.draw_line(c, c + Vector2(13, 0).rotated(a * PI / 2.0), Color(1.0, 0.82, 0.35), 3.0)
			canvas.draw_circle(c, 5, Color(1.0, 0.95, 0.7))


func _paint_souls() -> void:
	var p := Vector2(800, 512)
	canvas.draw_rect(Rect2(p, Vector2(140, 26)).grow(2.0), GOLD_D)
	canvas.draw_rect(Rect2(p, Vector2(140, 26)), BG)
	canvas.draw_rect(Rect2(p, Vector2(140, 26)).grow(1.0), GOLD, false, 1.0)
	canvas.draw_colored_polygon(PackedVector2Array([p + Vector2(16, 5), p + Vector2(23, 18), p + Vector2(16, 22), p + Vector2(9, 18)]), Color(1.0, 0.7, 0.25))
	_text("%04d" % player.souls, p + Vector2(34, 20), 19, Color(0.95, 0.88, 0.7), 98.0, HORIZONTAL_ALIGNMENT_RIGHT)


func _paint_minimap() -> void:
	_text(area_name, Vector2(792, 20), 14, TXT, 156.0, HORIZONTAL_ALIGNMENT_CENTER)
	var r := Rect2(796, 28, 148, 66)
	canvas.draw_rect(r.grow(2.0), GOLD_D)
	canvas.draw_rect(r, BG)
	var sx := (r.size.x - 8.0) / (Room.LEVEL_RIGHT - Room.LEVEL_LEFT)
	var map := func(wx: float, wy: float) -> Vector2:
		return Vector2(r.position.x + 4.0 + (wx - Room.LEVEL_LEFT) * sx, r.position.y + 8.0 + (wy - 250.0) * 0.26)
	var floor_pos: Vector2 = map.call(Room.LEVEL_LEFT, Room.FLOOR_Y)
	canvas.draw_rect(Rect2(floor_pos, Vector2(r.size.x - 8.0, 4)), Color(0.28, 0.36, 0.55))
	for pl in Room.PLATFORMS:
		var a: Vector2 = map.call(pl[0], pl[1])
		canvas.draw_rect(Rect2(a, Vector2(pl[2] * Room.TILE * sx, 3)), Color(0.35, 0.45, 0.68))
	for tx in Room.TORCH_X:
		var t: Vector2 = map.call(tx, Room.FLOOR_Y - 8)
		canvas.draw_rect(Rect2(t, Vector2(2, 2)), Color(1.0, 0.6, 0.2))
	var pp: Vector2 = map.call(player.global_position.x, player.global_position.y - 10)
	canvas.draw_circle(pp, 2.5, Color(1, 1, 1))
	canvas.draw_rect(r.grow(1.0), GOLD, false, 1.0)
	_text("3%", Vector2(r.end.x - 24, r.end.y - 3), 10, GOLD, 22.0, HORIZONTAL_ALIGNMENT_RIGHT)
