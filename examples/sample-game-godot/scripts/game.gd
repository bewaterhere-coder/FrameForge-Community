extends Node2D

const VIEW_SIZE := Vector2(960.0, 540.0)
const PLAYER_SPEED := 250.0
const PLAYER_RADIUS := 13.0
const GEM_RADIUS := 10.0

var player_position := Vector2(480.0, 330.0)
var gems: Array[Vector2] = [
	Vector2(175.0, 175.0),
	Vector2(760.0, 210.0),
	Vector2(610.0, 420.0),
]
var collected := 0
var finished := false


func _process(delta: float) -> void:
	if finished:
		return

	var direction := Vector2.ZERO
	if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT):
		direction.x -= 1.0
	if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT):
		direction.x += 1.0
	if Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP):
		direction.y -= 1.0
	if Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN):
		direction.y += 1.0

	if direction.length_squared() > 0.0:
		player_position += direction.normalized() * PLAYER_SPEED * delta
		player_position.x = clampf(player_position.x, 24.0, VIEW_SIZE.x - 24.0)
		player_position.y = clampf(player_position.y, 82.0, VIEW_SIZE.y - 24.0)

	for index in range(gems.size() - 1, -1, -1):
		if player_position.distance_to(gems[index]) < PLAYER_RADIUS + GEM_RADIUS + 4.0:
			gems.remove_at(index)
			collected += 1

	finished = gems.is_empty()
	queue_redraw()


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, VIEW_SIZE), Color("#172A35"))
	_draw_ground()
	_draw_trees()
	_draw_house()
	_draw_gems()
	_draw_player()
	_draw_hud()


func _draw_ground() -> void:
	for x in range(0, 960, 48):
		draw_line(Vector2(x, 72), Vector2(x, 540), Color("#24443D"), 1.0)
	for y in range(72, 540, 48):
		draw_line(Vector2(0, y), Vector2(960, y), Color("#24443D"), 1.0)
	draw_polygon(
		PackedVector2Array([
			Vector2(290, 540), Vector2(410, 240), Vector2(505, 240), Vector2(650, 540)
		]),
		PackedColorArray([Color("#8D744D")])
	)


func _draw_trees() -> void:
	var positions := [
		Vector2(70, 180), Vector2(140, 310), Vector2(830, 160),
		Vector2(870, 350), Vector2(710, 460), Vector2(235, 450)
	]
	for point in positions:
		draw_rect(Rect2(point + Vector2(-5, 12), Vector2(10, 28)), Color("#684B36"))
		draw_circle(point, 27.0, Color("#285344"))
		draw_circle(point + Vector2(-9, -8), 17.0, Color("#477B52"))
		draw_circle(point + Vector2(10, -5), 15.0, Color("#5C8D58"))


func _draw_house() -> void:
	draw_rect(Rect2(355, 112, 250, 126), Color("#81583C"))
	draw_colored_polygon(
		PackedVector2Array([
			Vector2(335, 125), Vector2(480, 40), Vector2(625, 125)
		]),
		Color("#B06F4D")
	)
	draw_rect(Rect2(380, 145, 48, 42), Color("#A9C8C4"))
	draw_rect(Rect2(532, 145, 48, 42), Color("#A9C8C4"))
	draw_rect(Rect2(458, 169, 44, 69), Color("#4B342A"))
	draw_circle(Vector2(493, 205), 3.0, Color("#EBCB80"))


func _draw_gems() -> void:
	for gem in gems:
		var points := PackedVector2Array([
			gem + Vector2(0, -GEM_RADIUS),
			gem + Vector2(GEM_RADIUS, 0),
			gem + Vector2(0, GEM_RADIUS),
			gem + Vector2(-GEM_RADIUS, 0)
		])
		draw_colored_polygon(points, Color("#F4C75E"))
		draw_polyline(PackedVector2Array([
			points[0], points[1], points[2], points[3], points[0]
		]), Color("#FFE9A6"), 2.0)


func _draw_player() -> void:
	draw_circle(player_position + Vector2(0, 12), 17.0, Color("#10251F"))
	draw_rect(Rect2(player_position + Vector2(-9, -1), Vector2(18, 25)), Color("#4D78B5"))
	draw_circle(player_position + Vector2(0, -9), 11.0, Color("#E6B98A"))
	draw_arc(player_position + Vector2(0, -10), 11.0, PI, TAU, 12, Color("#513B31"), 5.0)


func _draw_hud() -> void:
	draw_rect(Rect2(20, 18, 230, 42), Color("#101D2B"))
	draw_string(
		ThemeDB.fallback_font,
		Vector2(36, 46),
		"GEM TRAIL  -  %d / 3" % collected,
		HORIZONTAL_ALIGNMENT_LEFT,
		-1,
		20,
		Color("#F5EED7")
	)
	if finished:
		draw_rect(Rect2(255, 215, 450, 100), Color("#101D2B"))
		draw_string(
			ThemeDB.fallback_font,
			Vector2(340, 275),
			"All gems collected!",
			HORIZONTAL_ALIGNMENT_LEFT,
			-1,
			30,
			Color("#8DE5B8")
		)
