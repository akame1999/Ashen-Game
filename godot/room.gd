class_name Room
extends Node2D
## Builds the first room in code: parallax layers, stone floor, one-way platforms,
## torches with flickering light, banners, statue, ladder and chains.

const FLOOR_Y := 420.0
const TILE := 32
const T_STONE := 0
const T_DARK := 1
const T_MOSS := 2
const PARALLAX_HEIGHT := 540.0
const LEVEL_LEFT := -600.0
const LEVEL_RIGHT := 2400.0
const REGIONS := [ # area name, backdrop file (Ashen Veil asset pack), ambient CanvasModulate tint, stone tint, rim light
	{"name": "The Drowned March", "bg": "01_drowned_march.jpg", "tint": Color(0.72, 0.78, 0.95), "stone": Color(0.78, 0.84, 1.0), "rim": Color(0.55, 0.70, 1.0)},
	{"name": "Ashen Chapel", "bg": "02_ashen_chapel.jpg", "tint": Color(0.95, 0.80, 0.82), "stone": Color(1.0, 0.82, 0.85), "rim": Color(1.0, 0.45, 0.35)},
	{"name": "Cinder Bastion", "bg": "03_cinder_bastion.jpg", "tint": Color(1.0, 0.82, 0.72), "stone": Color(1.0, 0.75, 0.60), "rim": Color(1.0, 0.55, 0.15)},
	{"name": "The Veiled Throne", "bg": "04_veiled_throne.jpg", "tint": Color(0.84, 0.78, 1.0), "stone": Color(0.82, 0.76, 1.0), "rim": Color(0.78, 0.55, 1.0)}]
static var current_region := 0 ## survives scene reloads; F1-F4 switch region
const PARALLAX := [ # file, horizontal scroll scale, z_index, alpha (region backdrop is prepended; placeholder mid layers removed, painted art has its own depth)
	["4_foreground.png", 1.25, 10, 0.85]]
const PLATFORMS := [[560, 350, 6], [820, 290, 5], [1100, 350, 6], [1400, 300, 5], [1700, 360, 5]]
const TORCH_X := [200, 480, 760, 1040, 1320, 1600, 1880]
const ENEMIES := [["skeleton", 690, 420, 90], ["shield_skeleton", 1000, 420, 90], ["skeleton", 1250, 420, 90],
		["archer", 1480, 300, 60], ["armored_knight", 1900, 420, 80]]

var torch_count := 0
var enemy_count := 0
var platform_count := 0
var parallax_count := 0
var region_name := ""
var _stone := Color.WHITE
var _rim := Color(1, 1, 1)
var _lights: Array[PointLight2D] = []
var _tileset: Texture2D
var _light_tex: GradientTexture2D
var _time := 0.0


func _ready() -> void:
	_tileset = load("res://assets/tiles/tileset.png")
	_light_tex = _make_light_texture()
	var mod := CanvasModulate.new()
	var region: Dictionary = REGIONS[clampi(current_region, 0, REGIONS.size() - 1)]
	region_name = region["name"]
	mod.color = region["tint"]
	_stone = region["stone"]
	_rim = region["rim"]
	add_child(mod)
	_build_parallax()
	_build_props()
	_build_floor()
	for p in PLATFORMS:
		_build_platform(p[0], p[1], p[2])
	_build_torches()
	_spawn_enemies()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var idx: int = int(event.keycode) - int(KEY_F1)
		if idx >= 0 and idx < REGIONS.size() and idx != current_region:
			current_region = idx
			get_tree().reload_current_scene()


func _process(delta: float) -> void:
	_time += delta
	for i in _lights.size():
		var l := _lights[i]
		l.energy = 1.0 + sin(_time * 9.0 + i * 1.7) * 0.1 + sin(_time * 23.0 + i) * 0.05


func _make_light_texture() -> GradientTexture2D:
	var g := Gradient.new()
	g.colors = PackedColorArray([Color(1, 1, 1, 1), Color(1, 1, 1, 0)])
	g.offsets = PackedFloat32Array([0.0, 1.0])
	var t := GradientTexture2D.new()
	t.gradient = g
	t.width = 256
	t.height = 256
	t.fill = GradientTexture2D.FILL_RADIAL
	t.fill_from = Vector2(0.5, 0.5)
	t.fill_to = Vector2(1.0, 0.5)
	return t


func _build_parallax() -> void:
	## Any layer size works: each PNG is scaled to PARALLAX_HEIGHT tall and repeated horizontally.
	var layers: Array = [[REGIONS[clampi(current_region, 0, REGIONS.size() - 1)]["bg"], 0.04, -8, 1.0]]
	layers.append_array(PARALLAX)
	for layer in layers:
		var fn: String = layer[0]
		var path := "res://assets/parallax/%s" % fn if (fn.ends_with(".jpg") or fn.ends_with(".png")) else ("res://assets/parallax/%s.png" % fn)
		var tex: Texture2D = load(path)
		var sc := PARALLAX_HEIGHT / float(tex.get_height())
		var w := tex.get_width() * sc
		var px := Parallax2D.new()
		px.scroll_scale = Vector2(layer[1], 1.0)
		px.repeat_size = Vector2(w, 0)
		px.repeat_times = 6
		px.z_index = layer[2]
		var s := Sprite2D.new()
		s.texture = tex
		s.centered = false
		s.scale = Vector2(sc, sc)
		s.position = Vector2(-w, -10)
		if layer.size() > 3:
			s.modulate.a = float(layer[3])
		px.add_child(s)
		add_child(px)
		parallax_count += 1


