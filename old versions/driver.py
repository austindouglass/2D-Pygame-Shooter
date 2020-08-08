# Name: Austin Douglass
# 8/20/18
# 
# Project Z

import pygame

COLOR = {
    'BLUE' : [93, 173, 226], 'RED' : [231, 76, 60], 'BLACK' : [0, 0, 0]
    }
 
def run():     
    # initialize the pygame module
    pygame.init()
     
    # controls the main loop
    running = True
    window((1280, 720))
    clock = pygame.time.Clock()
    game_timer = 0
    input_delayer = {'shot' : -4, 'dash' : -100, 'mouse' : -10}
    surface = pygame.display.get_surface()
    player = ObjectGraphics({'shadow' : player_shadow_dimensions, 'coords' : player_dimensions},
                            surface.get_width(), surface.get_height())
    enemies = []
    pygame.key.set_repeat(1,50)
     
    # main loop
    while running:
        clock.tick(60)        
        surface.fill(pygame.Color(255, 255, 255))
        # event handling, gets all event from the eventqueue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("~ Window closed.")
                running = False
                pygame.quit()
                return
            elif event.type == pygame.VIDEORESIZE:
                window(event.size)
                player.resize(surface.get_width(), surface.get_height())

        input_delayer = inputs(player, input_delayer, game_timer, surface)

        if pygame.mouse.get_pressed()[2] == 1 and (input_delayer['mouse'] + 10) < game_timer:
            x, y = pygame.mouse.get_pos()
            enemies.append(ObjectGraphics({'shadow' : enemy_dimensions, 'coords' : enemy_dimensions}, x, y))
            input_delayer['mouse'] = game_timer
                
##        if pygame.mouse.get_pressed()[0] == 1 and (input_delayer + 3) < game_timer:  # 1 is left mouse button
##            player.add_shot_mouse(pygame.mouse.get_pos())
##            input_delayer = game_timer

        for enemy in enemies:
            enemy.draw_circle(surface)
        
        player.draw_shots(surface)
        player.draw_square(surface)
        pygame.display.flip()
        game_timer += 1
##        if game_timer % 60 == 0:
##            print(game_timer/60)

def window(size: tuple):
    #logo = pygame.image.load("logo32x32.png")
    #pygame.display.set_icon(logo)
    pygame.display.set_caption("Project Z :)")
    pygame.display.set_mode(size, pygame.RESIZABLE)

def inputs(player, input_delayer, game_timer, surface):
    # movement
    y_movement = int(surface.get_height()/144)
    x_movement = int(surface.get_width()/256)
    
    if pygame.key.get_pressed()[pygame.K_LSHIFT] == 1 and (input_delayer['dash'] + 100) < game_timer:
        dash = 30
        input_delayer['dash'] = game_timer
    else:
        dash = 1
        
    if pygame.key.get_pressed()[pygame.K_w] == 1:   #up
        player.move_square(surface, 0, -y_movement*dash)
    if pygame.key.get_pressed()[pygame.K_d] == 1:   #right
        player.move_square(surface, x_movement*dash, 0)
    if pygame.key.get_pressed()[pygame.K_s] == 1:   #down
        player.move_square(surface, 0, y_movement*dash)
    if pygame.key.get_pressed()[pygame.K_a] == 1:   #left
        player.move_square(surface, -x_movement*dash, 0)    

    # shots (10 for starting window)
    speed = (x_movement + y_movement)*2

    if (input_delayer['shot'] + 4) < game_timer:
        if pygame.key.get_pressed()[pygame.K_UP] == 1:      #up
            if pygame.key.get_pressed()[pygame.K_RIGHT] == 1:
                player.add_shot((speed, -speed))
            elif pygame.key.get_pressed()[pygame.K_LEFT] == 1:
                player.add_shot((-speed, -speed))
            else:
                player.add_shot((0, -speed))
        elif pygame.key.get_pressed()[pygame.K_DOWN] == 1:   #down
            if pygame.key.get_pressed()[pygame.K_RIGHT] == 1:
                player.add_shot((speed, speed))
            elif pygame.key.get_pressed()[pygame.K_LEFT] == 1:
                player.add_shot((-speed, speed))
            else:
                player.add_shot((0, speed))
        elif pygame.key.get_pressed()[pygame.K_RIGHT] == 1:  #right
            player.add_shot((speed, 0))
        elif pygame.key.get_pressed()[pygame.K_LEFT] == 1:   #left
            player.add_shot((-speed, 0))
        input_delayer['shot'] = game_timer
    return input_delayer

