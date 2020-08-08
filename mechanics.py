#Name: Austin Douglass
# 9/4/18
#
# Description: Goal is to create a console level version of the game
# Project Z Console

#Problems: AI running into shots, shots around walls
# might need to do damage check before boundary due to bullets disappering in front of enemies...

import random, audio, re
from copy import deepcopy

SHOW_DEBUG = False
SIZE = {'columns' : 16, 'rows' : 9 }
LEVEL_MAX = 12

#Types of blocks in the game
ENEMIES = {
#ENEMY BLOCKS:
#-actual enemies
    'E' : {'type' : 'E', 'health' : 2, 'damage' : 1},   #red default moving & shooting enemy
    'G' : {'type' : 'G', 'health' : 3, 'damage' : 1},   #green 4 way shot non-moving block
    'B' : {'type' : 'B', 'health' : 3, 'damage' : 0},   #brown non-moving block

#CREATIVE BLOCKS:
#-used to differentiate from actual enemy blocks
    '3' : {'type' : '3', 'health' : 9, 'damage' : 0},   #mimics white block in selection
    'e' : {'type' : 'e', 'health' : 2, 'damage' : 1},
    'g' : {'type' : 'g', 'health' : 3, 'damage' : 1},
    'b' : {'type' : 'b', 'health' : 3, 'damage' : 0},

#MENU BLOCKS:
#-used for selections in menu
    'v' : {'type' : 'v', 'health' : 3, 'damage' : 0},   # 1
    'w' : {'type' : 'w', 'health' : 3, 'damage' : 0},   # 2
    'x' : {'type' : 'x', 'health' : 3, 'damage' : 0},   # 3
    'y' : {'type' : 'y', 'health' : 3, 'damage' : 0},   # 4
    'z' : {'type' : 'z', 'health' : 3, 'damage' : 0},   # 5

#OTHER BLOCKS: (not considered enemies)
#   'P' - player block
#   '0' - empty space white block
#   '1' - blocked space black block
    }

NON_MOVERS      = ['B', 'G', 'v', 'w', 'x', 'y', 'z', 'e', 'g', 'b', '3']
MENU_BLOCKS     = ['v', 'w', 'x', 'y', 'z']

def run() -> None:
#runs the console version of the game
    if SHOW_DEBUG:
        print("~ Starting game.")
        
    game = GameBoard(SIZE['columns'], SIZE['rows'], 1)
    running = True
    game_round = 0

    while running:
        game.display_board()
        game.display_data()
        
        running = movement_input(game, input('Movement: '))
        shot_input(game, input('Shot: '))
        game.move_bullets()
        game.move_enemies('E')
        game.add_enemy_bullets('E')

        game_round += 1

    if SHOW_DEBUG:
        print("~ Ending game.")

def movement_input(game : 'GameBoard', key : str) -> bool:
#takes wasd input and moves the player in that direction (q quits game)
    if key == 'q':
        return False
    elif key == 'w':
        game.move_player(-1, 0)
    elif key == 's':
        game.move_player(1, 0)
    elif key == 'a':
        game.move_player(0, -1)
    elif key == 'd':
        game.move_player(0, 1)
    return True

def shot_input(game : 'GameBoard', key: str) -> None:
#takes wasd input for player bullet direction
    if key == 'w':
        game.add_bullet('S', game.player['location'], [-2, 0])
    elif key == 's':
        game.add_bullet('S', game.player['location'], [2, 0])
    elif key == 'a':
        game.add_bullet('S', game.player['location'], [0, -2])
    elif key == 'd':
        game.add_bullet('S', game.player['location'], [0, 2])

def block_input(game : 'GameBoard', key: str) -> None:
#takes wasd input for player block placement direction
    if key == 'w':
        game.add_enemy([-1, 0])
    elif key == 's':
        game.add_enemy([1, 0])
    elif key == 'a':
        game.add_enemy([0, -1])
    elif key == 'd':
        game.add_enemy([0, 1])

def select_input(game, block : str) -> None:
    game.set_block(block)

