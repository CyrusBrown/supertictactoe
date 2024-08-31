import pygame

pygame.init()
screen = pygame.display.set_mode((1080, 1080))
clock = pygame.time.Clock()
running = True
turn = 1

def check_win(boardstate):
    print(boardstate)
    # Check rows and columns
    for i in range(3):
        if boardstate[i][0] == boardstate[i][1] == boardstate[i][2] != 0:  # Check rows
            return True
        if boardstate[0][i] == boardstate[1][i] == boardstate[2][i] != 0:  # Check columns
            return True
    
    # Check diagonals
    if boardstate[0][0] == boardstate[1][1] == boardstate[2][2] != 0:
        return True
    if boardstate[0][2] == boardstate[1][1] == boardstate[2][0] != 0:
        return True

    return False

def draw_grid(center, scale, boardstate):
    cx, cy = center
    half_scale = scale / 2

    # Draw vertical lines
    pygame.draw.line(screen, "white", (cx - half_scale, cy - 3 * half_scale), (cx - half_scale, cy + 3 * half_scale), 10)
    pygame.draw.line(screen, "white", (cx + half_scale, cy - 3 * half_scale), (cx + half_scale, cy + 3 * half_scale), 10)

    # Draw horizontal lines
    pygame.draw.line(screen, "white", (cx - 3 * half_scale, cy - half_scale), (cx + 3 * half_scale, cy - half_scale), 10)
    pygame.draw.line(screen, "white", (cx - 3 * half_scale, cy + half_scale), (cx + 3 * half_scale, cy + half_scale), 10)

    for x in range(3):
        for y in range(3):
            player = boardstate[y][x]  # Ensure consistency by accessing as [y][x]

            # Calculate the position for the current cell
            pos_x = cx + (x - 1) * scale
            pos_y = cy + (y - 1) * scale

            if player == 1:
                pygame.draw.circle(screen, "white", (pos_x, pos_y), scale * 0.42, 10)
            elif player == -1:
                pygame.draw.line(screen, "white", (pos_x - scale * 0.33, pos_y - scale * 0.33), 
                                            (pos_x + scale * 0.33, pos_y + scale * 0.33), 10)
                pygame.draw.line(screen, "white", (pos_x + scale * 0.33, pos_y - scale * 0.33), 
                                            (pos_x - scale * 0.33, pos_y + scale * 0.33), 10)

class Board:
    def __init__(self, center, scale):
        self.boardstate = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.center = center
        self.scale = scale
        self.enabled = True

    def update(self, position, player):
        x, y = position
        if self.boardstate[y][x] == 0:  # Update using consistent [y][x] indexing
            self.boardstate[y][x] = player
            return True
        return False
    
    def draw(self):
        draw_grid(self.center, self.scale, self.boardstate)
    
    def check_win(self):
        return check_win(self.boardstate)

class SuperBoard:
    def __init__(self):
        self.boards = [
            [Board((180 + x * 360, 180 + y * 360), 110) for x in range(3)]
            for y in range(3)
        ]
        self.active_board = (1, 1)
        self.boardstate = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    
    def draw(self):
        for row in self.boards:
            for board in row:
                if board.enabled:
                    board.draw()
        draw_grid((540, 540), 360, self.boardstate)

        #draw highlight for the active board
        if self.active_board != (-1, -1):
            pygame.draw.rect(screen, "red", (self.active_board[0] * 360, self.active_board[1] * 360, 360, 360), 10)
        else:
            pygame.draw.rect(screen, "red", (0, 0, 1080, 1080), 10)


    def update(self, position, subgrid_position, player):
        board = self.boards[position[1]][position[0]]  # Consistent [y][x] indexing
        if position != self.active_board:
            if board.enabled:
                return False
            else:
                self.active_board = (-1, -1)
        if result := board.update(subgrid_position, player):
            self.active_board = subgrid_position
            print(board.check_win())
            if board.check_win():
                self.boardstate[position[1]][position[0]] = player
                board.enabled = False
        return result
    
    def check_win(self):
        return check_win(self.boardstate)


                         
def process_click(position):
    # Determine the large grid position
    grid_x = position[0] // 360
    grid_y = position[1] // 360
    large_grid_position = (grid_x, grid_y)
    
    # Determine the position within the selected large grid
    subgrid_x = (position[0] % 360) // 120
    subgrid_y = (position[1] % 360) // 120
    subgrid_position = (subgrid_x, subgrid_y)
    
    return large_grid_position, subgrid_position

superboard = SuperBoard()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            large_grid_position, subgrid_position = process_click(event.pos)
            if superboard.update(large_grid_position, subgrid_position, turn):
                turn *= -1
    screen.fill("black")  # Clear the screen before drawing
    superboard.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
