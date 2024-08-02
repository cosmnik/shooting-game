from pygame import *
import math
import random

debug = False
wrapmode = True #does the player wrap around the edges?

res = (700, 500)
FPS = 60
BPS = 6 #bullets per second

FPB = FPS/BPS #frames per bullet


window = display.set_mode(res)
display.set_caption("maze game")

hitSaucers = 0
missedSaucers = 0
hitreq = 100
misreq = 10

def drawtext(text, x, y, size = 20, color = (255,255,255)):
    font.init()
    f = font.Font(None, size)
    window.blit(f.render(text, True, color), (x,y))

def lerp(a,b,t):
    return a + (t * (b-a))


# print(lerp(2,3,0.0)) 
# print(lerp(2,3,0.25))
# print(lerp(2,3,0.5))
# print(lerp(2,3,0.75))
# print(lerp(2,3,1.0))

class Sprite(sprite.Sprite): #handles pygame image rendering
    def __init__(self, img, x, y, w, h, dx = 0, dy = 0):
        '''image : image path'''
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(img), (w, h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.dx = dx
        self.dy = dy
    
    def render(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(Sprite):
    def __init__(self, x, y, w, h, img):
        super().__init__(img, x, y, w, h)

        self.dx = 0
        self.dy = 0
        #movement speed
        self.speed = 120
    
    def update(self, keys):

        #friction
        self.dx *= 0.7
        self.dy *= 0.7

        movedir = (0,0)
        if keys[K_a]:
            movedir = (movedir[0] - 1, movedir[1])
        if keys[K_d]:
            movedir = (movedir[0] + 1, movedir[1])

        self.dx += movedir[0] * self.speed / FPS
        self.dy += movedir[1] * self.speed / FPS

        
        #if abs(self.dx) < 0.001: self.dx = 0
        #if abs(self.dy) < 0.001: self.dy = 0

        #looping

        self.rect.x += self.dx
        self.rect.y += self.dy
        if wrapmode: self.rect.x = (self.rect.x + 70) % 770 - 70

    def fire(self):
        bullet = Bullet(self.rect.x + 20, self.rect.y-20, 30, 100, 0, -15)
        bulletgroup.add(bullet)
        mixer.Channel(1).play(mixer.Sound(shootsfx))

class Alien(Sprite):
    def __init__(self, x, y, w, h, img):
        super().__init__(img, x, y, w, h)

        self.dx = 0
        self.dy = 0
        #movement speed (not used, see self.dx and self.dy)
        #self.speed = 120
    
    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        #if wrapmode: self.x = (self.x + self.w) % (res[0]+self.h) - self.w
        #self.y = (self.y + self.h) % (res[1]+self.h) - self.h
        if self.rect.y > res[1]:
            self.rect.y = -self.rect.h
            global missedSaucers
            missedSaucers += 1

class Bullet(Sprite):
    def __init__(self, x, y, w, h, dx = 0, dy = -15):
        super().__init__("bullet.png", x, y, w, h, dx, dy)
    
    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.rect.y < -self.rect.h:
            self.kill()


        

mixer.init()
mixer.music.load("space.ogg")
mixer.music.play()
shootsfx = "laserShoot.wav"
explodesfx = "explosion.wav"

bg = Sprite("galaxy.jpg", 0, 0, res[0], res[1])
clock = time.Clock()
game = True

player = Player(465,350,70,100, "rocket.png")

aliens = 8
aliensize = 0.8
aliengroup = sprite.Group()
for i in range(aliens):
    alien = Alien(random.random()*(res[0]-50)-25, 0, 80, 50, "ufo.png")
    alien.dy = ((random.random() * 100) + 30)/FPS+0.3
    aliengroup.add(alien)

class AlienOrb(Sprite):
    def __init__(self, x, y, w, h, target_x, target_y, newdx, newdy):
        super().__init__("alien_orb.png", x, y, w, h)
        self.tx = target_x
        self.ty = target_y
        self.initx = x
        self.inity = y
        self.newdx = newdx #saves the velocity of alien
        self.newdy = newdy
        self.prog = 0 #1 is at (tx, ty), 0 is (initx, inity)
    
    def update(self):
        if (self.tx - self.rect.x)**2 + (self.ty - self.rect.y)**2 < 10**2 or self.prog >= 1:
            self.kill()
            alien = Alien(self.tx, self.ty, 80, 50, "ufo.png") #membuat alien baru
            alien.dy = self.newdy + max((random.random() * 6 - 2)/FPS, 0)
            alien.dx = self.newdx
            aliengroup.add(alien)
        self.rect.x = lerp(self.initx, self.tx, self.prog)
        self.rect.y = lerp(self.inity, self.ty, self.prog)
        self.prog += 5/((self.tx - self.initx)**2 + (self.ty - self.inity)**2)**0.5

alienOrbGroup = sprite.Group()

bulletgroup = sprite.Group()
shootcooldown = FPB
active = True
while active:
    if game:
        keys = key.get_pressed()

        player.update(keys)
        aliengroup.update()
        bulletgroup.update()
        alienOrbGroup.update()

        collides = sprite.groupcollide(aliengroup, bulletgroup, True, True)

        for c in collides: 
            alienOrbGroup.add(AlienOrb(c.rect.x, c.rect.y, 24, 24, random.random()*(res[0]-50)-25, random.random()*25, c.dx, c.dy))
            c.kill()
            # alien = Alien(random.random()*(res[0]-50)-25, 0, 80, 50, "ufo.png")
            # alien.dy = ((random.random() * 100) + 30)/FPS + 1
            # aliengroup.add(alien)
            mixer.Channel(0).play(mixer.Sound(explodesfx))
            hitSaucers += 1
            if hitSaucers % 10 == 0:
                change = 18/FPS
                for i in aliengroup.sprites():
                    i.dy += change
                for i in alienOrbGroup.sprites():
                    i.newdy += change

        bg.render()
        player.render()
        aliengroup.draw(window)
        alienOrbGroup.draw(window)
        bulletgroup.draw(window)
        shootcooldown -= 1

        if keys[K_SPACE]:
            if shootcooldown <= 0:
                player.fire()
                shootcooldown = FPB
        drawtext(f"hit    : {hitSaucers} / {hitreq}", 0, 5, 40)
        drawtext(f"missed : {missedSaucers} / {misreq}", 0, 35, 40)


        
        if missedSaucers >= misreq and not debug:
            game = False
            drawtext("YOU LOST", 100, 200, 150, (255,0,0))
        
        if hitSaucers >= hitreq and not debug:
            game = False
            drawtext("YOU WON!", 100, 200, 150, (0,255,0))

        if debug:
            drawtext(f"player : pos ({player.rect.x}, {player.rect.y})",20,res[1] - 20, 20, (255,255,255))
            drawtext(f"player : vel ({player.dx}, {player.dy})",20,res[1] - 35, 20, (255,255,255))

    for e in event.get():
        if e.type == QUIT:
            active = False
    clock.tick(FPS)
    display.update()
