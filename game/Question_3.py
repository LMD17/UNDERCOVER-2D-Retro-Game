
# imports
import pygame
from pygame import mixer
import random
import sprite_sheet
import csv

# initialize mixer and pygame
mixer.init()
pygame.init()

# define screen width and height
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

# set display mode
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# set display caption
pygame.display.set_caption('UNDERCOVER')

# set frame rate
clock = pygame.time.Clock()
FPS = 60

# define game variables
GRAVITY = 0.75
SCROLL_THRESH = 200 # pixels (threshold is the distance the agent can get to the end of the screen before it starts scrolling(we want the screen to start scrolling before we get to the end of the screen))
ROWS = 16
COLUMNS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS # screen is a grid and we are calculating how many tiles there are in the screen
TILE_TYPES = 21
MAX_LEVELS = 4

screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False
restart = "none"    # variable to determine if level or game is restarted
controls = False    


# load music and sounds
pygame.mixer.music.stop()   # stop menu music
pygame.mixer.music.load("game/audio/music_menu.mp3")
pygame.mixer.music.play(-1, 0.0, 5000)
pygame.mixer.music.set_volume(0.3)


jump_fx = pygame.mixer.Sound('game/audio/jump.wav')
jump_fx.set_volume(0.15) # reduce volume
shot_fx = pygame.mixer.Sound('game/audio/shot.wav')
shot_fx.set_volume(0.15) # reduce volume
reload_fx = pygame.mixer.Sound('game/audio/reload.wav')
reload_fx.set_volume(0.5) # reduce volume
hurt_fx = pygame.mixer.Sound('game/audio/hurt.wav')
hurt_fx.set_volume(0.5) # reduce volume


# load images

# button images
start_img = pygame.image.load('game/image/start_btn.png').convert_alpha()
exit_img = pygame.image.load('game/image/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('game/image/restart_btn.png').convert_alpha()

# load background images
pine1_img = pygame.image.load('game/image/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('game/image/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('game/image/background/mountain.png').convert_alpha()
sky_img = pygame.image.load('game/image/background/sky_cloud.png').convert_alpha()

# store tiles in a list
img_list = []
for i in range(TILE_TYPES):
    img = pygame.image.load(f'game/image/tile/{i}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
    
bullet_img = pygame.image.load('game/image/icons/bullet.png').convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (bullet_img.get_width() * 0.8, bullet_img.get_height() * 0.8))	# scale the image

# load agent images
all_agent_images = []
idle_img = pygame.image.load('game/image/spritesheets/Gangsters_1/Idle.png').convert_alpha()
run_img = pygame.image.load('game/image/spritesheets/Gangsters_1/Run.png').convert_alpha()
jump_img = pygame.image.load('game/image/spritesheets/Gangsters_1/Jump.png').convert_alpha()
death_img = pygame.image.load('game/image/spritesheets/Gangsters_1/Death.png').convert_alpha()
reload_img = pygame.image.load('game/image/spritesheets/Gangsters_1/Reload.png').convert_alpha()
hurt_img = pygame.image.load('game/image/spritesheets/Gangsters_1/Hurt.png').convert_alpha()
# add all agent images to agent list
all_agent_images.append(idle_img) 
all_agent_images.append(run_img) 
all_agent_images.append(jump_img) 
all_agent_images.append(death_img) 
all_agent_images.append(reload_img) 
all_agent_images.append(hurt_img) 

# load villain images
all_villain_images = []
idle_img = pygame.image.load('game/image/spritesheets/Gangsters_3/Idle_3.png').convert_alpha()
run_img = pygame.image.load('game/image/spritesheets/Gangsters_3/Run.png').convert_alpha()
jump_img = pygame.image.load('game/image/spritesheets/Gangsters_3/Jump.png').convert_alpha()
death_img = pygame.image.load('game/image/spritesheets/Gangsters_3/Death.png').convert_alpha()
reload_img = pygame.image.load('game/image/spritesheets/Gangsters_3/Reload.png').convert_alpha()
hurt_img = pygame.image.load('game/image/spritesheets/Gangsters_3/Hurt_2.png').convert_alpha()
# add all villain images to agent list
all_villain_images.append(idle_img) 
all_villain_images.append(run_img) 
all_villain_images.append(jump_img) 
all_villain_images.append(death_img) 
all_villain_images.append(reload_img) 
all_villain_images.append(hurt_img) 

# load agent images
all_agent_brother_images = []
idle_img = pygame.image.load('game/image/spritesheets/Gangsters_2/Idle_2.png').convert_alpha()
walk_img = pygame.image.load('game/image/spritesheets/Gangsters_2/Walk.png').convert_alpha()
# add all agent images to agent list
all_agent_brother_images.append(idle_img) 
all_agent_brother_images.append(walk_img) 


# load pickup boxes
health_box_img = pygame.image.load('game/image/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('game/image/icons/ammo_box.png').convert_alpha()

item_boxes = {
    "health"    : health_box_img,
    'ammo'      : ammo_box_img
}

# define colours
BG = (82, 84, 82)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
PINK = (235, 65, 54)
GOLD = (168, 131, 50)

# define font
font_small = pygame.font.SysFont('Futura', 30)
font_extra_big = pygame.font.SysFont('Futura', 80)    # define unique font
font_big = pygame.font.SysFont('Futura', 60)    # define unique font

#  funciton to draw text
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

# Function to draw background
def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width() # we use sky_img width because it is the shortest width and we want to keep everything uniform
    # loop over images so that they appear after eachother so that it looks like our background is continuous
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))       #(x = width multiplied by x to repeat image)(bg_scroll multiplied by scale to move image at speed according to its distance from the agent)
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 100))    
        screen.blit(mountain_img, ((x * width) - 100 - bg_scroll * 0.7, SCREEN_HEIGHT - mountain_img.get_height() - 0))
    
