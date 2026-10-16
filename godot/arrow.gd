class_name Arrow
extends Node2D
## Archer projectile. Hurts the player on contact, vanishes at the floor or after a while.

var velocity := Vector2(260, 0)
var damage := 18
var life := 2.5


func _ready() -> void:
	scale.x = 1.0 if velocity.x >= 0.0 else -1.0


func _physics_process(delta: float) -> void:
	position += velocity * delta
	life -= delta
	var p := get_tree().get_first_node_in_group("player") as Player
	if p and p.state != Player.State.DEAD and Rect2(p.global_position + Vector2(-8, -38), Vector2(16, 38)).has_point(global_position):
		p.hurt(damage)
		queue_free()
	elif life <= 0.0 or global_position.y >= Room.FLOOR_Y:
		queue_free()


func _draw() -> void:
	draw_line(Vector2(-12, 0), Vector2(4, 0), Color(0.55, 0.4, 0.25), 2.0)
	draw_colored_polygon(PackedVector2Array([Vector2(4, -3), Vector2(10, 0), Vector2(4, 3)]), Color(0.85, 0.88, 0.95))
	draw_line(Vector2(-12, -2), Vector2(-9, 0), Color(0.7, 0.2, 0.2), 1.0)
	draw_line(Vector2(-12, 2), Vector2(-9, 0), Color(0.7, 0.2, 0.2), 1.0)