def player_shadow_dimensions(width, height):
    return {'x' : int(width/2), 'y' : int(height/2), 'size_x' : int(width/32), 'size_y' : int(height/18)}

def player_dimensions(width, height):
    return {'x' : int(width/2 + (int(width/32) - int(width/42))/2),
                'y' : int(height/2 + (int(height/18) - int(height/24))/2),
                    'size_x' : int(width/42), 'size_y' : int(height/24)}

def enemy_dimensions(x, y):
    return {'x' : x, 'y' : y}
    

class ObjectGraphics:
    def __init__(self, f, width, height):
        self.functions = f
        self.shadow = self.functions['shadow'](width, height)   # Coordinates of shadow
        self.coords = self.functions['coords'](width, height)   # Coordinates of center
        #print(self.coords['x'], self.coords['y'])
        self.current_bullets = []

    def resize(self, width, height):
        self.shadow = self.functions['shadow'](width, height)
        self.coords = self.functions['coords'](width, height)

    def move_square(self, surface, horizontal, vertical):
        width = surface.get_width()
        height = surface.get_height()

        if (width > self.shadow['x']+horizontal+self.shadow['size_x']
            and height > self.shadow['y']+vertical+self.shadow['size_y']
            and self.shadow['x']+horizontal > 0 and self.shadow['y']+vertical > 0):
            self.shadow['x']+=horizontal
            self.shadow['y']+=vertical
            self.coords['x']+=horizontal
            self.coords['y']+=vertical        
        
    def draw_square(self, surface):
        pygame.draw.rect(
            surface, pygame.Color(0, 0, 0),
                pygame.Rect(self.shadow['x'], self.shadow['y'], self.shadow['size_x'], self.shadow['size_y']), 0)        
        pygame.draw.rect(
            surface, pygame.Color(COLOR['BLUE'][0], COLOR['BLUE'][1], COLOR['BLUE'][2]),
                pygame.Rect(self.coords['x'], self.coords['y'], self.coords['size_x'], self.coords['size_y']), 0)

    def draw_circle(self, surface):
        pygame.draw.circle(surface, COLOR['BLACK'], (self.coords['x'], self.coords['y']), 13)
        pygame.draw.circle(surface, COLOR['RED'], (self.coords['x'], self.coords['y']), 10)

    def add_shot_mouse(self, target: tuple):
        location = [self.coords['x']+15, self.coords['y']+15]
        self.current_bullets.append([location, target, tuple(location)]) #last location saves original to memory
        #print(location, target)

    def add_shot(self, direction: (int, int)):
        location = [self.coords['x']+10, self.coords['y']+10]
        self.current_bullets.append([location, direction])

    def draw_shots(self, surface):
        remove_bullets = []
        
        for bullet in self.current_bullets:            
            #add movement to bullet
            bullet[0][0] += bullet[1][0]
            bullet[0][1] += bullet[1][1]
            
            #remove offscreen bullets
            if (surface.get_width() < bullet[0][0] and surface.get_height() < bullet[0][1]
                and bullet[0][0] < 0 and bullet[0][1] < 0):
                remove_bullets.append(bullet)                
            else:           #draw bullet
                pygame.draw.rect(surface, pygame.Color(0, 0, 0),
                                 pygame.Rect(bullet[0][0], bullet[0][1], int(surface.get_width()/128), int(surface.get_height()/72)), 0)    


if __name__=="__main__":
    run()
