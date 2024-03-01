import curses
import random
import time

obstacles = []


def main():
    want_obstacles = (
        input("Você quer jogar com obstáculos? (s/n): ").lower().strip() == "s"
    )
    curses.wrapper(game_loop, want_obstacles)


def game_loop(window, want_obstacles):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    # Setup inicial
    global obstacles
    curses.curs_set(0)
    snake = [[12, 15], [11, 15], [10, 15], [9, 15], [8, 15], [7, 15], [6, 15]]
    fruit = get_new_fruit(window=window, snake=snake)
    current_direction = curses.KEY_DOWN
    snake_eat_fruit = False
    score = 0
    high_score = get_high_score()
    game_speed = 150

    if want_obstacles:
        obstacles = generate_obstacles(window=window, count=5, snake=snake, fruit=fruit)

    while True:
        draw_screen(window=window)
        draw_snake(snake=snake, window=window)
        draw_actor(actor=fruit, window=window, char=curses.ACS_DIAMOND, color_pair=2)
        if want_obstacles:
            draw_obstacles(window=window, obstacles=obstacles)
        draw_score(window=window, score=score, high_score=high_score)

        direction = get_new_direction(window=window, timeout=game_speed)
        if direction is None:
            direction = current_direction
        elif direction_is_opposite(
            direction=direction, current_direction=current_direction
        ):
            direction = current_direction
        move_snake(snake=snake, direction=direction, snake_eat_fruit=snake_eat_fruit)

        if (
            snake_hit_border(snake=snake, window=window)
            or snake_hit_itself(snake=snake)
            or (want_obstacles and snake_hit_obstacle(snake=snake, obstacles=obstacles))
        ):
            break

        if snake_hit_fruit(snake=snake, fruit=fruit):
            score += 1
            snake_eat_fruit = True
            fruit = get_new_fruit(window=window, snake=snake)
            game_speed = max(35, game_speed - 5)
            if want_obstacles:
                obstacles = generate_obstacles(
                    window=window, count=5, snake=snake, fruit=fruit
                )
        else:
            snake_eat_fruit = False

        current_direction = direction

    if score > high_score:
        save_high_score(score)
        high_score = score

    finish_game(score=score, window=window, high_score=high_score)


def generate_obstacles(window, count, snake, fruit):
    height, width = window.getmaxyx()
    obstacles = []
    while len(obstacles) < count:
        obstacle = [random.randint(1, height - 2), random.randint(1, width - 2)]
        if obstacle not in snake and obstacle != fruit and obstacle not in obstacles:
            obstacles.append(obstacle)
    return obstacles


def draw_obstacles(window, obstacles):
    for obstacle in obstacles:
        window.addch(obstacle[0], obstacle[1], "X", curses.color_pair(3))


def snake_hit_obstacle(snake, obstacles):
    return snake[0] in obstacles


def get_high_score():
    try:
        with open("high_score.txt", "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return 0


def save_high_score(score):
    with open("high_score.txt", "w") as file:
        file.write(str(score))


def draw_score(window, score, high_score):
    height, width = window.getmaxyx()
    score_text = f"Pontuação: {score}  Recorde: {high_score}"
    window.addstr(1, 2, score_text)


def finish_game(score, window, high_score):
    height, width = window.getmaxyx()
    s = f"Você perdeu! Coletou {score} frutas! Recorde: {high_score}"
    x = int((width - len(s)) / 2)
    y = int(height / 2)
    window.addstr(y, x, s)
    window.refresh()
    time.sleep(2)


def get_new_fruit(window, snake):
    height, width = window.getmaxyx()
    while True:
        fruit = [random.randint(1, height - 2), random.randint(1, width - 2)]
        if fruit not in snake:
            return fruit


def get_new_direction(window, timeout):
    window.timeout(timeout)
    direction = window.getch()
    if direction in [curses.KEY_UP, curses.KEY_LEFT, curses.KEY_DOWN, curses.KEY_RIGHT]:
        return direction
    return None


def direction_is_opposite(direction, current_direction):
    match direction:
        case curses.KEY_UP:
            return current_direction == curses.KEY_DOWN
        case curses.KEY_LEFT:
            return current_direction == curses.KEY_RIGHT
        case curses.KEY_DOWN:
            return current_direction == curses.KEY_UP
        case curses.KEY_RIGHT:
            return current_direction == curses.KEY_LEFT


def move_snake(snake, direction, snake_eat_fruit):
    head = snake[0].copy()
    snake.insert(0, head)
    move_actor(actor=head, direction=direction)
    if not snake_eat_fruit:
        snake.pop()


def move_actor(actor, direction):
    match direction:
        case curses.KEY_UP:
            actor[0] -= 1
        case curses.KEY_LEFT:
            actor[1] -= 1
        case curses.KEY_DOWN:
            actor[0] += 1
        case curses.KEY_RIGHT:
            actor[1] += 1


def snake_hit_border(snake, window):
    head = snake[0]
    return actor_hit_border(actor=head, window=window)


def actor_hit_border(actor, window):
    height, width = window.getmaxyx()
    # EIXO VERTICAL
    if (actor[0] <= 0) or (actor[0] >= (height - 1)):
        return True
    # EIXO HORIZONTAL
    if (actor[1] <= 0) or (actor[1] >= (width - 1)):
        return True
    return False


def snake_hit_itself(snake):
    head = snake[0]
    body = snake[1:]
    return head in body


def snake_hit_fruit(snake, fruit):
    return fruit in snake


def draw_screen(window):
    window.clear()
    window.border(0)


def draw_snake(snake, window):
    head = snake[0]
    body = snake[1:-1]
    tail = snake[-1]
    window.attron(curses.color_pair(1))  # Ativar cor da cobra
    window.addch(head[0], head[1], "O")
    for body_part in body:
        window.addch(body_part[0], body_part[1], "#")
    window.addch(tail[0], tail[1], "~")
    window.attroff(curses.color_pair(1))  # Desativar cor da cobra


def draw_actor(actor, window, char, color_pair):
    window.attron(curses.color_pair(color_pair))  # Ativar cor do ator
    window.addch(actor[0], actor[1], char)
    window.attroff(curses.color_pair(color_pair))  # Desativar cor do ator


def select_difficulty():
    difficulty = {
        "1": 1000,
        "2": 500,
        "3": 150,
        "4": 90,
        "5": 35,
    }
    while True:
        answer = input("Selecione a dificuldade de 1 a 5:")
        game_speed = difficulty.get(answer)
        if game_speed is not None:
            return game_speed
        print("Escolha a dificuldade de 1 a 5!")


if __name__ == "__main__":
    main()