# Function to reset level
def reset_level():
    # empty all groups
    villain_group.empty()
    agent_brother_group.empty()
    bullet_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()
    
    # create empty tile list
    data = []
    # populate list with default values
    for _ in range(ROWS):
        row = [-1] * COLUMNS
        data.append(row)
    
    return data

class Character(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo_amount):
        pygame.sprite.Sprite.__init__(self) # inherit some functionality from Sprite class
        self.alive = True
        self.char_type = char_type
        self.scale = scale
        self.speed = speed
        self.ammo = ammo_amount
        self.start_ammo = ammo_amount
        self.max_ammo = 20
        
        # define player action variables
        self.moving_left = False
        self.moving_right = False
        self.shot = False
        
        self.shoot_cooldown = 0
        self.reload_cooldown = 0
        
        self.health = 100
        self.max_health = self.health
        
        self.direction = 1 # which way is he facing (1 means looking to the right)
        self.vel_y = 0
        self.jump = False
        self.reload = False
        self.in_air = True
        self.flip = False
        
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.last_update = pygame.time.get_ticks() # get time
        
        
        # AI specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 10)    # increase x for character (villain) to see further away
        self.idling = False
        self.idling_counter = 0
        
        #load all images for players
        # ['Idle', 'Run', 'Jump', 'Death', 'Shot', 'Hurt']
        agent_animation_steps = [6, 10, 2, 5, 4, 5]
        villain_animation_steps = [2, 10, 10, 5, 12, 3]
        agent_brother_animation_steps = [13, 10]
        
        if self.char_type == "agent":
            # loop through Character animation types
            for i in range(len(agent_animation_steps)):
                sheet = sprite_sheet.SpriteSheet(all_agent_images[i])
                # reset temporary list of images
                temporary_image_list = []
                # loop through images in each sprite
                for step in range(agent_animation_steps[i]):
                    # If jump then we need to increase height
                    temporary_image_list.append(sheet.get_image(step, 128, 72, self.scale, BLACK))    # append images to temporary list
                self.animation_list.append(temporary_image_list)    # append temporary list to animation list which contains all animations
        elif self.char_type == "villain":
            # loop through Character animation types
            for i in range(len(villain_animation_steps)):
                sheet = sprite_sheet.SpriteSheet(all_villain_images[i])
                # reset temporary list of images
                temporary_image_list = []
                # loop through images in each sprite
                for step in range(villain_animation_steps[i]):
                    
                    
                    # If jump then we need to increase height
                    temporary_image_list.append(sheet.get_image(step, 128, 72, self.scale, BLACK))    # append images to temporary list
                self.animation_list.append(temporary_image_list)    # append temporary list to animation list which contains all animations
        else:
            # loop through Character animation types
            for i in range(len(agent_brother_animation_steps)):
                sheet = sprite_sheet.SpriteSheet(all_agent_brother_images[i])
                # reset temporary list of images
                temporary_image_list = []
                # loop through images in each sprite
                for step in range(agent_brother_animation_steps[i]):
                    # If jump then we need to increase height
                    temporary_image_list.append(sheet.get_image(step, 128, 128, self.scale, BLACK))    # append images to temporary list
                self.animation_list.append(temporary_image_list)    # append temporary list to animation list which contains all animations

        self.image = self.animation_list[self.action][self.frame_index] # get first action on first frame (which is the first idle image)
        self.main_rect = self.image.get_rect()   # takes size of img and creates boundry box around it. This rectangle is what we use to control the position and used for collisions
        self.main_rect.center = (x, y) # position rectanlge
        self.rect = pygame.Rect(0, 0, 30, self.image.get_height())  # second rectangle for collisions
        self.width = self.rect.width
        self.height = self.rect.height
        
       
    # update runs all the subchecks
    def update(self):
        self.update_animation()
        self.check_alive()
        self.update_cooldown()
        self.rect.center = (self.main_rect.centerx, self.main_rect.centery) # position collision rectanlge in middle of image ractangle
        
    
    # update colldown
    def update_cooldown(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.reload_cooldown > 0:
            self.reload_cooldown -= 1
    
    # Move method
    def move(self):
        # reset movement variables
        screen_scroll = 0
        dx = 0  # delta x means change in x
        dy = 0  # delta y means change in y
        
        
        # assign movement variables if moving left or right
        if self.moving_left:
            dx = -self.speed # negative because we are moving in the left direction (x-axis decreases to the left)
            self.flip = True
            self.direction = -1
        if self.moving_right:
            dx = self.speed # moving to the right x increases
            self.flip = False
            self.direction = 1
            
        
            
        # Jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -12    # negative becuase y coordinate starts at 0 at top of screen and then increases as you go down
            self.jump = False
            self.in_air = True
            
        # apply gravity
        self.vel_y += GRAVITY # add gravity because y-axis increases going down
        if self.vel_y > 11:
            self.vel_y # this will keep self.vel_y at 11
        dy += self.vel_y
        
        # check for collision
        for tile in world.obstacle_list:
            
            
            # check collision in x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0  # if collision occurs, then we dont want to make the movement and we reset dx
                # if the ai has hit the wall then turn around
                if self.char_type == 'villain' or self.char_type == 'brother':
                    self.direction *= -1    # change direction
                    self.move_counter = 0
            # check fo collision in y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height): 
                # check if below the ground, i.e. jumping
                if self.vel_y < 0:  # means that character is moving up and if colides while jumping that means character has hit head on somthing
                    self.vel_y = 0 # stop moving up (jumping)
                    dy = tile[1].bottom - self.rect.top # bottom of ground that character hit head on minus characters top (head) so character can basically jump between the ground below and ground above
                # check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False # when character hits the ground, no longer in air
                    dy = tile[1].top - self.rect.bottom - 0.75 # top of ground that character hit feet on minus characters bottom (feet) 
        
        # check for agent collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0 # agent dead
        # check for agent collision with exit sign
        level_complete = False            
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True      # player has completed the game  
        # check for agent collision with agent's brother
        game_complete = False     
        if self.char_type == "agent":   # check if agent collided with agent_brother
            if pygame.sprite.spritecollide(self, agent_brother_group, False):
                game_complete = True    # player has completed the game       
                agent.health = 0    # game ends 
        # check for agent fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0 # agent dead
        
        # check if agent going off the edges of the screen
        if self.char_type == "agent":   
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0  # stop agent from going oof the edge of the world/screen
        
        # update rectangle position
        self.main_rect.x += dx
        self.main_rect.y += dy
        
        # update scroll baseed on agent position
        if self.char_type == "agent":   # only scroll according to agent not villain
            if (self.main_rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH) \
                or (self.main_rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):    # check if agent is close to edge of screen on right or left of screeen (world.level_length gives indices or number of tiles there are in a lvel so we multiply by tile size to get pixels) ("bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH" = is calculating the end of the level to stop scrolling with how many tiles there are minus SCREEN_WIDTH to account for the screen width)
                self.main_rect.x -= dx   # agent must stay in this position and background (or screen) must move
                screen_scroll = -dx # screen must move in opposite direction of agent movement (hence the negative)
                
        return screen_scroll, level_complete, game_complete    # return local variable screen_scroll and level_complete
    
    # Create bullets and add them to the bullet_group
    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20    # time until another bullet can be shot (cooldown time)
            if self.char_type == "agent":
                bullet = Bullet(self.rect.centerx + (0.55 * self.rect.size[0] * self.direction), self.rect.centery - (0.05 * self.rect.size[1]), self.direction, self.char_type) # create instance of bullet (we add character width to x coordinate then multiply by 0.55 so that bullet is not too far ahead of player then multiply by character.direction to make the bullet appear infront of the character whichever direction the character may be facing) (Add to the y coordinate so that the bullet comes out of the gun)
            else:
                bullet = Bullet(self.rect.centerx + (0.55 * self.rect.size[0] * self.direction), self.rect.centery - (0.25 * self.rect.size[1]), self.direction, self.char_type) # create instance of bullet (we add character width to x coordinate then multiply by 0.55 so that bullet is not too far ahead of player then multiply by character.direction to make the bullet appear infront of the character whichever direction the character may be facing) (Add to the y coordinate so that the bullet comes out of the gun)
            bullet_group.add(bullet)  # add bullet to bullet_group
            self.ammo -= 1  # reduce ammo
            shot_fx.play() # play shot sound
            
    def reload_ammo(self):
        if self.reload_cooldown == 0 and self.ammo < self.start_ammo:
            self.reload_cooldown = 20    # time until another bullet can be reloaded (cooldown time)
            self.ammo += 1
            self.update_action(4) # 4 is reload
            reload_fx.play()
            
    # AI for villain movement and shooting
    def ai(self):
        # check if villain and agent are alive
        if self.alive and agent.alive:
            
            # randomly get character to idle (this is so that all villains aren't moving in unison)
            if self.idling == False and random.randint(1, 200) == 1:
                self.idling = True
                self.update_action(0)   # 0: idle action
                self.idling_counter = 50
                self.vision.center = (self.rect.centerx + 100 * self.direction, self.rect.centery - 5) # center to align vision with character, then add 100 to put vision completely in front of character because we centered on x axis (multiply by direction so that vision is in front of character)
                
                
            # check if the ai can see the agent
            if self.vision.colliderect(agent.rect):
                # stop running and face agent
                self.update_action(0) # 0: idle action
                # only villains can shoot not the agent's brother
                if self.char_type == "villain":
                    # shoot at agent
                    self.shoot()
                
                self.vision.center = (self.rect.centerx + 100 * self.direction, self.rect.centery -5 ) # center to align vision with character, then add 100 to put vision completely in front of character because we centered on x axis (multiply by direction so that vision is in front of character)
                    
            else:   # cant see agent
                if self.idling == False:
                    if self.direction == 1:
                        self.moving_right = True
                    else:
                        self.moving_right = False
                    self.moving_left = not self.moving_right
                    self.move()
                    self.update_action(1)   # character run
                    # move counter determines how character moves from left to right
                    self.move_counter += 1
                    
                    self.vision.center = (self.rect.centerx + 100 * self.direction, self.rect.centery - 5) # center to align vision with character, then add 100 to put vision completely in front of character because we centered on x axis (multiply by direction so that vision is in front of character)
                                       
                    if self.move_counter > TILE_SIZE:   # tile size used to get character to walk one tile
                        self.direction *= -1    # change direction
                        self.move_counter *= -1 # walk all the way to the other side
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        
        # scroll (shift x coordinates over by screen scroll)
        self.main_rect.x += screen_scroll
            
    
    # to do animation we just flick through the images quickly
    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100    # using this as a timer
        # update imgae depending on current frame
        self.image = self.animation_list[self.action][self.frame_index] # get first frame of current action
        # check if enough time has passed since the last update
        if (pygame.time.get_ticks() - self.last_update) > ANIMATION_COOLDOWN:
            self.last_update = pygame.time.get_ticks()  # update the last_update time
            self.frame_index += 1   # increment frame index
        # if the animation has run out then reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            # check if character has died
            if self.action == 3:    # 3 is the death animation
                self.frame_index = len(self.animation_list[self.action]) - 1  # set final character pose to final image of death animation
            elif self.action == 5:  # check if character has been shot and is hurt
                self.update_action(0)   # reset action to idle
            else: # the animation should loop as normal
                self.frame_index = 0   # resetn frame index back to 0 to start looping through action again
            
    # change the action (idle, run, etc)
    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.last_update = pygame.time.get_ticks()
    
    # check if character is alive
    def check_alive(self):
        # check if character has 0 or less health and is in the screen
        if self.char_type == "brother":
            return
        if self.health <= 0 and self.rect.right > 0 and self.rect.left < SCREEN_WIDTH:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)   # run character death animation
            
    
    # draw image onto the screen
    def draw(self):
        # draw image onto the screen
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.main_rect)  # (image, location)
        # pygame.draw.rect(screen, RED, self.main_rect, 1)
        # pygame.draw.rect(screen, GREEN, self.rect, 1)


