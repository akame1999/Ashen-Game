extends SceneTree
## Headless smoke test.  Run: godot --headless --path godot --script res://tests/test_player.gd
var failures := 0

func check(cond: bool, msg: String) -> void:
	if cond:
		print("PASS ", msg)
	else:
		failures += 1
		print("FAIL ", msg)

func frames(n: int) -> void:
	for i in n:
		await physics_frame

func tap(action: String, n := 3) -> void:
	Input.action_press(action)
	await frames(n)
	Input.action_release(action)

func _initialize() -> void:
	var main: Node = load("res://main.tscn").instantiate()
	root.add_child(main)
	_run(main)

func _run(main: Node) -> void:
	var p: Player = main.get_node("Player")
	var room: Room = main.get_node("Room")
	await frames(40)
	check(room.parallax_count == 5 and room.torch_count >= 5 and room.platform_count >= 4, "room built (parallax, torches, platforms)")
	check(p.is_on_floor(), "player lands on floor")
	check(p.sprite.animation == "idle", "idle animation")
	var x0 := p.global_position.x
	Input.action_press("move_right")
	await frames(30)
	check(p.global_position.x > x0 + 20.0 and p.sprite.animation == "run", "runs right")
	Input.action_release("move_right")
	Input.action_press("move_left")
	await frames(10)
	check(p.facing == -1 and p.sprite.flip_h, "faces left")
	Input.action_release("move_left")
	await frames(5)
	await tap("jump")
	await frames(5)
	check(not p.is_on_floor() and p.sprite.animation in ["jump", "fall"], "jumps")
	await frames(120)
	check(p.is_on_floor(), "lands again")
	await tap("attack", 2)
	await frames(2)
	check(p.state == Player.State.ATTACK and p.sprite.animation == "light1", "light attack")
	await frames(70)
	check(p.state == Player.State.NORMAL, "attack ends")
	await tap("heavy", 2)
	await frames(2)
	check(p.sprite.animation == "heavy", "heavy attack")
	await frames(90)
	await tap("skill", 2)
	await frames(2)
	check(p.sprite.animation == "skill" and p.fp < p.max_fp, "skill (costs FP)")
	await frames(90)
	await tap("dodge", 2)
	await frames(2)
	check(p.state == Player.State.DODGE and p.invulnerable, "dodge is invulnerable")
	await frames(40)
	check(p.state == Player.State.NORMAL and not p.invulnerable, "dodge ends")
	var hp0 := p.hp
	p.hurt(25)
	check(p.hp == hp0 - 25, "damage reduces HP")
	await frames(40)
	p.die()
	await frames(5)
	check(p.state == Player.State.DEAD and p.sprite.animation == "death", "death")
	print("FAILURES: ", failures)
	quit(failures)
