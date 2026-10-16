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
const CENTER_X := 44.0 # character's x centre inside a 96px frame
const SHEET := "res://assets/characters/player.png"
const META := "res://assets/characters/player.json"
const FPS := {"idle": 6.0, "run": 12.0, "jump": 8.0, "fall": 8.0, "dodge": 14.0, "light1": 14.0,
		"light2": 14.0, "heavy": 10.0, "skill": 12.0, "hurt": 8.0, "death": 8.0}
const LOOPS := ["idle", "run", "fall"]

var state: State = State.NORMAL
var facing := 1
var invulnerable := false
var sprite: AnimatedSprite2D
var attack_name := ""
var combo_queued := false
var dodge_time := 0.0
var _frame_size := 96
var max_hp := 320
var hp := 320
var max_fp := 120.0
var fp := 120.0
var level := 1
var souls := 27
const SKILL_COST := 20.0
const FP_REGEN := 4.0


func _ready() -> void:
	_setup_input()
	_build_sprite()
	sprite.animation_finished.connect(_on_anim_finished)
	sprite.play("idle")


func _setup_input() -> void:
	var keys := {"move_left": [KEY_A, KEY_LEFT], "move_right": [KEY_D, KEY_RIGHT],
			"jump": [KEY_SPACE, KEY_W, KEY_UP], "dodge": [KEY_SHIFT], "attack": [KEY_J],
			"heavy": [KEY_K], "skill": [KEY_E]}
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
	var meta: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(META))
	var tex: Texture2D = load(SHEET)
	_frame_size = int(meta["frame"])
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
	sprite.offset = Vector2(-CENTER_X, -float(meta["feet_row"]))
	add_child(sprite)


func _physics_process(delta: float) -> void:
	fp = minf(max_fp, fp + FP_REGEN * delta)
	if not is_on_floor():
		velocity.y += GRAVITY * delta
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
			if Input.is_action_just_pressed("jump") and is_on_floor():
				velocity.y = JUMP_V
			if Input.is_action_just_pressed("dodge") and is_on_floor():
				_start_dodge()
			elif Input.is_action_just_pressed("attack"):
				_start_attack("light1")
			elif Input.is_action_just_pressed("heavy"):
				_start_attack("heavy")
			elif Input.is_action_just_pressed("skill") and fp >= SKILL_COST:
				fp -= SKILL_COST
				_start_attack("skill")
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
		State.HURT:
			velocity.x = move_toward(velocity.x, 0.0, 600.0 * delta)
	sprite.flip_h = facing < 0
	sprite.position.x = -(_frame_size - 2.0 * CENTER_X) if facing < 0 else 0.0
	move_and_slide()


func _update_move_anim() -> void:
	var anim := "idle"
	if not is_on_floor():
		anim = "jump" if velocity.y < 0.0 else "fall"
	elif absf(velocity.x) > 1.0:
		anim = "run"
	if sprite.animation != anim or not sprite.is_playing():
		sprite.play(anim)


func _start_dodge() -> void:
	state = State.DODGE
	invulnerable = true
	dodge_time = DODGE_TIME
	sprite.play("dodge")


func _start_attack(anim: String) -> void:
	state = State.ATTACK
	attack_name = anim
	combo_queued = false
	velocity.x = facing * 60.0
	sprite.play(anim)


func hurt(amount: int = 30) -> void:
	if invulnerable or state == State.DEAD:
		return
	hp = maxi(0, hp - amount)
	if hp == 0:
		die()
		return
	state = State.HURT
	velocity.x = -facing * 120.0
	sprite.play("hurt")


func die() -> void:
	state = State.DEAD
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