# Worl class manages world assets
class World():
    def __init__(self):
        self.obstacle_list = []
        
    def process_data(self, data):
        # how many tiles going right do we have in any given row (this gives how long the level is)
        self.level_length = len(data[0])   # get length of data (data is a list of lists with all columns same length so we just take index 0 to get length)
        # iterate through each value in level data file
        for  y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]  # fetch relevant tile from img_list (each image has a file name that is a number)
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE

                    tile_data = (img, img_rect) # store in tuple
                    
                    # first 9 blocks are dirt blocks
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)    # append to obstacle list
                    # water blocks
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)  # add villain to villain group
                    # decoration blocks
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)  # add villain to villain group
                    # create an agent
                    elif tile == 15:
                        agent = Character('agent', x * TILE_SIZE, y * TILE_SIZE, 0.8, 5, 20)
                        health_bar = HealthBar(105, 10, agent.health, agent.max_health)
                    # create an villain
                    elif tile == 16:
                        villain = Character('villain', x * TILE_SIZE, y * TILE_SIZE, 0.8, 2, 20)
                        villain_group.add(villain)  # add villain to villain group
                    # create ammo box
                    elif tile == 17:
                        item_box = ItemBox("ammo", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)  # add villain to villain group
                    # create ammo box
                    elif tile == 18:
                        agent_brother = Character('brother', x * TILE_SIZE, y * TILE_SIZE, 0.8, 1, 0)
                        agent_brother_group.add(agent_brother)
                    # create health box
                    elif tile == 19:
                        item_box = ItemBox("health", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)  # add villain to villain group
                    # create exit
                    elif tile == 20:
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)  # add villain to villain group
                    
        return agent, health_bar    # return these so that they can be accessed outside of the world class
    
    def draw(self):
        for tile in self.obstacle_list:
            # change x value of rectangles
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])   # tile[0] is img in the tuple and tile[1] is rect in the tuple (defined in prcocess data method above)
                        



