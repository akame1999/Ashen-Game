class_name Player
extends CharacterBody2D
## Side-scrolling player: run, jump, dodge, light combo, heavy, skill, hurt, death.
## Animations are built at runtime from assets/characters/player.png + player.json.

enum State { NORMAL, DODGE, ATTACK, HURT, DEAD }

const SPEED := 150.0
const JUMP_V := -330.0
const GRAVITY := 900.0
const DODGE_SPEED := 260.0
const DODGE_TIME := 0.3
const SKINS := [ # F6 cycles; Ashen Veil asset-pack combat bodies (no sword baked in) are the default
	{"name": "Male", "sheet": "res://assets/characters/player_male.png", "meta": "res://assets/characters/player_male.json", "hand": Vector2(34, -69)},
	{"name": "Female", "sheet": "res://assets/characters/player_female.png", "meta": "res://assets/characters/player_female.json", "hand": Vector2(36, -68)},
	{"name": "Ashen Knight", "sheet": "res://assets/characters/player.png", "meta": "res://assets/characters/player.json"}]
static var skin := 0 ## survives scene reloads; F6 cycles skins
const FPS := {"idle": 6.0, "run": 16.0, "jump": 8.0, "fall": 8.0, "dodge": 20.0, "light1": 14.0,
		"light2": 14.0, "heavy": 10.0, "skill": 12.0, "hurt": 8.0, "death": 8.0}
const LOOPS := ["idle", "run", "fall"]
const HIT_FRAME := {"light1": 2, "light2": 2, "heavy": 3, "skill": 2}
const DAMAGE := {"light1": 25, "light2": 28, "heavy": 60, "skill": 45}
const REACH := {"light1": 46.0, "light2": 46.0, "heavy": 58.0, "skill": 78.0}
const FX := {"light1": "slash_light", "light2": "slash_light", "heavy": "slash_heavy", "skill": "slash_skill"}
const FX_FRAMES := {"slash_light": 6, "slash_heavy": 7, "slash_skill": 7}

var state: State = State.NORMAL
var facing := 1
var invulnerable := false
var sprite: AnimatedSprite2D
var attack_name := ""
var combo_queued := false
var dodge_time := 0.0
var _frame_size := 96
var _node_scale := 1.0
var _cx := 44.0 # character's x centre inside a frame (from player.json)
var iframes := 0.0
var cd := {}
var flasks := 3
var max_flasks := 3
var _hit_done := false
var max_hp := 320
var hp := 320
var max_fp := 120.0
var fp := 120.0
var level := 1
var souls := 27
var jumps_left := 2
var weapon_pivot: Node2D
var weapon_sprite: Sprite2D
var weapon_info := {} # runtime manifest entry of the drawn weapon
var _weapons := {} # manifest id -> entry
var _equipped_idx := -1
var _hand := Vector2.ZERO # hand socket at pack scale; ZERO = skin has its own sword
const MAX_JUMPS := 2
var current_weapon_idx := 0
const WEAPONS := ["Rookfang", "Gravetide", "Oathbreaker", "Ashen Katana", "Void Daggers", "Veilpiercer", "Cinder Greataxe", "Frost Halberd", "Ghostwood Bow", "Soulfire Staff", "Blackthorn Shield", "Nightfall Scythe"]
const WEAPON_DATA := [ # damage x, reach x, slash FX image
	{"dmg": 1.0, "reach": 1.0, "fx": "slash_crimson"},
	{"dmg": 0.85, "reach": 0.95, "fx": "slash_frost"},
	{"dmg": 1.5, "reach": 1.2, "fx": "slash_holy"},
	{"dmg": 1.09, "reach": 1.16, "fx": "slash_frost"}, # Ashen Katana
	{"dmg": 0.73, "reach": 0.82, "fx": "slash_crimson"}, # Void Daggers
	{"dmg": 1.09, "reach": 1.47, "fx": "slash_holy"}, # Veilpiercer spear
	{"dmg": 1.27, "reach": 1.25, "fx": "slash_crimson"}, # Cinder Greataxe
	{"dmg": 1.09, "reach": 1.42, "fx": "slash_frost"}, # Frost Halberd
	{"dmg": 0.91, "reach": 1.6, "fx": "slash_holy"}, # Ghostwood Bow (ranged, melee-approximated for now)
	{"dmg": 0.82, "reach": 1.6, "fx": "slash_holy"}, # Soulfire Staff (ranged, melee-approximated for now)
	{"dmg": 0.45, "reach": 0.74, "fx": "slash_crimson"}, # Blackthorn Shield
	{"dmg": 1.18, "reach": 1.32, "fx": "slash_frost"}] # Nightfall Scythe
