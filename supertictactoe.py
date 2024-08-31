import pygame

pygame.init()
pygame.font.init()
game_font = pygame.font.SysFont('Comic Sans MS', 200)
screen = pygame.display.set_mode((1080, 1080))
clock = pygame.time.Clock()
running = True
turn = 1
winner = 0

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
        if self.boardstate[y][x] == 0:
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
            pygame.draw.rect(screen, "red", (self.active_board[0] * 360 , self.active_board[1] * 360, 360, 360), 10)
        else:
            pygame.draw.rect(screen, "red", (0, 0, 1080, 1080), 10)


    def update(self, position, subgrid_position, player):

        #select the subboard
        board = self.boards[position[1]][position[0]]

        #check if the board is the current selected board
        if not board.enabled:
            return False
        if position != self.active_board and self.active_board != (-1, -1):
            if board.enabled:
                return False
        if result := board.update(subgrid_position, player):
            if board.check_win():
                self.boardstate[position[1]][position[0]] = player
                board.enabled = False
            if self.boardstate[subgrid_position[1]][subgrid_position[0]] == 0:
                self.active_board = subgrid_position
            else:
                self.active_board = (-1, -1)
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

def init_game():
    global turn, winner
    turn = 1
    winner = 0
    superboard = SuperBoard()
    return superboard

superboard = init_game()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            large_grid_position, subgrid_position = process_click(event.pos)
            if superboard.update(large_grid_position, subgrid_position, turn):
                turn *= -1
            if superboard.check_win():
                winner = turn * -1
    
    if winner == 0:
        screen.fill("black")  # Clear the screen before drawing
        superboard.draw()
        pygame.display.flip()
        clock.tick(60)
    else:
        screen.fill("black")
        text_surface = game_font.render(f"{'X' if winner == -1 else 'O'} wins!", False, (255, 255, 255))
        text_surface2 = game_font.render("Click to restart", False, (255, 255, 255))
        screen.blit(text_surface, (540 - text_surface.get_width() // 2, 540 - text_surface.get_height() // 2))
        screen.blit(text_surface2, (540 - text_surface2.get_width() // 2, 540 + text_surface.get_height() // 2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                superboard = init_game()
                break
            if event.type == pygame.QUIT:
                running = False

pygame.quit()
