extends SceneTree
## Headless combat test. Run: godot --headless --path godot --script res://tests/test_combat.gd
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
	await frames(30)
	check(room.enemy_count == 5, "room spawned 5 enemies")
	for e in get_nodes_in_group("enemies"):
		e.queue_free()
	await frames(3)
	# every enemy kind builds and has an attack animation
	for k in Enemy.CONFIGS:
		var t := Enemy.new()
		t.kind = k
		t.position = Vector2(-300, 420)
		main.add_child(t)
		await frames(2)
		check(t.sprite.sprite_frames.has_animation("attack") and t.sprite.sprite_frames.has_animation("death"), "%s sheet loaded" % k)
		t.queue_free()
	await frames(3)
	# player damages a skeleton
	var e := Enemy.new()
	e.kind = "skeleton"
	e.position = Vector2(p.position.x + 30, 420)
	main.add_child(e)
	await frames(5)
	p.facing = 1
	await tap("attack", 2)
	await frames(30)
	check(e.hp < e.max_hp, "light attack damages skeleton (hp %d)" % e.hp)
	# skeleton hurts player
	var php := p.hp
	for i in 400:
		if p.hp < php:
			break
		if e.alive:
			e.position.x = p.position.x + 40.0
		await physics_frame
	check(p.hp < php, "skeleton hurts player (hp %d)" % p.hp)
	# kill it, collect souls
	var souls0 := p.souls
	for i in 12:
		if not e.alive:
			break
		e.position.x = p.position.x + 30.0
		e.cooldown = 5.0
		p.facing = 1
		await frames(40)
		await tap("attack", 2)
		await frames(50)
	check(not e.alive and p.souls == souls0 + 12, "skeleton dies and drops souls (%d)" % p.souls)
	# archer arrow
	var a := Enemy.new()
	a.kind = "archer"
	a.position = Vector2(p.position.x + 200, 420)
	main.add_child(a)
	await frames(10)
	p.iframes = 0.0
	var hp1 := p.hp
	await frames(400)
	check(p.hp < hp1, "archer arrow hurts player (hp %d)" % p.hp)
	# soul burst hits enemies at range, costs FP, starts a cooldown
	for n in get_nodes_in_group("enemies"):
		n.queue_free()
	await frames(3)
	p.iframes = 0.0
	p.fp = p.max_fp
	var sb := Enemy.new()
	sb.kind = "skeleton"
	sb.position = Vector2(p.position.x + 90, 420)
	main.add_child(sb)
	await frames(2)
	await tap("soul_burst", 2)
	await frames(40)
	check(not sb.alive and p.fp < p.max_fp - 30.0 and float(p.cd.get("soul_burst", 0.0)) > 0.0, "soul burst kills in radius, costs FP, cooldown starts")
	print("FAILURES: ", failures)
	quit(failures)
