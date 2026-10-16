class_name Enemy
extends CharacterBody2D
## Generic enemy: patrol -> chase -> attack, with hurt/death. Behaviour comes from CONFIGS.

enum State { PATROL, CHASE, ATTACK, HURT, DEAD }

const GRAVITY := 900.0
const CENTER_X := 44.0
const FPS := {"idle": 6.0, "walk": 8.0, "attack": 10.0, "hurt": 8.0, "death": 8.0}
const LOOPS := ["idle", "walk"]
const CONFIGS := {
	"skeleton": {"hp": 60, "speed": 42.0, "range": 58.0, "hit_frame": 3, "damage": 20, "souls": 12, "cooldown": 1.3, "aggro": 230.0},
	"shield_skeleton": {"hp": 90, "speed": 36.0, "range": 42.0, "hit_frame": 4, "damage": 25, "souls": 18, "cooldown": 1.5, "aggro": 220.0, "block": true},
	"archer": {"hp": 45, "speed": 32.0, "range": 300.0, "hit_frame": 4, "damage": 18, "souls": 15, "cooldown": 2.2, "aggro": 330.0, "ranged": true, "keep": 150.0, "leash": true},
	"armored_knight": {"hp": 220, "speed": 30.0, "range": 68.0, "hit_frame": 4, "damage": 45, "souls": 60, "cooldown": 1.9, "aggro": 260.0, "heavy": true},
}

var kind := "skeleton"
var patrol_range := 90.0
var state: State = State.PATROL
var facing := -1
var hp := 1
var max_hp := 1
var alive := true
var cfg: Dictionary
var sprite: AnimatedSprite2D
var origin_x := 0.0
var cooldown := 0.5
var _hit_done := false
var _flash := 0.0
var _frame_size := 96
var _font: Font


func _ready() -> void:
	cfg = CONFIGS[kind]
	max_hp = cfg["hp"]
	hp = max_hp
	origin_x = position.x
	add_to_group("enemies")
	collision_layer = 2
	collision_mask = 1
	var cs := CollisionShape2D.new()
	var cap := CapsuleShape2D.new()
	cap.radius = 8.0
	cap.height = 38.0
	cs.shape = cap
	cs.position = Vector2(0, -19)
	add_child(cs)
	var data := SheetUtil.sheet_frames("res://assets/characters/%s.png" % kind, "res://assets/characters/%s.json" % kind, FPS, LOOPS)
	_frame_size = data["size"]
	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = data["frames"]
	sprite.centered = false
	sprite.offset = Vector2(-CENTER_X, -float(data["feet_row"]))
	add_child(sprite)
	sprite.animation_finished.connect(_on_anim_finished)
	sprite.play("idle")
	_font = load("res://assets/fonts/Cinzel-Variable.ttf")


func _target() -> Player:
	return get_tree().get_first_node_in_group("player") as Player


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += GRAVITY * delta
	if _flash > 0.0:
		_flash -= delta
		sprite.modulate = Color(2.2, 2.2, 2.2) if _flash > 0.0 else Color.WHITE
	if not alive:
		velocity.x = move_toward(velocity.x, 0.0, 500.0 * delta)
		move_and_slide()
		return
	cooldown -= delta
	var p := _target()
	var dx := 0.0
	var dy := 0.0
	var can_see := false
	if p and p.state != Player.State.DEAD:
		dx = p.global_position.x - global_position.x
		dy = p.global_position.y - global_position.y
		can_see = absf(dx) < float(cfg["aggro"]) and absf(dy) < 90.0
	match state:
		State.PATROL:
			velocity.x = facing * float(cfg["speed"]) * 0.5
			if global_position.x > origin_x + patrol_range:
				facing = -1
			elif global_position.x < origin_x - patrol_range:
				facing = 1
			_play("walk")
			if can_see:
				state = State.CHASE
		State.CHASE:
			if not can_see:
				state = State.PATROL
			else:
				if absf(dx) > 2.0:
					facing = 1 if dx > 0.0 else -1
				_chase(absf(dx))
		State.ATTACK:
			velocity.x = 0.0
			if not _hit_done and sprite.frame >= int(cfg["hit_frame"]):
				_hit_done = true
				_do_hit()
		State.HURT:
			velocity.x = move_toward(velocity.x, 0.0, 500.0 * delta)
	sprite.flip_h = facing < 0
	sprite.position.x = -(_frame_size - 2.0 * CENTER_X) if facing < 0 else 0.0
	move_and_slide()
	if cfg.get("leash", false):
		position.x = clampf(position.x, origin_x - patrol_range, origin_x + patrol_range)