const KIT_FX := "res://assets/fx/kit/%s.png"
const WEAPON_MANIFEST := "res://assets/weapons/runtime_manifest.json"
const WEAPON_IDS := ["01_rookfang_longsword", "04_gravetide_twinblades", "02_oathbreaker_greatsword",
	"03_ashen_katana", "05_void_dagger_pair", "06_veilpiercer_spear", "07_cinder_greataxe", "08_frost_halberd", "09_ghostwood_bow",
	"10_soulfire_rune_staff", "11_blackthorn_shield", "12_nightfall_scythe"] # keys 1-9, 0, -, =
const SWING_KEY := {"light1": "swing_light", "light2": "swing_light", "heavy": "swing_heavy", "skill": "swing_skill", "soul_burst": "swing_skill"}
const SKILL_COST := 20.0
const SOUL_COST := 40.0
const FLASK_HEAL := 110
const SOUL_RADIUS := 110.0
const SOUL_DAMAGE := 70
const CD_TIME := {"heavy": 1.2, "dodge": 0.8, "skill": 2.0, "soul_burst": 4.0}
const FP_REGEN := 4.0


func _ready() -> void:
	add_to_group("player")
	_setup_input()
	_build_sprite()
	_build_weapon()
	sprite.animation_finished.connect(_on_anim_finished)
	sprite.play("idle")


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F6:
		skin = (skin + 1) % SKINS.size()
		get_tree().reload_current_scene()


func _setup_input() -> void:
	var keys := {"move_left": [KEY_A, KEY_LEFT], "move_right": [KEY_D, KEY_RIGHT],
			"jump": [KEY_SPACE, KEY_W, KEY_UP], "dodge": [KEY_SHIFT], "attack": [KEY_J],
			"heavy": [KEY_K], "skill": [KEY_E], "soul_burst": [KEY_Q], "flask": [KEY_R], "weapon_1": [KEY_1, KEY_KP_1], "weapon_2": [KEY_2, KEY_KP_2], "weapon_3": [KEY_3, KEY_KP_3],
			"weapon_4": [KEY_4], "weapon_5": [KEY_5], "weapon_6": [KEY_6], "weapon_7": [KEY_7], "weapon_8": [KEY_8], "weapon_9": [KEY_9],
			"weapon_10": [KEY_0], "weapon_11": [KEY_MINUS], "weapon_12": [KEY_EQUAL]}
	for a in keys:
		if not InputMap.has_action(a):
			InputMap.add_action(a)
		for k in keys[a]:
			var ev := InputEventKey.new()
			ev.physical_keycode = k
			InputMap.action_add_event(a, ev)
	for pair in [["attack", MOUSE_BUTTON_LEFT], ["heavy", MOUSE_BUTTON_RIGHT]]:
		var mb := InputEventMouseButton.new()
		mb.button_index = pair[1]
		InputMap.action_add_event(pair[0], mb)


