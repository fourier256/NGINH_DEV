import pygame
import sys
from G_Object import G_Object
from G_SpriteModel import G_SpriteModel
from G_TileMap import G_TileMap
import json
import object_db
import animation_db
#import map_decoder


# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 480, 320
FPS = 60
FIXED_DELTA_TIME = 1 / 60  # Fixed update interval

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Initialize screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Template")
clock = pygame.time.Clock()

# Game state
running = True
accumulator = 0  # For fixed update timing

# Init Map
g_object_list = []
g_tile_map = G_TileMap(pygame.image.load("assets/img/tileset.png"), 'assets/map/map_00.json')

def init_tilemap(tile_map_name) :
    g_object_list = []
    g_tile_map = G_TileMap(pygame.image.load("assets/img/tileset.png"), 'assets/map/' + time_map_name + '.json')
    data = json.load(open('assets/map/' + time_map_name + '.json', 'r'))
    for unit in data['g_object']['units'] :
        unit_name = unit['name']
        max_hp = object_db.get_hp(unit_name)
        max_mp = object_db.get_mp(unit_name)
        speed = object_db.get_speed(unit_name)
        image = pygame.image.load(animation_db.get_image(object_db.get_model(unit_name)))
        animation_dict = animation_db.get_animation_dict(object_db.get_model(unit_name))
        model = G_SpriteModel(image, animation_dict)
        g_object_list.append(G_Object(max_hp, max_mp, speed, unit['x_position']*16, unit['y_position']*16, 'd', model))

# Event handlers
def on_draw():
    screen.fill(WHITE)  # Clear screen with white color
    # TODO: Add rendering code here
    g_tile_map.on_draw(screen)
    for g_object in g_object_list: 
        g_object.on_draw(screen)
    pygame.display.flip()

def on_update(delta_time):
    # TODO: Add game logic update code here
    pass

def on_key_down(key):
    if key == pygame.K_ESCAPE:
        pygame.quit()
        sys.exit()
    elif key == pygame.K_UP:
        g_object_list[0].y_position -=16
    elif key == pygame.K_DOWN:
        g_object_list[0].y_position +=16
    elif key == pygame.K_LEFT:
        g_object_list[0].x_position -=16
    elif key == pygame.K_RIGHT:
        g_object_list[0].x_position +=16
        
    # TODO: Add key down logic here

def on_key_up(key):
    # TODO: Add key up logic here
    pass
    #print(key)

def on_mouse_move(pos):
    # TODO: Add mouse movement logic here
    pass
    #print(pos)

def on_mouse_click_left(pos):
    # TODO: Add left mouse click logic here
    pass
    #print(pos)

def on_mouse_click_right(pos):
    # TODO: Add right mouse click logic here
    pass
    #print(pos)




# Main loop
while running:
    frame_time = clock.tick(FPS) / 1000  # Time since last frame in seconds
    accumulator += frame_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            on_key_down(event.key)

        elif event.type == pygame.KEYUP:
            on_key_up(event.key)

        elif event.type == pygame.MOUSEMOTION:
            on_mouse_move(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                on_mouse_click_left(event.pos)
            elif event.button == 3:  # Right click
                on_mouse_click_right(event.pos)

    # Fixed update loop
    while accumulator >= FIXED_DELTA_TIME:
        on_update(FIXED_DELTA_TIME)
        accumulator -= FIXED_DELTA_TIME

    on_draw()

# Quit pygame
pygame.quit()