class GameBoard:
    def __init__(self, columns, rows, level):
    #initializes the board with basic data
        self.board = [[0 for x in range(columns)] for y in range(rows)] 
        self.info = {'playtime' : 0, 'row_max' : rows, 'col_max' : columns,
                     'current_level' : level }
        self.player = {'location' : [-1,-1], 'health' : 3, 'damage' : 1}
        self.timer = 0
        self.enemies = []
        self.bullets = []
        self.menu_select = 0   #menu select determines which menu block was pressed if any [default 0]
        self.block_select = 'E'
        self.load_board()

    def get_board(self) -> list:
    #returns game board
        return self.board

    def display_board_values(self) -> None:
    #same thing as display_board() except in context of a list
        if SHOW_DEBUG:
            print("~ In display_board_values()")
        for row in range(self.info['row_max']):
            print(self.board[row], row)

    def display_board(self) -> None:
        if SHOW_DEBUG:
            print("~ In display_board()")
        for row in range(self.info['row_max']):
            for col in range(self.info['col_max']):
                print(self.board[row][col], end = '')
            print()

    def display_data(self) -> None:
    #displays data stored about the game
        print('Info:')
        for k, v in self.info.items():
            print(k, v, end= ' | ')
        print()

        print('Player:')
        for k, v in self.player.items():
            print(k, v, end= ' | ')
        print()

        print('Enemies:')
        for enemy in self.enemies:            
            for k, v in enemy.items():
                print(k, v, end= ' | ')
            print()

    def initialize_board(self, b_data) -> None:
    #initializes the board from the file
        for row in range(self.info['row_max']):
            for col in range(self.info['col_max']):
                self.board[row][col] = b_data[row][col]
                if self.board[row][col] == 'P':
                    self.player['location'] = [row,col]
                elif self.board[row][col] != '0' and self.board[row][col] != '1':
                    self.create_enemy(self.board[row][col], [row,col])

    def load_board(self) -> None:
    #retrieves board layout from a level file
        with open('data\levels\lvl_' + str(self.info['current_level']) + '.txt', 'r') as file:
            b_data = file.read().splitlines()
        self.initialize_board(b_data)

    def create_enemy(self, e_type, coords : list) -> None:
    #creates an enemy by dictionary and adds it to the list
        enemy = deepcopy(ENEMIES[e_type])
        enemy['location'] = coords
        self.enemies.append(enemy)

    def move_player(self, r_move, c_move) -> None:
        row, col = self.player['location']
        if self.in_boundary(row + r_move, col + c_move) and self.board[row+r_move][col+c_move] not in ENEMIES.keys():
            self.board[row][col] = '0'
            row += r_move
            col += c_move
            self.board[row][col] = 'P'
            self.player['location'] = [row,col]

    def add_bullet(self, bullet_type : str, location : list, direction : list) -> None:
        self.bullets.append({'type' : bullet_type, 'location' : location, 'direction' : direction })

    def move_bullets(self) -> None:
    #moves all bullets on screen
        if SHOW_DEBUG:
            print("~ In move_bullets()")
            
        remove_bullets = []
        
        for bullet in self.bullets:
            row, col = bullet['location']
            r_move, c_move = bullet['direction']
            if self.board[row][col] == bullet['type']:
                self.board[row][col] = '0'

            #switching which statement before "and" fixes 1-block shots but causes out of bounds error
            if self.in_boundary(row+r_move, col+c_move) and self.damage_check(row, col, r_move, c_move, bullet['type']):
                row += r_move
                col += c_move 
                self.board[row][col] = bullet['type']
                bullet['location'] = [row, col]
            else:
                remove_bullets.append(bullet)

        for b in remove_bullets:
            self.bullets.remove(b)

    def damage_check(self, row, col, r_move, c_move, bullet_type) -> bool:
    #checks if a moving object will damage an enemy or player
        if self.board[row][col] == '1':
            return False
        
        for i in range(abs(r_move)):
            row += abs(r_move)//r_move
            if self.board[row][col] == 'P':
                self.player['health'] -= 1
                return False
            elif (bullet_type == 'S' or self.board[row][col] in NON_MOVERS) and self.board[row][col] in ENEMIES.keys():
                enemy = self.get_enemy([row, col])
                enemy['health'] -= self.player['damage']
                if enemy['health'] == 0:
                    self.board[row][col] = '0'
                    self.check_menu_blocks(enemy)
                    self.enemies.remove(enemy)
                return False
            elif self.board[row][col] != '0':
                return False

        for i in range(abs(c_move)):
            col += abs(c_move)//c_move
            if self.board[row][col] == 'P':
                self.player['health'] -= 1
                return False
            elif (bullet_type == 'S' or self.board[row][col] in NON_MOVERS) and self.board[row][col] in ENEMIES.keys():
                enemy = self.get_enemy([row, col])
                enemy['health'] -= self.player['damage']
                if enemy['health'] == 0:
                    self.board[row][col] = '0'
                    self.check_menu_blocks(enemy)
                    self.enemies.remove(enemy)
                return False
            elif self.board[row][col] != '0':
                return False
            
        return True

    def get_enemy(self, location) -> dict:
    #finds and returns enemy by a location
        for enemy in self.enemies:
            if enemy['location'] == location:
                return enemy
        

    def in_boundary(self, row, col) -> bool:
    #checks if coordinate is in board boundaries
        return (self.info['row_max'] > row > -1
                and self.info['col_max'] > col > -1
                and self.board[row][col] != '1')

    def move_enemies(self, e_type) -> None:
    #moves enemy type around the board
        p_row, p_col = self.player['location']
        for enemy in self.enemies:
            if enemy['type'] == e_type:
                row, col = enemy['location']
                self.board[row][col] = '0'
                movement = [0,0]
                if row != p_row:
                    if row > p_row:
                        movement[0] = -1
                    else:
                        movement[0] = 1
                if col != p_col:
                    if col > p_col:
                        movement[1] = -1
                    else:
                        movement[1] = 1

                enemy['location'] = self.movement_choice(movement, [row, col])
                r, c = enemy['location']
                self.board[r][c] = enemy['type']

    def movement_choice(self, movement : list, location : list) -> list:
    #randomly chooses a movement option based on free spaces
        choice = random.randint(0,1)
        row, col = location
        location[choice] += movement[choice]
        r, c = location
        if self.in_boundary(r, c) and self.board[r][c] == '0':
            return location
        
        location = [row, col]
        choice = abs(choice-1)
        location[choice] += movement[choice]
        r, c = location
        if self.in_boundary(r, c) and self.board[r][c] == '0':
            return location

        return [row, col]

    def add_enemy_bullets(self, e_type) -> None:
    #adds enemy bullets
        p_row, p_col = self.player['location']
        for enemy in self.enemies:
            if enemy['type'] == e_type:
                row, col = enemy['location']
                movement = [0,0]

                if col == p_col:
                    if row > p_row:
                        self.add_bullet('s', enemy['location'], [-2,0])
                    else:
                        self.add_bullet('s', enemy['location'], [2,0])
                    return None                    
                elif row == p_row:
                    if col > p_col:
                        self.add_bullet('s', enemy['location'], [0,-2])
                    else:
                        self.add_bullet('s', enemy['location'], [0,2])
                    return None
                else:
                    if row > p_row:
                        movement[0] = -2
                    else:
                        movement[0] = 2                    
                    if col > p_col:
                        movement[1] = -2
                    else:
                        movement[1] = 2
                        
                choice = random.randint(0,1)        
                movement[choice] = 0
                self.add_bullet('s', enemy['location'], movement)

    def add_g_bullets(self) -> None:
    #adds enemy bullets for G enemy
        for enemy in self.enemies:
            if enemy['type'] == 'G':
                self.add_bullet('s', enemy['location'], [-2,0])
                self.add_bullet('s', enemy['location'], [2,0])
                self.add_bullet('s', enemy['location'], [0,-2])
                self.add_bullet('s', enemy['location'], [0,2])

    def get_player_info(self) -> dict:
        return self.player

    def get_enemies_info(self) -> list:
        return self.enemies

    def get_enemies_health(self) -> list:
        hp = []
        for enemy in self.enemies:
            hp.append(enemy['health'])
        return hp

    def total_enemies_health(self) -> int:
        total = 0
        for enemy in self.enemies:
            total += enemy['health']
        return total

    def increment_time(self) -> None:
        self.timer += 1

    def get_time(self) -> int:
        return self.timer
        
    def get_level(self) -> int:
        return self.info['current_level']

    def set_level(self, new_level : int):
        self.info['current_level'] = new_level

    def next_level(self):
        if self.info['current_level'] < LEVEL_MAX:
            self.info['current_level'] += 1

    def prev_level(self):
        if self.info['current_level'] > 0:
            self.info['current_level'] -= 1

    def get_level_max(self) -> int:
        return LEVEL_MAX

    def reset_board(self) -> None:
    #reintisializes whole GameBoard
        self.board = [[0 for x in range(self.info['col_max'])] for y in range(self.info['row_max'])] 
        self.player = {'location' : [-1,-1], 'health' : 3, 'damage' : 1}
        self.info['playtime'] += self.timer//60
        self.timer = 0
        self.enemies = []
        self.bullets = []
        self.load_board()

    def status(self) -> str:
        if self.player['health'] == 0:
            return 'Game Over'
        elif len(self.enemies) == 0:
            return 'Game Won'
        else:
            return 'continue'
        
    def get_non_movers(self) -> list:
        return NON_MOVERS

    def get_menu_blocks(self) -> list:
        return MENU_BLOCKS

    def reset_menu(self) -> None:
        self.menu_select = 0

    def get_menu_select(self) -> int:
        return self.menu_select

    def check_menu_blocks(self, enemy : 'if type is a menu block') -> None:
    #changes menu_selct if a block is changed
        if enemy['type'] in MENU_BLOCKS:
            self.menu_select = MENU_BLOCKS.index(enemy['type']) + 1

    def set_block(self, block : str) -> None:
    #sets the block_select for creating levels
        self.block_select = block

    def add_enemy(self, direction : list) -> None:
        location = [self.player['location'][0] + direction[0], self.player['location'][1] + direction[1]]
        self.create_enemy(self.block_select, location)

    def re_level_check(self) -> bool:
    #uses regular expressions to check if level name is the same
        return True
        

if __name__ == "__main__":
    run()