class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE //2, y + (TILE_SIZE - self.image.get_height())) # (x = middle of tile, y = on tile)
    
    # scroll (shift x coordinates over by screen scroll)
    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE //2, y + (TILE_SIZE - self.image.get_height())) # (x = middle of tile, y = on tile)
        
    # scroll (shift x coordinates over by screen scroll)
    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height())) # (x = middle of tile, y = on tile)
        
    # scroll (shift x coordinates over by screen scroll)
    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
        
    def update(self):
        # scroll (shift x coordinates over by screen scroll)
        self.rect.x += screen_scroll
        # check if the agent has picked up the box
        if pygame.sprite.collide_rect(self, agent):
            # check item box type
            if self.item_type == "health":
                agent.health += 25
                # agent can not have more than max health
                if agent.health > agent.max_health:
                    agent.health  = agent.max_health
            elif self.item_type == "ammo":
                agent.ammo += 10
                # agent can not have more than max health
                if agent.ammo > agent.max_ammo:
                    agent.ammo  = agent.max_ammo
                
            # delete item box
            self.kill()

# Class to handle health bar
class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
    
    # draw health bar
    def draw(self, health):
        # update with new health
        self.health = health
        # calculate health ration
        ratio = self.health / self.max_health
        
        # draw health bar
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y + 18, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y + 20, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y + 20, 150 * ratio, 20))

