extends SceneTree
## Saves a screenshot of the main scene. Needs a display (xvfb-run) and a renderer.
## xvfb-run -a godot --rendering-driver opengl3 --path godot --script res://tests/screenshot.gd -- /tmp/shot.png
func _initialize() -> void:
	var main: Node = load("res://main.tscn").instantiate()
	root.add_child(main)
	_run()

func _run() -> void:
	for i in 90:
		await process_frame
	var path := "/tmp/shot.png"
	var args := OS.get_cmdline_user_args()
	if args.size() > 0:
		path = args[0]
	root.get_texture().get_image().save_png(path)
	print("saved ", path)
	quit()