func _chase(dist: float) -> void:
	var speed := float(cfg["speed"])
	if cfg.get("ranged", false):
		if dist < float(cfg["keep"]) - 20.0:
			velocity.x = -facing * speed
			_play("walk")
		elif cooldown <= 0.0 and dist <= float(cfg["range"]):
			_start_attack()
		else:
			velocity.x = 0.0
			_play("idle")
	elif dist <= float(cfg["range"]) - 6.0:
		velocity.x = 0.0
		if cooldown <= 0.0:
			_start_attack()
		else:
			_play("idle")
	else:
		velocity.x = facing * speed
		_play("walk")


func _play(anim: String) -> void:
	if sprite.animation != anim or not sprite.is_playing():
		sprite.play(anim)


func _start_attack() -> void:
	state = State.ATTACK
	_hit_done = false
	cooldown = float(cfg["cooldown"])
	velocity.x = 0.0
	sprite.play("attack")


func _do_hit() -> void:
	if cfg.get("ranged", false):
		var a := Arrow.new()
		a.velocity = Vector2(facing * 260.0, 0.0)
		a.damage = int(cfg["damage"])
		a.position = global_position + Vector2(facing * 16.0, -30.0)
		get_parent().add_child(a)
		return
	var p := _target()
	if p == null:
		return
	var reach := float(cfg["range"])
	var box := Rect2(global_position + Vector2(4.0 if facing > 0 else -4.0 - reach, -44.0), Vector2(reach, 44.0))
	if box.intersects(Rect2(p.global_position + Vector2(-8, -38), Vector2(16, 38))):
		p.hurt(int(cfg["damage"]))


func take_damage(amount: int, from_x: float) -> void:
	if not alive:
		return
	var dmg := amount
	var from_dir := 1 if from_x > global_position.x else -1
	if cfg.get("block", false) and from_dir == facing:
		dmg = int(dmg * 0.4)
	hp -= dmg
	_flash = 0.12
	_popup(dmg)
	queue_redraw()
	if hp <= 0:
		_die()
		return
	facing = from_dir
	if not cfg.get("heavy", false) or dmg >= 40:
		state = State.HURT
		velocity.x = -from_dir * 90.0
		sprite.play("hurt")


func _die() -> void:
	alive = false
	state = State.DEAD
	remove_from_group("enemies")
	sprite.play("death")
	var p := _target()
	if p:
		p.souls += int(cfg["souls"])
	get_tree().create_timer(2.0).timeout.connect(_fade_out)


func _fade_out() -> void:
	var t := create_tween()
	t.tween_property(self, "modulate:a", 0.0, 0.8)
	t.tween_callback(queue_free)


func _popup(amount: int) -> void:
	var l := Label.new()
	l.text = str(amount)
	l.add_theme_font_override("font", _font)
	l.add_theme_font_size_override("font_size", 14)
	l.add_theme_color_override("font_color", Color.WHITE)
	l.add_theme_color_override("font_outline_color", Color(0.45, 0.05, 0.05))
	l.add_theme_constant_override("outline_size", 4)
	l.z_index = 20
	l.position = global_position + Vector2(-8, -64)
	get_parent().add_child(l)
	var t := l.create_tween()
	t.tween_property(l, "position:y", l.position.y - 26.0, 0.6)
	t.parallel().tween_property(l, "modulate:a", 0.0, 0.6)
	t.tween_callback(l.queue_free)


func _on_anim_finished() -> void:
	if state == State.ATTACK or state == State.HURT:
		state = State.CHASE


func _draw() -> void:
	if alive and hp < max_hp:
		draw_rect(Rect2(-13, -56, 26, 4), Color(0, 0, 0, 0.8))
		draw_rect(Rect2(-12, -55, 24.0 * hp / max_hp, 2), Color(0.8, 0.12, 0.12))
