extends SceneTree
## Saves a screenshot of the main scene. Needs a display (xvfb-run) and a renderer.
## xvfb-run -a godot --rendering-driver opengl3 --path godot --script res://tests/screenshot.gd -- /tmp/shot.png
func _initialize() -> void:
	var main: Node = load("res://main.tscn").instantiate()
	root.add_child(main)
	_run()

func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var main := root.get_node("Main")
	if args.size() > 1 and args[1] == "combat":
		var p: Player = main.get_node("Player")
		for i in 20:
			await process_frame
		p.position.x = 560.0
		for i in 50:
			await process_frame
		Input.action_press("attack")
		for i in 14:
			await process_frame
		Input.action_release("attack")
	else:
		for i in 90:
			await process_frame
	var path := "/tmp/shot.png"
	if args.size() > 0:
		path = args[0]
	root.get_texture().get_image().save_png(path)
	print("saved ", path)
	quit()
