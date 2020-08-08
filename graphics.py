#Name: Austin Douglass
# 9/13/18 - 7/30/19
#
# File: graphics.py
# Note: Graphics for mechanics engine and testing how full game will run

#Problem: shots going through walls*
#Idea: Create run into a class (play_game) to use in a "driver" script; this will be helpful for main menu

import pygame, mechanics, audio, re

SHOW_DEBUG = True
RESOLUTION = (1280, 720)
COLOR = {
    'BLUE3' : [0, 128, 255], 'BLUE2' : [77, 166, 255], 'BLUE1' : [153, 204, 255],
    'RED2' : [255, 26, 26], 'RED1' : [255, 102, 102], 'BLACK' : [0, 0, 0],
    'WHITE' : [255,255,255], 'YELLOW' : [255, 255, 0], 'GREY' : [128,128,128],
    'GREEN3' : [0, 230, 0], 'GREEN2' : [77, 255, 77], 'GREEN1' : [153, 255, 153],
    'BROWN3' : [115, 77, 38], 'BROWN2' : [172, 115, 57], 'BROWN1' : [204, 153, 102]
    }
SIZE = {'columns' : 16, 'rows' : 9 }

CURRENT_LEVEL = 0

def run():
    pygame.mixer.pre_init(44100, -16, 2, 1024)
    pygame.init()

    music = audio.Music()
    running, paused = True, False
    current_menu = 'main'
    status = 'continue'
    setup_window(RESOLUTION)
    surface = pygame.display.get_surface()
    clock = pygame.time.Clock()
    game = mechanics.GameBoard(SIZE['columns'], SIZE['rows'], CURRENT_LEVEL)
    input_delayer = get_delayer()

    #graphics board - saves rectangles (idea color whole squares? p v e)
    graphics_board =  setup_gb(surface, surface.get_width(), surface.get_height())
    
    # main display/game loop
    while running:
        clock.tick(60)
        display_game(game, surface, graphics_board, paused, status, current_menu)
        old_info = [game.get_player_info()['health'], len(game.get_enemies_info()), game.total_enemies_health()]
        if current_menu in ['main']:
            if game.get_level() != 0:
                load_menu(game, input_delayer)
            game_movement(game, input_delayer)
            current_menu, running = check_selection(game, music)
        elif current_menu in ['level select']:
            if game.get_level() < 1:
                load_next_level(game, input_delayer)
            running, current_menu = level_select_input(running, current_menu, game, input_delayer, music)
        elif not paused and status == 'continue':
            paused = game_movement(game, input_delayer)
            running = handle_window(music)
        elif status == 'Game Over':
            status, running, current_menu = game_over_menu(surface, game, input_delayer, music)
        elif status == 'Game Won':
            status, running, current_menu = game_won_menu(surface, game, input_delayer, music)
        else:
            paused, running, current_menu = pause_menu(surface, game, input_delayer)

        if current_menu not in ['level select']:
            audio.chooseSounds(old_info[0] > game.get_player_info()['health'],
                               old_info[1] > len(game.get_enemies_info()),
                               old_info[2] > game.total_enemies_health()
                               )
        status = game.status()
        
    pygame.quit()