# Class to handle a bullet
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, shooter):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.shooter = shooter  # used to determine who is shooting
        
    def update(self):
        # move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        # check if bullet is off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill() # delete bullet instance
            
        # check for collision with ground
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill() # kill bullet
            
        # Check for all villains
        for villain in villain_group:
            if pygame.sprite.spritecollide(villain, bullet_group, False) and self.shooter != "villain":
                if villain.alive:
                    villain.health -= 25 # reduce health
                    self.kill() # delete bullet instance
        
        # check collision with agent
        if pygame.sprite.spritecollide(agent, bullet_group, False) and self.shooter != "agent":
            if agent.alive:
                agent.health -= 5  # reduce health
                self.kill() # delete bullet instance

# Class to handle screen fades
class ScreenFade():
    def __init__(self, direction, color, speed):
         self.direction = direction
         self.color = color
         self.speed = speed
         self.fade_counter = 0
         
    # function to handle fade
    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        
        if self.direction == 1: # whole screen fade
            draw_text(f"LEVEL: {level}", font_small, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.color, (0, SCREEN_WIDTH // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        if self.direction == 2:    # vertical screen fade down (death and victory fade)
            pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.direction == 3:
            pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.color, (0, SCREEN_WIDTH // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            
        if self.fade_counter >= SCREEN_WIDTH: # using screen width constant because we know that the fade will be complete at this length as screen width is greater than screen hegith (this is so that wether we do a fade from the top or bottom, the fade will be correct)
            fade_complete = True
        
        return fade_complete    # return 
    
# create screen fades
intro_fade = ScreenFade(1, BLACK, 5)
death_fade = ScreenFade(2, PINK, 5)
victory_fade = ScreenFade(3, BLACK, 5)

# create sprite groups
agent_brother_group = pygame.sprite.Group()    # group villains together
villain_group = pygame.sprite.Group()    # group villains together
bullet_group = pygame.sprite.Group()    # group bullets together
item_box_group = pygame.sprite.Group()    # group bullets together
water_group = pygame.sprite.Group()    # group bullets together
decoration_group = pygame.sprite.Group()    # group bullets together
exit_group = pygame.sprite.Group()    # group bullets together

# declare movement and control variables
movement = None

# create empty tile list
world_data = []
# populate list with default values
for r in range(ROWS):
    row = [-1] * COLUMNS
    world_data.append(row)
    
# load in level data and create world
with open(f'game/level/level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World() # create World
agent, health_bar = world.process_data(world_data)  # get agent and healthbar

# game loop
run = True  
while run:
    
    # set clock tick to FPS
    clock.tick(FPS)
    
    # display controls            
    if controls:
        pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) # cover screen with gold rectangle
        draw_text(f"CONTROLS", font_extra_big, WHITE, SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2 - 275)
        draw_text(f"W = jump", font_big, WHITE, SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2 - 175)
        draw_text(f"D = move right", font_big, WHITE, SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2 - 75)
        draw_text(f"A = move left", font_big, WHITE, SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2 + 25)
        draw_text(f"R = reload", font_big, WHITE, SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2 + 125)
        draw_text(f"SPACE = shoot", font_big, WHITE, SCREEN_WIDTH//2-150, SCREEN_HEIGHT//2 + 225)

    # game has not started
    elif start_game == False:
        # draw menu
        screen.fill(BG) # fill screen
        
        draw_text(f"UNDERCOVER", font_extra_big, WHITE, SCREEN_WIDTH//2-200, SCREEN_HEIGHT//2 - 270)
        draw_text(f"__WELCOME__", font_extra_big, WHITE, SCREEN_WIDTH//2-210, SCREEN_HEIGHT//2 - 200)
        draw_text(f"YOUR MISSION", font_big, WHITE, SCREEN_WIDTH//2-160, SCREEN_HEIGHT//2-50)
        draw_text(f"You are an undercover agent your _mission_", font_small, WHITE, SCREEN_WIDTH//2-220, SCREEN_HEIGHT//2)
        draw_text(f"RESCUE YOUR BROTHER!", font_small, WHITE, SCREEN_WIDTH//2-120, SCREEN_HEIGHT//2+30)
        draw_text(f"Press 'B' to BEGIN your MISSION", font_big, WHITE, SCREEN_WIDTH//2-320, SCREEN_HEIGHT//2 + 150)
        draw_text(f"Press 'ESC' to exit the game", font_big, WHITE, SCREEN_WIDTH//2-270, SCREEN_HEIGHT//2 + 220)
        
    else:   # game has started
        # update background
        draw_bg()   # update background each iteration so that movement doesnt create a trail
        
        # draw world map
        world.draw()
        
        # draw agent health
        draw_text(f'LEVEL: {level}', font_small, WHITE, 10, 10)  # draw health text
        draw_text('HEALTH:', font_small, WHITE, 10, 30)  # draw health text
        health_bar.draw(agent.health)   # draw health bar
        # draw ammo
        draw_text('AMMO: ', font_small, WHITE, 10, 50)    # draw ammo text
        
        # draw Controls on top right of screen
        draw_text(f"RESTART: 'S'", font_small, WHITE, SCREEN_WIDTH-130, 10)  # draw restart control text
        draw_text("EXIT: 'ESC'", font_small, WHITE, SCREEN_WIDTH-115, 30)  # draw exit control text
        for x in range(agent.ammo):
            screen.blit(bullet_img, (90 + (x * 10), 55)) # as x increases the bullets get drawn further to the side
        
        agent.update() # update agent
        agent.draw()   # draw agent
        
        
        # for all villains
        for villain in villain_group:
            villain.ai() # ai movement
            villain.update() # update
            villain.draw() # draw
        
        # for agent
        for agent_brother in agent_brother_group:
            agent_brother.ai() # ai movement
            agent_brother.update() # update
            agent_brother.draw() # draw
        
        
        # update and draw groups
        bullet_group.update()
        item_box_group.update()
        water_group.update()
        decoration_group.update()
        exit_group.update()
        bullet_group.draw(screen)
        item_box_group.draw(screen)
        water_group.draw(screen)
        decoration_group.draw(screen)
        exit_group.draw(screen)
        
        # show intro
        if start_intro == True:
            
            if intro_fade.fade():   # check if fade is complete
                start_intro = False # if fade is complete start_intro becomes false
                intro_fade.fade_counter = 0 # reset fade counter so that intro_fade can be run from scratch again if needed
                
        # update player actions
        if agent.alive:
            if agent.shot:   # shoot bullets
                agent.shoot()
            if agent.in_air:
                agent.update_action(2) # 2 is jump
            elif agent.moving_left or agent.moving_right:
                agent.update_action(1) # 1 is run
            elif agent.reload and agent.ammo < agent.start_ammo:
                agent.reload_ammo()
            else:
                agent.update_action(0) # 0 is idle
            
            screen_scroll, level_complete, game_complete = agent.move()    # move agent
            bg_scroll -= screen_scroll  # keep track of how far screen has scrolled cumulatively 
            
            # check if player has completed the level
            if level_complete:
                start_intro = True  # start_intro on each next level screen
                level += 1
                bg_scroll = 0   # bg_scroll is the total amount of scrolling done in the game
                world_data = reset_level()  # get world data from reset_level
                if level <= MAX_LEVELS:
                    # load in level data and create world
                    with open(f'game/level/level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World() # create World
                    agent, health_bar = world.process_data(world_data)  # get agent and healthbar
             
        elif game_complete: # check if player completed the game
            pygame.draw.rect(screen, GOLD, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)) # cover screen with gold rectangle
            if victory_fade.fade():
                draw_text(f"CONGRATULATIONS", font_extra_big, WHITE, SCREEN_WIDTH//2-275, SCREEN_HEIGHT//2 - 220)
                draw_text(f"VICTORY", font_extra_big, WHITE, SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2 - 170)
                draw_text(f"!!!", font_extra_big, WHITE, SCREEN_WIDTH//2-10, SCREEN_HEIGHT//2 - 120)
                draw_text(f"Press 'S' to restart the GAME", font_big, WHITE, SCREEN_WIDTH//2-275, SCREEN_HEIGHT//2)
                draw_text(f"Press 'ESC' to exit the GAME", font_big, WHITE, SCREEN_WIDTH//2-272, SCREEN_HEIGHT//2 + 100)
                restart = "game"    # game is completed and if user selects to restart then the game is restarted
        
        else: # player not alive
            screen_scroll = 0   # when a player dies, reset to 0 (screen_scroll has to do with the players movement)
            if death_fade.fade():   # wait for fade to complete   
                draw_text(f"!!!YOU DIED!!!", font_extra_big, WHITE, SCREEN_WIDTH//2-190, SCREEN_HEIGHT//2 - 200)
                draw_text(f"Press 'S' to restart the LEVEL", font_big, WHITE, SCREEN_WIDTH//2-275, SCREEN_HEIGHT//2)
                draw_text(f"Press 'ESC' to exit the game", font_big, WHITE, SCREEN_WIDTH//2-275, SCREEN_HEIGHT//2 + 100)
                restart = "level"   # level is failed and if user selects to restart then the level is restarted
                
               
    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            run = False # run is now false
            
        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                controls = True # user is selecting to view controls
            if event.key == pygame.K_SPACE:
                agent.shot = True
                # Remember what movement user was doing before shot so that movement can continue after shooting
                if agent.moving_left:
                    agent.moving_left = False
                    movement = 0
                elif agent.moving_right:
                    agent.moving_right = False
                    movement = 1
            if event.key == pygame.K_a:
                agent.moving_left = True
                agent.shot = False  # agent must stop shooting when moving
            if event.key == pygame.K_d:
                agent.moving_right = True
                agent.shot = False  # agent must stop shooting when moving
            if event.key == pygame.K_w and agent.alive:    # !!need to check if agent is alive in more than one place!!
                agent.jump = True
                jump_fx.play()  # play jump sound
            if event.key == pygame.K_r:    # !!need to check if agent is alive in more than one place!!
                agent.reload = True
                # Remember what movement user was doing before reload so that movement can continue after shooting
                if agent.moving_left:
                    agent.moving_left = False
                    movement = 0
                elif agent.moving_right:
                    agent.moving_right = False
                    movement = 1
            if event.key == pygame.K_b: # start game
                pygame.mixer.music.stop()   # stop menu music
                pygame.mixer.music.load('game/audio/music_level.mp3') # load level music
                pygame.mixer.music.play(-1, 0.0, 5000) # start game music
                start_game = True   # start the game
                start_intro = True  # start the intro        
            if event.key == pygame.K_s: # restart level or game
                if restart == "level":
                    # run intro fade again when player restarts the game
                    start_intro = True # start intro_fade again
                    death_fade.fade_counter = 0 # reset fade counter so that death_fade can be run from scratch again if needed
                elif restart == "game":
                    level = 1
                    start_game = False # start intro_fade again
                    victory_fade.fade_counter = 0 # reset fade counter so that death_fade can be run from scratch again if needed
                    pygame.mixer.music.stop()   # stop game music
                    pygame.mixer.music.load('game/audio/music_menu.mp3') # load menu music
                    pygame.mixer.music.play(-1, 0.0, 5000) # start menu music
                    
                restart = "none"    # reset the restart variable to "none"
                bg_scroll = 0   # bg_scroll is the total amount of scrolling done in the game
                world_data = reset_level()  # get world data from reset_level
                # load in level data and create world
                with open(f'game/level/level{level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World() # create World
                agent, health_bar = world.process_data(world_data)  # get agent and healthbar
            if event.key == pygame.K_ESCAPE:
                run = False
                
        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_c:
                controls = False    # user is deselecting to view controls
            if event.key == pygame.K_a:
                agent.moving_left = False
                movement = None
            if event.key == pygame.K_d:
                agent.moving_right = False
                movement = None
            if event.key == pygame.K_r:
                agent.reload = False
                # check if agent was moving before shooting and reset back to that movement if key is still down
                if movement == 0:
                    agent.moving_left = True
                elif movement == 1:
                    agent.moving_right = True
            if event.key == pygame.K_SPACE:
                agent.shot = False
                # check if agent was moving before shooting and reset back to that movement if key is still down
                if movement == 0:
                    agent.moving_left = True
                elif movement == 1:
                    agent.moving_right = True
                    
    # take everything that happened in one iteration of the loop and upate the game window with that.
    pygame.display.update()
    
pygame.quit()
