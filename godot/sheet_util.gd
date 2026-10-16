class_name SheetUtil
extends RefCounted
## Helpers to turn generated sprite sheets into SpriteFrames and to spawn one-shot effects.


static func strip_frames(path: String, fw: int, fh: int, n: int, fps: float, loop := false) -> SpriteFrames:
	var tex: Texture2D = load(path)
	var fs := SpriteFrames.new()
	fs.set_animation_speed("default", fps)
	fs.set_animation_loop("default", loop)
	for i in n:
		var at := AtlasTexture.new()
		at.atlas = tex
		at.region = Rect2(i * fw, 0, fw, fh)
		fs.add_frame("default", at)
	return fs


static func sheet_frames(png: String, json_path: String, fps: Dictionary, loops: Array) -> Dictionary:
	var meta: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(json_path))
	var tex: Texture2D = load(png)
	var size := int(meta["frame"])
	var fs := SpriteFrames.new()
	fs.remove_animation("default")
	for row in meta["rows"]:
		var n: String = row["name"]
		fs.add_animation(n)
		fs.set_animation_speed(n, fps.get(n, 10.0))
		fs.set_animation_loop(n, n in loops)
		for i in int(row["frames"]):
			var at := AtlasTexture.new()
			at.atlas = tex
			at.region = Rect2(i * size, int(row["row"]) * size, size, size)
			fs.add_frame(n, at)
	return {"frames": fs, "size": size, "feet_row": float(meta["feet_row"])}


static func spawn_fx(parent: Node, path: String, n: int, fps: float, pos: Vector2, pivot: Vector2, flip_h := false, flip_v := false, size := 96, scale_f := 1.0) -> AnimatedSprite2D:
	var a := AnimatedSprite2D.new()
	a.sprite_frames = strip_frames(path, size, size, n, fps, false)
	a.centered = false
	a.offset = Vector2(-(size - pivot.x) if flip_h else -pivot.x, -(size - pivot.y) if flip_v else -pivot.y)
	a.flip_h = flip_h
	a.flip_v = flip_v
	a.position = pos
	a.scale = Vector2(scale_f, scale_f)
	a.z_index = 5
	a.animation_finished.connect(a.queue_free)
	parent.add_child(a)
	a.play("default")
	return a