def setup_window(size: tuple):
    logo = pygame.image.load("logo32x32.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("Austin's Pygame Project")
    pygame.display.set_mode(size)   #pygame.RESIZABLE or pygame.FULLSCREEN note: resolution doesn't change currently
    #print(size)

def handle_window(music : 'audio Music obj') -> bool:
#return whether or not the window was closed
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("~ Window closed.")
            return False
        elif event.type == pygame.VIDEORESIZE:
            setup_window(event.size)
        elif event.type == music.song_ended():
            music.play_next_song()

    return True

def setup_gb(surface, width, height) -> "Graphics Board - list":
    gb = [[0 for x in range(SIZE['columns'])] for y in range(SIZE['rows'])]
    for row in range(SIZE['rows']):
        for col in range(SIZE['columns']):
            gb[row][col] = background_square(width, height, row, col)
    return gb

def color_blocks(game, surface, graphics_board) -> None:
#Colors each individual block on the graphics board
    board = game.get_board()

    #all block colors
    for row in range(SIZE['rows']):
        for col in range(SIZE['columns']):
            if board[row][col] in ['0', '3']:
                pygame.draw.rect(surface, COLOR['WHITE'],
                                 graphics_board[row][col], 0)
            elif board[row][col] == 'P' and game.get_player_info()['health'] >= 1:
                pygame.draw.rect(surface,
                                 COLOR['BLUE' + str(game.get_player_info()['health'])],
                                 graphics_board[row][col], 0)
            elif board[row][col] in ['E', 'e']:
                pygame.draw.rect(surface,
                                 COLOR['RED' + str(game.get_enemy([row,col])['health'])],
                                 graphics_board[row][col], 0)
            elif board[row][col] in ['s', 'S']:
                pygame.draw.rect(surface, COLOR['GREY'],
                                 graphics_board[row][col], 0)
            elif board[row][col] in ['G', 'g']:
                pygame.draw.rect(surface,
                                 COLOR['GREEN' + str(game.get_enemy([row,col])['health'])],
                                 graphics_board[row][col], 0)
            elif board[row][col] in game.get_non_movers():
                pygame.draw.rect(surface,
                                 COLOR['BROWN' + str(game.get_enemy([row,col])['health'])],
                                 graphics_board[row][col], 0)
                

def display_game(game, surface, graphics_board, paused, status, current_menu) -> None:
#Shows the whole game screen
    surface.fill(COLOR['BLACK'])
    color_blocks(game, surface, graphics_board)
                
    if current_menu in ['game', 'paused']:
        game_text(surface, game)
    if current_menu in ['main']:
        main_menu_text(surface)
    if current_menu in ['level select']:
        level_select_text(surface, game)
    if not paused and status == 'continue':
        pygame.display.flip()

def game_movement(game, input_delayer : dict) -> bool:
#Continues movement on all game board pieces
    pause = False
    time = game.get_time()
    
    if (input_delayer['player'] + 7) < time:
        pause = player_input(game)
        input_delayer['player'] = time
    if (input_delayer['shot'] + 6) < time:
        game.move_bullets()
        input_delayer['shot'] = time
    if (input_delayer['E_enemy'] + 20) < time:
##        game.display_board()
##        game.display_data()
##        print('----------------------------------')
        game.move_enemies('E')
        input_delayer['E_enemy'] = time
    if (input_delayer['E_shot'] + 25) < time:
        game.add_enemy_bullets('E')
        input_delayer['E_shot'] = time
    if (input_delayer['G_shot'] + 60) < time:
        game.add_g_bullets()
        input_delayer['G_shot'] = time
        
    game.increment_time()
    return pause

def background_square(width, height, row, col):
#this is the setup for the grid background rectangle locations
    size_x, size_y = ((width // SIZE['columns']), (height // SIZE['rows']))
    decreaser_x = (width // 128)
    decreaser_y = (height // 72)
    x = size_x * row + (decreaser_x // 2)
    y = size_y * col + (decreaser_y // 2)
    size_x -= decreaser_x
    size_y -= decreaser_y
    #print(x,y,size_x,size_y)
    return pygame.Rect(y, x, size_x, size_y)

def player_input(game) -> bool:
#basic inputs to move and shoot with the player or pause game
    player = mechanics

    if pygame.key.get_pressed()[pygame.K_ESCAPE] == 1:
        return True

    #MOVEMENT
    if pygame.key.get_pressed()[pygame.K_w] == 1:   #up
        player.movement_input(game, 'w')
    elif pygame.key.get_pressed()[pygame.K_d] == 1:   #right
        player.movement_input(game, 'd')
    elif pygame.key.get_pressed()[pygame.K_s] == 1:   #down
        player.movement_input(game, 's')
    elif pygame.key.get_pressed()[pygame.K_a] == 1:   #left
        player.movement_input(game, 'a')

    #SHOTS
    if pygame.key.get_pressed()[pygame.K_UP] == 1:      #up
        player.shot_input(game, 'w')
    elif pygame.key.get_pressed()[pygame.K_DOWN] == 1:   #down
        player.shot_input(game, 's')
    elif pygame.key.get_pressed()[pygame.K_RIGHT] == 1:  #right
        player.shot_input(game, 'd')
    elif pygame.key.get_pressed()[pygame.K_LEFT] == 1:   #left
        player.shot_input(game, 'a')

    return False

def setup_text(surface, size : int, text : str, location : tuple) -> None:
#basic setup to put text on the screen
    myfont = pygame.font.SysFont('data/nevis.ttf', size, True)
    textsurface = myfont.render(text , False, COLOR['WHITE'])
    surface.blit(textsurface, location)

def game_text(surface, game):
#Game HUD
    width = surface.get_width()
    height = surface.get_height()

    text_size = width//20
    y = height//36
    
    setup_text(surface, text_size, 'Timer: ' + str(game.get_time() // 60),
              (width//1.3, y))
    setup_text(surface, text_size, 'Health: ' + str(game.get_player_info()['health']),
              (width//1.92, y))
    setup_text(surface, text_size, 'Enemies Remaining: ' + str(len(game.get_enemies_health())),
              (width//64, y))

def pause_menu(surface, game, input_delayer) -> list:
#main control for the pause menu
    audio.startPause()
    #pause_display(surface, game)
    paused = True
    running = True
    menu = 'pause'
    
    while running and paused and menu in ['pause']:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("~ Window closed.")
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
                    menu = 'game'
                elif event.key == pygame.K_r:
                    paused = False
                    menu = 'game'
                    reload_board(game, input_delayer)
                    #requires key access to change value past function
                elif event.key == pygame.K_q:
                    paused = False
                    menu = 'main'
                    
    audio.endPause()                
    return [paused, running, menu]

def pause_display(surface, game) -> None:
#pause menu display
    width = surface.get_width()
    height = surface.get_height()
    size = width//20

    box = pygame.Rect(0, height//4, width, height//2)
    pygame.draw.rect(surface, COLOR['BLACK'], box, 0)

    setup_text(surface, size, 'Continue   Restart     Quit to Menu',
              (size, height//2))
    setup_text(surface, (int)(size//1.43), '[esc]              [r]                 [q] ',
              (2*size, height//2 + height//10.8))
    
    pygame.display.flip()

def get_delayer() -> dict:
#small delay on certain game actions
    return {'shot' : -6, 'player' : -7, 'E_enemy' : -20,
            'E_shot' : -25, 'G_shot' : -60}

def game_over_menu(surface, game, input_delayer, music : 'audio music obj') -> list:
#main control for the game over menu
    audio.playerDeath()
    game_over_display(surface, game)
    status = 'Game Over'
    running = True
    menu = 'game'
    
    while running and status == 'Game Over':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("~ Window closed.")
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reload_board(game, input_delayer)
                    status = 'continue'
                elif event.key == pygame.K_q:
                    menu = 'main'
                    status = 'continue'
            elif event.type == music.song_ended():
                music.play_next_song()
                
    return [status, running, menu]

def game_over_display(surface, game) -> None:
#game over menu display
    width = surface.get_width()
    height = surface.get_height()
    size = width//20

    box = pygame.Rect(0, height//4, width, height//2)
    pygame.draw.rect(surface, COLOR['BLACK'], box, 0)

    setup_text(surface, size, 'Y O U  L O S T:      Restart     Quit',
              (size, height//2))
    setup_text(surface, (int)(size//1.43), '[r]                 [q] ',
              (9*size, height//2 + size))
    
    pygame.display.flip()
    
    
def game_won_menu(surface, game, input_delayer, music : 'audio music obj') -> list:
#main control for the game over menu
    audio.gameWon()
    game_won_display(surface, game)
    status = 'Game Won'
    running = True
    menu = 'game'
    
    while running and status == 'Game Won':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("~ Window closed.")
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reload_board(game, input_delayer)
                    status = 'continue'
                elif event.key == pygame.K_SPACE: #<-----
                    load_next_level(game, input_delayer)
                    status = 'continue'
                elif event.key == pygame.K_q:
                    menu = 'main'
                    status = 'continue'
            elif event.type == music.song_ended():
                music.play_next_song()
                
    return [status, running, menu]

def game_won_display(surface, game) -> None:
#game over menu display
    width = surface.get_width()
    height = surface.get_height()
    size = width//20

    box = pygame.Rect(0, height//4, width, height//2)
    pygame.draw.rect(surface, COLOR['BLACK'], box, 0)
    
    setup_text(surface, size+10, 'L E V E L  C O N Q U E R E D !',
              (size, height//2 - size//.66))
    setup_text(surface, size, 'Next Level     Play Again      Quit',
              (size, height//2))
    setup_text(surface, (int)(size//1.43), '[spacebar]               [r]                       [q] ',
              (size//.66, height//2 + size))
    
    pygame.display.flip()

def check_selection(game, music) -> list:  # -> [current_menu, running]
# return whether or not start game was pressed
    selected = game.get_menu_select()
    game.reset_menu()
    if selected == 1:
        return ['level select', True]
    elif selected == 5:
        return ['main', False]
    return ['main', handle_window(music)]

def reload_board(game, input_delayer) -> None:
#reloads the boards and inputs
    game.reset_board()
    for key in input_delayer.keys():
        input_delayer[key] = 0

def load_next_level(game, input_delayer) -> None:
#increments level and then reloads board
    game.next_level()
    reload_board(game, input_delayer)

def load_prev_level(game, input_delayer) -> None:
#decrements level and then reloads board
    game.prev_level()
    reload_board(game, input_delayer)

def load_menu(game, input_delayer) -> None:
#sets game to the menu level and reloads the board
    game.set_level(0)
    reload_board(game, input_delayer)

def main_menu_text(surface):
    width = surface.get_width()
    height = surface.get_height()
    text_size = width//15
    height_distance = height//9.1

    setup_text(surface, width//13, ' TITLE',            (width//2, height//4 - height//8))
    setup_text(surface, text_size, ' Play Game',        (width//2, height//4))
    #setup_text(surface, text_size, ' User Levels',      (width//2, height//4 + height_distance))
    #setup_text(surface, text_size, ' Create A Level',   (width//2, height//4 + 2*height_distance))
    #setup_text(surface, text_size, ' Settings',         (width//2, height//4 + 3*height_distance))
    setup_text(surface, text_size, ' Exit Game',        (width//2, height//4 + 4*height_distance))

    
    setup_text(surface, text_size//3*2, 'wasd - move | arrow keys - shoot', (width//12, height//4 + 6*height_distance))

#def setup_menu

def current_display(game, surface, graphics_board, paused, status, current_menu, mini_graphics_board) -> None:
    if current_menu in ['level_select']:
        display_game(game, surface, mini_graphics_board, paused, status, current_menu)
    else:
        display_game(game, surface, graphics_board, paused, status, current_menu)

def level_select_text(surface, game) -> None:
#level select text
    width = surface.get_width()
    height = surface.get_height()

    text_size = width//30
    bigger_text = width//30 + 5
    y = height//100    

    setup_text(surface, bigger_text, 'Level Selected: ' + str(game.get_level()),
              (width//64, y))    
    setup_text(surface, bigger_text, 'Press [spacebar] to play!',
              (width//1.92, y))
    
    setup_text(surface, text_size, '(press [<] or [>] to change)',
              (width//64, y+40))    
    setup_text(surface, text_size, 'Press [q] to go back',
              (width//1.92, y+40))

def level_select_input(running, menu, game, input_delayer, music) -> list:
#handles input for level_select menu
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("~ Window closed.")
            running = False
        elif event.type == music.song_ended():
            music.play_next_song()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                menu = 'main'
            elif event.key == pygame.K_LEFT and game.get_level() > 1:
                load_prev_level(game, input_delayer)
                audio.lvlSelect()
            elif event.key == pygame.K_RIGHT and game.get_level() < game.get_level_max():
                load_next_level(game, input_delayer)
                audio.lvlSelect()
            elif event.key == pygame.K_SPACE:
                menu = 'game'
    return [running, menu]

def creator_input(game) -> bool:
#basic inputs to move player and place blocks or pause game
    player = mechanics

    #PAUSE
    if pygame.key.get_pressed()[pygame.K_ESCAPE] == 1:
        return True

    #BLOCK SELECT
    if pygame.key.get_pressed()[pygame.K_1] == 1:
        player.select_input(game, 'E')
    elif pygame.key.get_pressed()[pygame.K_2] == 1:
        player.select_input(game, 'G')
    elif pygame.key.get_pressed()[pygame.K_3] == 1:
        player.select_input(game, 'B')
    elif pygame.key.get_pressed()[pygame.K_4] == 1:
        player.select_input(game, '0')

    #MOVEMENT
    if pygame.key.get_pressed()[pygame.K_w] == 1:   #up
        player.movement_input(game, 'w')
    elif pygame.key.get_pressed()[pygame.K_d] == 1:   #right
        player.movement_input(game, 'd')
    elif pygame.key.get_pressed()[pygame.K_s] == 1:   #down
        player.movement_input(game, 's')
    elif pygame.key.get_pressed()[pygame.K_a] == 1:   #left
        player.movement_input(game, 'a')

    #BLOCK PLACEMENT
    if pygame.key.get_pressed()[pygame.K_UP] == 1:      #up
        player.block_input(game, 'w')
    elif pygame.key.get_pressed()[pygame.K_DOWN] == 1:   #down
        player.block_input(game, 's')
    elif pygame.key.get_pressed()[pygame.K_RIGHT] == 1:  #right
        player.block_input(game, 'd')
    elif pygame.key.get_pressed()[pygame.K_LEFT] == 1:   #left
        player.block_input(game, 'a')

    return False

if __name__ == "__main__":
    run()