func _build_sprite() -> void:
	var sk: Dictionary = SKINS[clampi(skin, 0, SKINS.size() - 1)]
	var meta: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(sk["meta"]))
	var tex: Texture2D = load(sk["sheet"])
	_frame_size = int(meta["frame"])
	_cx = float(meta.get("center_x", 44.0))
	_node_scale = float(meta.get("scale", 1.0))
	var fs := SpriteFrames.new()
	fs.remove_animation("default")
	for row in meta["rows"]:
		var n: String = row["name"]
		fs.add_animation(n)
		fs.set_animation_speed(n, FPS.get(n, 10.0))
		fs.set_animation_loop(n, n in LOOPS)
		for i in int(row["frames"]):
			var at := AtlasTexture.new()
			at.atlas = tex
			at.region = Rect2(i * _frame_size, int(row["row"]) * _frame_size, _frame_size, _frame_size)
			fs.add_frame(n, at)
	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = fs
	sprite.centered = false
	sprite.offset = Vector2(-_cx, -float(meta["feet_row"]))
	sprite.scale = Vector2(_node_scale, _node_scale)
	add_child(sprite)


func _build_weapon() -> void:
	var sk: Dictionary = SKINS[clampi(skin, 0, SKINS.size() - 1)]
	_hand = sk.get("hand", Vector2.ZERO)
	var man: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(WEAPON_MANIFEST))
	for w in man["weapons"]:
		_weapons[w["id"]] = w
	weapon_pivot = Node2D.new()
	weapon_pivot.z_index = 2
	weapon_sprite = Sprite2D.new()
	weapon_sprite.centered = false
	weapon_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	weapon_pivot.add_child(weapon_sprite)
	add_child(weapon_pivot)
	weapon_pivot.visible = _hand != Vector2.ZERO


func _equip_weapon(idx: int) -> void:
	_equipped_idx = idx
	weapon_info = _weapons.get(WEAPON_IDS[clampi(idx, 0, WEAPON_IDS.size() - 1)], {})
	if weapon_info.is_empty():
		return
	var anchor := Vector2(float(weapon_info["grip_anchor"][0]), float(weapon_info["grip_anchor"][1]))
	var sc := float(weapon_info["scale"])
	weapon_sprite.texture = load(weapon_info["texture"])
	weapon_sprite.scale = Vector2(sc, sc)
	weapon_sprite.position = -anchor * sc # grip sits on the pivot (the hand)


func _update_weapon() -> void:
	if _hand == Vector2.ZERO:
		return
	weapon_pivot.visible = state != State.DEAD
	if _equipped_idx != current_weapon_idx:
		_equip_weapon(current_weapon_idx)
	# mirror via scale.x like the asset pack does; whole rig is shrunk by the sprite scale
	weapon_pivot.scale = Vector2(facing * _node_scale, _node_scale)
	var pos := _hand
	var rot := 0.0
	if state == State.ATTACK and SWING_KEY.has(attack_name) and not weapon_info.is_empty():
		var n := maxi(1, sprite.sprite_frames.get_frame_count(sprite.animation))
		var p := clampf((float(sprite.frame) + sprite.frame_progress) / float(n), 0.0, 1.0)
		var ang: Array = weapon_info.get(SWING_KEY[attack_name], [-1.1, 0.8])
		rot = lerpf(float(ang[0]), float(ang[1]), p)
		pos += Vector2(sin(p * PI) * 7.0, -sin(p * PI) * 4.0)
	weapon_pivot.position = Vector2(facing * pos.x, pos.y) * _node_scale
	weapon_pivot.rotation = rot


