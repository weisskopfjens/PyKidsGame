import pygame
from pygame.locals import *
import random
from svg import Parser, Rasterizer
import logging

# -----------------------------------------------------------
# 
# (C) 2020 Jens Weißkopf, Langenfeld, Germany
# Released under GNU Public License (GPL)
# email jens@familieweisskopf.de
# Mediadata from https://freesvg.org/
#
# Happy and Joyful Children by Free Music | https://soundcloud.com/fm_freemusic
# Music promoted by https://www.free-stock-music.com
# Creative Commons Attribution 3.0 Unported License
# https://creativecommons.org/licenses/by/3.0/deed.en_US
#
# -----------------------------------------------------------

redlist = [2, 5, 9, 10]
yellowlist = [3, 7]
greenlist = [4, 6]
bluelist = [8, 11, 12]
colorlist = []
colorlist.append(redlist)
colorlist.append(yellowlist)
colorlist.append(greenlist)
colorlist.append(bluelist)

def load_svg(filename, scale=None, size=None, clip_from=None, fit_to=None):
    """Returns Pygame Image object from rasterized SVG
    If scale (float) is provided and is not None, image will be scaled.
    If size (w, h tuple) is provided, the image will be clipped to specified size.
    If clip_from (x, y tuple) is provided, the image will be clipped from specified point.
    If fit_to (w, h tuple) is provided, image will be scaled to fit in specified rect.
    """
    svg = Parser.parse_file(filename)
    tx, ty = 0, 0
    if size is None:
        w, h = svg.width, svg.height
    else:
        w, h = size
        if clip_from is not None:
            tx, ty = clip_from
    if fit_to is None:
        if scale is None:
            scale = 1
    else:
        fit_w, fit_h = fit_to
        scale_w = float(fit_w) / svg.width
        scale_h = float(fit_h) / svg.height
        scale = min([scale_h, scale_w])
    rast = Rasterizer()
    req_w = int(w * scale)
    req_h = int(h * scale)
    buff = rast.rasterize(svg, req_w, req_h, scale, tx, ty)
    image = pygame.image.frombuffer(buff, (req_w, req_h), 'RGBA')
    return image

def aspect_scale(img,box):
    """ Scales 'img' to fit into box bx/by.
     This method will retain the original image's aspect ratio """
    bx,by = box
    ix,iy = img.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by
    sx = int(sx)
    sy = int(sy)

    return pygame.transform.smoothscale(img, (sx,sy))

class Snowflake(pygame.sprite.Sprite):
    def __init__(self, start_pos):
        super().__init__()
        self.imgsize = random.randint(2,70)
        self.image = load_svg("snowflake.svg", None, None, None, (self.imgsize,self.imgsize))
        self.rect = self.image.get_rect()
        self.rect[0] = start_pos[0] + random.randint(-20,20)
        self.rect[1] = start_pos[1] + random.randint(-20,20)
        self.speed = ( random.uniform(-10,10), random.uniform(-10,10) )
        self.position = [self.rect[0],self.rect[1]]

    def update(self):
        self.position[0] = self.position[0] + self.speed[0]
        self.position[1] = self.position[1] + self.speed[1]
        self.rect[0] = int(self.position[0])
        self.rect[1] = int(self.position[1])
        #self.rect[0] = self.rect[0] + self.speed[0]
        #self.rect[1] = self.rect[1] + self.speed[1]
        if not screen.get_rect().contains(self.rect):
            self.kill()
        
class Player(pygame.sprite.Sprite):
    #This class represents a car. It derives from the "Sprite" class in Pygame.
    def __init__(self):
        # Call the parent class (Sprite) constructor
        super().__init__()
        self.image = pygame.image.load('player2.png').convert_alpha()
        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect()

class Field(pygame.sprite.Sprite):
    #This class represents a car. It derives from the "Sprite" class in Pygame.
    def __init__(self,image,imgnr):
        # Call the parent class (Sprite) constructor
        super().__init__()
        self.image = image
        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect()
        self.imgnr = imgnr
        self.winfield = False

