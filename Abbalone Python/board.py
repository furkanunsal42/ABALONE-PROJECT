class Board:
    balls = []
    board = []

    def __init__(self):
        self.initialize_board()

    def initialize_board(self):
        self.board = []
        for y in range(9):
            distance_to_middle = abs(4-y)
            self.board.append([i for i in range(9 - distance_to_middle)])

    def is_position_in_range(self, position):
        x = y = None
        if len(position) == 2:
            x, y = position
        elif len(position) == 3:
            x, y, _ = position
        if y > 8:
            return False
        elif x >= len(self.board[y]):
            return False
        else:
            return True

    def find_ball_by_position(self, target_ball, balls=None):
        if target_ball is None:
            return None
        if balls is None:
            balls = self.balls
        if len(target_ball) == 3:
            target_x, target_y, target_color = target_ball
        elif len(target_ball) == 2:
            target_x, target_y = target_ball

        for ball in balls:
            ball_x, ball_y, ball_color = ball
            if {ball_x, ball_y} == {target_x, target_y}:
                return ball
        return None

    def find_borders(self, ball):
        x, y = None, None
        if len(ball) == 2:
            x, y = ball
        elif len(ball) == 3:
            x, y, _ = ball
        if y < 4:
            borders = [[x - 1, y - 1], [x, y - 1],
                       [x - 1, y], [x + 1, y],
                       [x, y + 1], [x + 1, y + 1]]

        elif y == 4:
            borders = [[x - 1, y - 1], [x, y - 1],
                       [x - 1, y], [x + 1, y],
                       [x - 1, y + 1], [x, y + 1]]

        elif y > 4:
            borders = [[x, y - 1], [x + 1, y - 1],
                       [x - 1, y], [x + 1, y],
                       [x - 1, y + 1], [x, y + 1]]

        final_borders = []
        for border in borders:
            x, y = border
            if y > 8:
                final_borders.append(None)
            elif x >= len(self.board[y]):
                final_borders.append(None)
            elif x < 0 or y < 0:
                final_borders.append(None)
            else:
                final_borders.append(border)

        return final_borders

    def display(self):
        board = self.board.copy()

        for ball in self.balls:
            x, y, color = ball
            board[y][x] = color

        for i, layer in enumerate(board):
            print(i ,"  " * abs(4-i), layer)

        self.initialize_board()

    def _display_borders(self, position):
        borders = self.find_borders(position)
        for border_position in borders:
            if border_position is None:
                continue
            x, y, _ = border_position
            if x >= 0 and y >= 0:
                self.board[y][x] = "B"
        self.display()

    def find_border_direction(self, ball_position, border_position):
        borders = self.find_borders(ball_position)
        for direction, border in enumerate(borders):
            if border == border_position:
                return direction
        return None

    @staticmethod
    def opposite_direction(direction_index):
        if 0 > direction_index > 5:
            return None
        opposite_direction = 5 - direction_index
        return opposite_direction

    def find_force(self, ball, direction):
        def is_backed(ball, direction):
            ball_borders = self.find_borders(ball)
            if ball_borders[direction] in self.balls:
                return ball_borders[direction]
            else:
                return False

        behind = ball
        force = 0
        while True:
            behind = is_backed(behind, direction)
            if not behind:
                break
            if behind:
                force += 1
        return force

    def find_head(self, balls, direction):
        block_direction = self.block_check(balls)
        if block_direction is False:
            print("find_head failed (block check fail)")
            return False

        if block_direction == direction or block_direction == self.opposite_direction(direction):
            for ball in balls:
                borders = self.find_borders(ball)
                if borders[direction] not in balls:
                    return ball
        else:
            return None

    def block_check(self, balls):
        color = None
        for ball in balls:
            if color is None:
                color = ball[2]
            elif ball[2] != color:
                print("block check fail (colors are not identical)")
                return False

        if len(balls) == 1:
            return True

        if len(balls) > 3:  # max length test
            print("length test failed")
            return False

        first_detected_direction = None
        for ball in balls:  # linearity test
            direction = None
            ball_borders = self.find_borders(ball)
            for i, ball_border in enumerate(ball_borders):
                if self.find_ball_by_position([ball_border[0], ball_border[1], None], balls) is not None:
                #if ball_border in balls:
                    direction = i
                    if first_detected_direction is None:
                        first_detected_direction = direction
                    else:
                        if direction != first_detected_direction \
                                and direction != self.opposite_direction(first_detected_direction):
                            print("linearity test failed (linearity couldn't proven)")
                            return False

        if direction is None:
            print("linearity test failed (second ball couldn't found)")
            return False

        return first_detected_direction

    def border_check(self, balls, direction):
        for ball in balls:
            borders = self.find_borders(ball)
            if borders[direction] is None:
                print("border check fail")
                return False
        return True

    def direction_check(self, balls, move_direction):
        if len(balls) == 1:
            return None
        block_direction = self.block_check(balls)
        if block_direction is False:
            return False
        else:
            if block_direction != move_direction and block_direction != self.opposite_direction(move_direction):
                return False
        return True

    def force_check(self, balls, direction):
        if self.direction_check(balls, direction):
            head = self.find_head(balls, direction)
            if head is not None and head is not False:
                attacking_position = self.find_borders(head)[direction]
                defending_force = self.find_force(attacking_position, direction)
                if len(balls) > defending_force:
                    return True
            print("force_check (baricated)")
            return False
        elif not self.direction_check(balls, direction):
            for ball in balls:
                borders = self.find_borders(ball)
                moving_position = borders[direction]
                if moving_position in self.balls:
                    print("force check (unsufficent force)")
                    return False
            return True

    def input_check(self, balls):
        for ball in balls:
            if ball not in self.balls:
                print("input error")
                return False
        return True

    def push(self, ball, direction):
        if self.find_ball_by_position(ball) is None:
            return False
        borders = self.find_borders(ball)
        moving_position = borders[direction]
        if self.find_ball_by_position(moving_position) is not None:
            self.push(self.find_ball_by_position(moving_position), direction)
        self.balls.remove(ball)
        if moving_position is None:
            return ["pushed", ball]
        if self.is_position_in_range(moving_position):
            moving_position.append(ball[2])
            self.balls.append(moving_position)
        return True

    def move(self, balls, direction):
        if self.input_check(balls) is False:
            return False
        if self.block_check(balls) is False:
            return False
        if not self.border_check(balls, direction):
            return False
        if not self.force_check(balls, direction):
            return False

        for ball in balls:
            borders = self.find_borders(ball)
            moving_position = borders[direction]
            moving_ball = self.find_ball_by_position(moving_position)
            if moving_ball is not None and moving_ball not in balls:
                push_data = self.push(moving_ball, direction)
            self.balls.remove(ball)
            moving_position.append(ball[2])
            self.balls.append(moving_position)
        return True