func _physics_process(delta: float) -> void:
	iframes = maxf(0.0, iframes - delta)
	for k in cd:
		cd[k] = maxf(0.0, float(cd[k]) - delta)
	fp = minf(max_fp, fp + FP_REGEN * delta)
	if not is_on_floor():
		velocity.y += GRAVITY * delta
	else:
		jumps_left = MAX_JUMPS
	if state == State.DEAD:
		velocity.x = move_toward(velocity.x, 0.0, 600.0 * delta)
		move_and_slide()
		return
	var dir := Input.get_axis("move_left", "move_right")
	match state:
		State.NORMAL:
			velocity.x = dir * SPEED
			if dir != 0.0:
				facing = 1 if dir > 0.0 else -1
			if Input.is_action_just_pressed("jump"):
				if is_on_floor():
					velocity.y = JUMP_V
					jumps_left = MAX_JUMPS - 1
				elif jumps_left > 0:
					velocity.y = JUMP_V * 0.95
					jumps_left -= 1
					sprite.play("jump")
					SheetUtil.spawn_fx(get_parent(), "res://assets/fx/impact_spark.png", 6, 24.0, global_position + Vector2(0, -6), Vector2(48, 48), false, false, 96, 0.45)
			for wi in WEAPON_IDS.size():
				if Input.is_action_just_pressed("weapon_%d" % (wi + 1)):
					current_weapon_idx = wi

			if Input.is_action_just_pressed("dodge") and is_on_floor() and _cd_ready("dodge"):
				_cd_start("dodge")
				_start_dodge()
			elif Input.is_action_just_pressed("attack"):
				_start_attack("light1")
			elif Input.is_action_just_pressed("heavy") and _cd_ready("heavy"):
				_cd_start("heavy")
				_start_attack("heavy")
			elif Input.is_action_just_pressed("skill") and fp >= SKILL_COST and _cd_ready("skill"):
				fp -= SKILL_COST
				_cd_start("skill")
				_start_attack("skill")
			elif Input.is_action_just_pressed("soul_burst") and fp >= SOUL_COST and _cd_ready("soul_burst"):
				fp -= SOUL_COST
				_cd_start("soul_burst")
				iframes = 0.5 # the burst can't be interrupted while it charges
				_start_attack("soul_burst")
			elif Input.is_action_just_pressed("flask") and flasks > 0 and hp < max_hp:
				_drink_flask()
			if state == State.NORMAL:
				_update_move_anim()
		State.DODGE:
			dodge_time -= delta
			velocity.x = facing * DODGE_SPEED
			if dodge_time <= 0.0:
				invulnerable = false
				state = State.NORMAL
		State.ATTACK:
			velocity.x = move_toward(velocity.x, 0.0, 900.0 * delta)
			if attack_name == "light1" and Input.is_action_just_pressed("attack"):
				combo_queued = true
			if not _hit_done and sprite.frame >= int(HIT_FRAME.get(attack_name, 2)):
				_hit_done = true
				_do_hit()
		State.HURT:
			velocity.x = move_toward(velocity.x, 0.0, 600.0 * delta)
	sprite.flip_h = facing < 0
	sprite.position.x = -(_frame_size - 2.0 * _cx) * _node_scale if facing < 0 else 0.0
	_update_weapon()
	move_and_slide()


func _update_move_anim() -> void:
	var anim := "idle"
	if not is_on_floor():
		anim = "jump" if velocity.y < 0.0 else "fall"
	elif absf(velocity.x) > 1.0:
		anim = "run"
	if sprite.animation != anim or not sprite.is_playing():
		sprite.play(anim)


func _drink_flask() -> void:
	flasks -= 1
	var healed := mini(FLASK_HEAL, max_hp - hp)
	hp += healed
	sprite.modulate = Color(0.7, 2.0, 0.9)
	create_tween().tween_property(sprite, "modulate", Color.WHITE, 0.4)
	var l := Label.new()
	l.text = "+%d" % healed
	l.add_theme_font_override("font", load("res://assets/fonts/Cinzel-Variable.ttf"))
	l.add_theme_font_size_override("font_size", 14)
	l.add_theme_color_override("font_color", Color(0.6, 1.0, 0.65))
	l.add_theme_color_override("font_outline_color", Color(0.05, 0.25, 0.1))
	l.add_theme_constant_override("outline_size", 4)
	l.z_index = 20
	l.position = global_position + Vector2(-10, -64)
	get_parent().add_child(l)
	var t := l.create_tween()
	t.tween_property(l, "position:y", l.position.y - 26.0, 0.7)
	t.parallel().tween_property(l, "modulate:a", 0.0, 0.7)
	t.tween_callback(l.queue_free)