class Game():
    def __init__(self, gamescreen, fieldsize = 200):
        self.restart_timer = -1
        self.repeatquestion_timer = -1
        self.thiscolorspeech_timer = -1
        self.fields = []
        self.field_sprites_list = pygame.sprite.Group()
        self.fieldsize = fieldsize
        self.gamescreen = gamescreen
        self.gamescreen_mx = gamescreen.get_width()/2
        self.gamescreen_my = gamescreen.get_height()/2
        self.pics = []
        for i in range(1, 13):
            logging.info("Loading picture ["+str(i)+".svg]")
            self.pics.append( load_svg(str(i)+".svg", None, None, None, (self.fieldsize,self.fieldsize)) )
        self.thiscolorspeech = []
        for i in range(2, 12):
            logging.info("Loading speech [color-"+str(i)+".ogg]")
            self.thiscolorspeech.append( pygame.mixer.Sound("color-"+str(i)+".ogg") )
        self.colorspeech = []
        self.colorspeech.append( pygame.mixer.Sound('red.ogg') )
        self.colorspeech.append( pygame.mixer.Sound('yellow.ogg') )
        self.colorspeech.append( pygame.mixer.Sound('green.ogg') )
        self.colorspeech.append( pygame.mixer.Sound('blue.ogg') )
        self.rightspeech = pygame.mixer.Sound('richtig.ogg')
        self.falsespeech = pygame.mixer.Sound('falsch.ogg')
            
    def start(self):
        if self.restart_timer > 0:
            return
        self.fields.clear()
        self.fields = random.sample(range(0,4), 4)
        self.wantedcol = self.fields[random.randint(0,3)]
        relpos = ((-1,-1),(0,-1),(-1,0),(0,0))
        logging.info("Wanted color is "+str(self.wantedcol))
        self.colorspeech[self.wantedcol].play()
        self.repeatquestion_timer = 300 + random.randint(0,600)
        i = 0
        for field in self.fields:
            picnr = (random.choice(colorlist[field])-1)
            fieldsprite = Field( self.pics[ picnr ], picnr )
            fieldsprite.rect[0] = self.gamescreen_mx + relpos[i][0] * self.fieldsize
            fieldsprite.rect[1] = self.gamescreen_my + relpos[i][1] * self.fieldsize
            self.field_sprites_list.add(fieldsprite)
            if field == self.wantedcol:
                fieldsprite.winfield = True
            logging.info(i)
            logging.info("field="+str(field))
            logging.info(str(random.choice(colorlist[field]))+".svg")
            i=i+1

    def restart(self):
        self.restart_timer = 180
        
    def answer(self, plr_spritelist):
        logging.info(player.rect)
        
        #if player.rect.colliderect(self.winfield.rect):
        #if pygame.sprite.collide_mask(player,self.winfield):
        collide_dict = pygame.sprite.groupcollide(self.field_sprites_list,plr_spritelist, False, False)
        for plrcollide in collide_dict.keys():
            if len(collide_dict) == 1 and plrcollide.winfield == True:
                self.colorspeech[self.wantedcol].stop()
                logging.info("Win!")
                self.rightspeech.play()
                self.field_sprites_list.empty()
                self.restart()
                for i in range(0,100):
                    sf = Snowflake(plrcollide.rect.center)
                    snow_sprites_list.add(sf)
                    
            else:
                self.colorspeech[self.wantedcol].stop()
                logging.info("Loose!")
                self.falsespeech.play()
                self.wrongimgnr = plrcollide.imgnr-2
                self.thiscolorspeech_timer = 110
                self.repeatquestion_timer = 300

    def thiscolor(self, imgnr):
        self.wrongimgnr
        

    def update(self):
        if self.restart_timer > 0:
            self.restart_timer = self.restart_timer - 1
        elif self.restart_timer == 0:
            self.restart_timer = -1
            self.start()

        if self.repeatquestion_timer > 0:
            self.repeatquestion_timer = self.repeatquestion_timer - 1
        elif self.repeatquestion_timer == 0:
            self.repeatquestion_timer = 300 + random.randint(0,600)
            self.colorspeech[self.wantedcol].play()

        if self.thiscolorspeech_timer > 0:
            self.thiscolorspeech_timer = self.thiscolorspeech_timer - 1
        elif self.thiscolorspeech_timer == 0:
            self.thiscolorspeech[self.wrongimgnr].play()
            self.thiscolorspeech_timer = -1
            
        board = pygame.Surface((self.fieldsize*2, self.fieldsize*2),pygame.SRCALPHA)
        board.fill((0,0,0,128))
        self.gamescreen.blit(board, (self.gamescreen_mx - self.fieldsize, self.gamescreen_my - self.fieldsize) )
        self.field_sprites_list.update()
        self.field_sprites_list.draw(self.gamescreen)
        
pygame.init()
pygame.font.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((1024, 768),pygame.FULLSCREEN)
#screen = pygame.display.set_mode((1024, 768))

background = pygame.image.load('background2.jpg').convert()
background = pygame.transform.scale(background,(1024, 768))

snow_sprites_list = pygame.sprite.Group()
player_sprites_list = pygame.sprite.Group()
player = Player()
player_sprites_list.add(player)

game = Game(screen, 200)
game.start()

#Allowing the user to close the window...
carryOn = True
clock=pygame.time.Clock()

while carryOn:
    screen.blit(background, (0, 0))
    event = pygame.event.poll ()
    if event.type == pygame.QUIT:
         carryOn = False  # Be interpreter friendly
    elif event.type == KEYDOWN:
        if event.key == K_ESCAPE:
            carryOn = False
            pygame.quit()
    elif event.type == MOUSEBUTTONDOWN:
        player.rect[0],player.rect[1] = event.pos
        game.answer(player_sprites_list)

    player_sprites_list.update()
    snow_sprites_list.update()
        
    screen.blit(background, (0,0))
    
    player.rect[0],player.rect[1] = pygame.mouse.get_pos()
    game.update()
    
    player_sprites_list.draw(screen)
    snow_sprites_list.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
exit()
