extends Node2D

var _dead_time := 0.0


func _ready() -> void:
	print("Ashen Veil boot OK - Godot ", Engine.get_version_info().string)


func _process(delta: float) -> void:
	var p := get_node_or_null("Player") as Player
	if p and p.state == Player.State.DEAD:
		_dead_time += delta
		if _dead_time > 2.5 and DisplayServer.get_name() != "headless":
			get_tree().reload_current_scene()