func _tile(idx: int, pos: Vector2, parent: Node) -> void:
	var s := Sprite2D.new()
	s.texture = _tileset
	s.region_enabled = true
	s.region_rect = Rect2(idx * TILE, 0, TILE, TILE)
	s.centered = false
	s.position = pos
	s.modulate = _stone
	parent.add_child(s)


func _edge(parent: Node, x: float, y: float, w: float, shadow_h: float) -> void:
	## Region-coloured rim light on the walking surface plus a soft shadow beneath it.
	var glow := ColorRect.new()
	glow.color = Color(_rim, 0.22)
	glow.position = Vector2(x, y - 4)
	glow.size = Vector2(w, 6)
	glow.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(glow)
	var rim := ColorRect.new()
	rim.color = Color(_rim, 0.85)
	rim.position = Vector2(x, y)
	rim.size = Vector2(w, 2)
	rim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(rim)
	var sh := ColorRect.new()
	sh.color = Color(0, 0, 0, 0.4)
	sh.position = Vector2(x, y + TILE * (2 if shadow_h > 20.0 else 1) - 2)
	sh.size = Vector2(w, shadow_h)
	sh.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(sh)


func _box(parent: Node, rect: Rect2, one_way := false) -> void:
	var cs := CollisionShape2D.new()
	var rs := RectangleShape2D.new()
	rs.size = rect.size
	cs.shape = rs
	cs.position = rect.position + rect.size / 2.0
	cs.one_way_collision = one_way
	parent.add_child(cs)


func _build_floor() -> void:
	var body := StaticBody2D.new()
	body.name = "Floor"
	add_child(body)
	_box(body, Rect2(LEVEL_LEFT, FLOOR_Y, LEVEL_RIGHT - LEVEL_LEFT, 120))
	var x := LEVEL_LEFT
	while x < LEVEL_RIGHT:
		_tile(T_MOSS, Vector2(x, FLOOR_Y), body)
		_tile(T_STONE, Vector2(x, FLOOR_Y + TILE), body)
		_tile(T_DARK, Vector2(x, FLOOR_Y + TILE * 2), body)
		x += TILE
	_edge(body, LEVEL_LEFT, FLOOR_Y, LEVEL_RIGHT - LEVEL_LEFT, 28.0)


func _build_platform(x: float, y: float, tiles: int) -> void:
	var body := StaticBody2D.new()
	add_child(body)
	_box(body, Rect2(x, y, tiles * TILE, 12), true)
	for i in tiles:
		_tile(T_MOSS, Vector2(x + i * TILE, y), body)
		_tile(T_DARK, Vector2(x + i * TILE, y + TILE), body)
	_edge(body, x, y, tiles * TILE, 10.0)
	platform_count += 1
	var chain := load("res://assets/props/chain.png")
	var links := mini(2, int((FLOOR_Y - (y + TILE * 2)) / 32.0))
	for k in links:
		var c := Sprite2D.new()
		c.texture = chain
		c.centered = false
		c.position = Vector2(x + tiles * TILE * 0.5, y + TILE * 2 + k * 32)
		add_child(c)


func _frames(path: String, fw: int, fh: int, n: int, fps: float) -> SpriteFrames:
	var tex: Texture2D = load(path)
	var fs := SpriteFrames.new()
	fs.set_animation_speed("default", fps)
	for i in n:
		var at := AtlasTexture.new()
		at.atlas = tex
		at.region = Rect2(i * fw, 0, fw, fh)
		fs.add_frame("default", at)
	return fs


func _anim(path: String, fw: int, fh: int, n: int, fps: float, pos: Vector2) -> AnimatedSprite2D:
	var a := AnimatedSprite2D.new()
	a.sprite_frames = _frames(path, fw, fh, n, fps)
	a.centered = false
	a.position = pos
	a.play("default")
	add_child(a)
	return a


func _build_props() -> void:
	var statue := Sprite2D.new()
	statue.texture = load("res://assets/props/statue_hooded.png")
	statue.centered = false
	statue.position = Vector2(388, FLOOR_Y - 112)
	add_child(statue)
	for bx in [300, 700, 1260, 1560]:
		_anim("res://assets/props/banner.png", 48, 96, 4, 4.0, Vector2(bx, FLOOR_Y - 150))
	var ladder := load("res://assets/props/ladder.png")
	for k in 3:
		var l := Sprite2D.new()
		l.texture = ladder
		l.centered = false
		l.position = Vector2(525, 350 + k * 32)
		add_child(l)


func _build_torches() -> void:
	for x in TORCH_X:
		_anim("res://assets/props/torch.png", 32, 48, 4, 8.0, Vector2(x - 16, FLOOR_Y - 48))
		var light := PointLight2D.new()
		light.texture = _light_tex
		light.color = Color(1.0, 0.62, 0.28)
		light.energy = 1.0
		light.texture_scale = 2.2
		light.position = Vector2(x, FLOOR_Y - 34)
		add_child(light)
		_lights.append(light)
		torch_count += 1


func _spawn_enemies() -> void:
	for d in ENEMIES:
		var e := Enemy.new()
		e.kind = d[0]
		e.position = Vector2(d[1], d[2])
		e.patrol_range = d[3]
		add_child(e)
		enemy_count += 1