func _cd_ready(n: String) -> bool:
	return float(cd.get(n, 0.0)) <= 0.0


func _cd_start(n: String) -> void:
	cd[n] = float(CD_TIME[n])


func _start_dodge() -> void:
	state = State.DODGE
	invulnerable = true
	dodge_time = DODGE_TIME
	SheetUtil.pop_sprite(get_parent(), KIT_FX % "dash_trail", global_position + Vector2(-facing * 26, -22), 0.2, facing < 0, false, 0.3, 1.1, 4)
	sprite.play("dodge")


func _start_attack(anim: String) -> void:
	state = State.ATTACK
	attack_name = anim
	combo_queued = false
	_hit_done = false
	velocity.x = facing * 60.0
	sprite.play("skill" if anim == "soul_burst" else anim)


func hurt(amount: int = 30) -> void:
	if invulnerable or iframes > 0.0 or state == State.DEAD:
		return
	hp = maxi(0, hp - amount)
	iframes = 0.7
	sprite.modulate = Color(2.0, 0.6, 0.6)
	create_tween().tween_property(sprite, "modulate", Color.WHITE, 0.25)
	if hp == 0:
		die()
		return
	state = State.HURT
	velocity.x = -facing * 120.0
	sprite.play("hurt")


func _soul_burst() -> void:
	var center := global_position + Vector2(0, -22)
	SheetUtil.spawn_fx(get_parent(), "res://assets/fx/soul_burst.png", 8, 18.0, center, Vector2(48, 48), false, false, 96, SOUL_RADIUS / 44.0)
	for n in get_tree().get_nodes_in_group("enemies"):
		var en := n as Enemy
		if en and en.alive and center.distance_to(en.global_position + Vector2(0, -20)) <= SOUL_RADIUS:
			en.take_damage(SOUL_DAMAGE, global_position.x)


func _do_hit() -> void:
	if attack_name == "soul_burst":
		_soul_burst()
		return
	var wd: Dictionary = WEAPON_DATA[clampi(current_weapon_idx, 0, WEAPON_DATA.size() - 1)]
	var reach: float = float(REACH.get(attack_name, 46.0)) * float(wd["reach"])
	var dmg: int = int(round(float(DAMAGE.get(attack_name, 25)) * float(wd["dmg"])))
	var box := Rect2(global_position + Vector2(4.0 if facing > 0 else -4.0 - reach, -46.0), Vector2(reach, 46.0))
	var big := 1.3 if attack_name == "heavy" or attack_name == "skill" else 1.0
	SheetUtil.pop_sprite(get_parent(), KIT_FX % wd["fx"], global_position + Vector2(facing * reach * 0.5, -26), reach * 1.7 * big / 512.0,
			facing < 0, attack_name == "light2", 0.22, 1.15)
	for n in get_tree().get_nodes_in_group("enemies"):
		var en := n as Enemy
		if en and en.alive and box.intersects(Rect2(en.global_position + Vector2(-10, -40), Vector2(20, 40))):
			en.take_damage(dmg, global_position.x)
			SheetUtil.spawn_fx(get_parent(), "res://assets/fx/impact_spark.png", 6, 24.0, en.global_position + Vector2(0, -26), Vector2(48, 48))
			SheetUtil.pop_sprite(get_parent(), KIT_FX % "impact_blood", en.global_position + Vector2(0, -24), 0.16, false, false, 0.25, 1.4, 6)


func die() -> void:
	state = State.DEAD
	if weapon_pivot:
		weapon_pivot.visible = false
	sprite.play("death")


func _on_anim_finished() -> void:
	match state:
		State.ATTACK:
			if attack_name == "light1" and combo_queued:
				_start_attack("light2")
			else:
				state = State.NORMAL
		State.HURT:
			state = State.NORMAL
