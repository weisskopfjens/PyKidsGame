import pygame
from pygame.locals import *
from random import *
from svg import Parser, Rasterizer

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

pygame.init()
pygame.font.init()

class Carrot(pygame.sprite.Sprite):
    #This class represents a car. It derives from the "Sprite" class in Pygame.
    def __init__(self):
        # Call the parent class (Sprite) constructor
        super().__init__()
        #self.image = pygame.image.load('carrot.png').convert_alpha()
        self.image = load_svg(str(randint(1, 7))+".svg", None, None, None, (100,100))
        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect()

class Cloud(pygame.sprite.Sprite):
    #This class represents a car. It derives from the "Sprite" class in Pygame.
    def __init__(self, x, y, size):
        # Call the parent class (Sprite) constructor
        super().__init__()
        #self.image = pygame.image.load('carrot.png').convert_alpha()
        self.image = load_svg("cloud.svg", None, None, None, (200,100))
        self.image = aspect_scale(self.image,(size,size) )
        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = randint(1, 3)

    def update(self):
        # Makes the enemy move in the x direction.
        self.rect.x = self.rect.x + self.speed
        if self.rect.x > 1024:
            self.rect.x = 0 - self.rect.size[0]
            self.speed = randint(1, 3)

class Rabbit(pygame.sprite.Sprite):
    #This class represents a car. It derives from the "Sprite" class in Pygame.
    def __init__(self):
        # Call the parent class (Sprite) constructor
        super().__init__()
        self.image = pygame.image.load('player.png').convert_alpha()
        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect()


pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((1024, 768),pygame.FULLSCREEN)
#screen = pygame.display.set_mode((1024, 768))

background = pygame.image.load('background.jpg').convert()
effect = pygame.mixer.Sound('eat.wav')
effect2 = pygame.mixer.Sound('rulp.wav')
pygame.mixer.music.load('music.mp3')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.2)

background = pygame.transform.scale(background,(1024, 768))

screen.blit(background, (0, 0))

carrot_sprites_list = pygame.sprite.Group()
rabbit_sprites_list = pygame.sprite.Group()
cloud_sprites_list = pygame.sprite.Group()

for i in range(6):
    cloud = Cloud( randint(0, 900),randint(0, 150),randint(50, 150) )
    cloud_sprites_list.add(cloud)

carrot = Carrot()
carrot.rect.x = randint(0, 900)
carrot.rect.y = randint(0, 600)
carrot_sprites_list.add(carrot)

rabbit = Rabbit()
rabbit_sprites_list.add(rabbit)

#Allowing the user to close the window...
carryOn = True
clock=pygame.time.Clock()

while carryOn:
    event = pygame.event.poll ()
    if event.type == pygame.QUIT:
         carryOn = False  # Be interpreter friendly
    elif event.type == KEYDOWN:
        if event.key == K_ESCAPE:
            carryOn = False
            pygame.quit()
    cloud_sprites_list.update()    
    carrot_sprites_list.update()
    rabbit_sprites_list.update()    
    # See if the Sprite block has collided with anything in the Group block_list
    # The True flag will remove the sprite in block_list
    blocks_hit_list = pygame.sprite.groupcollide(rabbit_sprites_list, carrot_sprites_list, False, True)
    # Check the list of colliding sprites, and add one to the score for each one
    for block in blocks_hit_list:
        effect.play()
        carrot = Carrot()
        carrot.rect.x = randint(0, 900)
        carrot.rect.y = randint(0, 600)
        carrot_sprites_list.add(carrot)
        dorulp = randint(0, 5)
        if dorulp == 1:
            effect2.play()
        
    screen.blit(background, (0,0))
    rabbit.rect.center = pygame.mouse.get_pos()
    cloud_sprites_list.draw(screen)
    carrot_sprites_list.draw(screen)
    rabbit_sprites_list.draw(screen)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
exit()
