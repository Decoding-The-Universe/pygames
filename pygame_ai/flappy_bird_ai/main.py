import pygame
import random
import time
import neat
import os
import math
import numpy as np
pygame.font.init()
WIN_WIDTH = 1100
WIN_HEIGHT = 700

def image(file_name):
    return pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', file_name)))

BIRD_IMGS = [image('bird1.png'), image('bird2.png'), image('bird3.png')]
PIPE_IMG = image('pipe.png') #pygame.image.load(os.path.join('imgs', 'pipe.png'))
BASE_IMG =  image('base.png')
BG = pygame.transform.scale2x(image('bg.png'))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Bg:
    
    def __init__(self, IMG):
        self.IMG = IMG
        self.VEL = 5
        self.x1 = 0
        self.y = 0
        self.WIDTH = self.IMG.get_width()
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.WIDTH
        
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.WIDTH
            
    
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))



class Bird:

    IMGS = BIRD_IMGS
    MAX_ROTATION = 25 # max rotation in upward direction and max_tilt_in_downward has no limit..........
    ROT_VEL = 20 # tilt in downard per each move.... 
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0 ###
        self.tick_count = 0 ###
        self.vel = 0
        self.height = self.y
        self.img_count = 0 ###
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0 ###
        self.height =  self.y
    
    def move(self):
        self.tick_count += 1 ###
        # s = ut + 1/2 at**2 (u = vel, a = 3, t = tick_count)
        d = self.vel*self.tick_count + 1.5*self.tick_count**2

        if d >= 16:
            d = 16
        
        if d < 0:
            d-=2
        
        self.y = self.y + d

        if d<0 or self.y < self.height + 50: # if moving up (or) until you come 50 px down show the bird tilted up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt> -90:
                self.tilt -= self.ROT_VEL
    
    def draw(self, win):
        self.img_count +=1
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        next_center = self.img.get_rect(topleft = (self.x, self.y)).center
        center_elements = []
        for i in range(2):
            center_elements.append(round(next_center[i]))
        next_center = (center_elements[0], center_elements[1])
        new_rect = rotated_image.get_rect(center = next_center) #(w, h, c)
#### check 79, 83 line of code...... in google. how it works????
        win.blit(rotated_image, new_rect.topleft)
    def get_mask(self, bird):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 200
    VEL = 5
    def __init__(self, x):
        self.x = x
        self.height =0
        self.PIPE_BOTTOM = PIPE_IMG
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True ) # args --> (img, hf, vf)
        self.gap = 100
        self.top = 0
        self.bottom = 0
        self.passed = False
        self.set_height()
    
    def set_height(self):
        self.height = math.floor(random.randrange(50, 450))
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.gap      
    
    def move(self):
        self.x -= self.VEL
        #pass
    
    def draw(self, win):
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
        win.blit(self.PIPE_TOP, (self.x, self.top))

    def collide(self, bird):
        bird_mask = bird.get_mask(bird)
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)
        if b_point or t_point:
            return True
        return False

class Base:
    WIDTH = BASE_IMG.get_width()
    VEL = 5
    IMG = BASE_IMG 

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
        self.x3  = 2*self.WIDTH
        self.x4  = 3*self.WIDTH
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        self.x3 -= self.VEL
        self.x4 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = 3*self.WIDTH
        
        if self.x2 + self.WIDTH < 0:
            self.x2 = 3*self.WIDTH
        
        if self.x3 + self.WIDTH < 0:
            self.x3 = 3*self.WIDTH

        if self.x4 + self.WIDTH < 0:
            self.x4 = 3*self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
        win.blit(self.IMG, (self.x3, self.y))
        win.blit(self.IMG, (self.x4, self.y))
def draw(win, birds, pipes, base, bg, score):
    bg.draw(win)
    for pipe in pipes:
        pipe.draw(win)
    for bird in birds:
        bird.draw(win)
    base.draw(win)
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    pygame.display.update()

def main(genomes, config):
    nets = []
    ge = []
    birds = []
    #each genome = (id, g)
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(200, 350))
        g.fitness = 0
        ge.append(g)


    clock = pygame.time.Clock()
    WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pipes = [Pipe(500)]
    score = 0
    base = Base(630)
    run = True
    bg = Bg(BG)
    while run:
        add_pipe = False
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            base.move()
            bg.move()

            pipe_ind = 0
            if len(birds) > 0:
                if birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                    pipe.ind =1
            else:
                run = False
                break

            for x, bird in enumerate(birds):
                bird.move()
                ge[x].fitness += 0.1
                output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
                if output[0] > 0.5:
                    bird.jump()


            rem = []
            add_pipe = False
            for pipe in pipes:
                for x, bird in enumerate(birds):
                    if pipe.collide(bird):
                        birds.pop(x)
                        nets.pop(x)
                        ge.pop(x)
                    if not pipe.passed and pipe.x < bird.x:
                        #print(pipe.passed, (pipe.x , bird.x))
                        score+=1
                        pipe.passed = True
                        add_pipe = True
                    pipe.move()
                if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                    rem.append(pipe)
            if add_pipe:
                for g in ge:
                    g.fitness += 5
                pipes.append(Pipe(800))
            
            for r in rem:
                pipes.remove(r)
            for x, bird in enumerate(birds):
                if bird.y + bird.img.get_height() + 0.5 >= base. y or bird.y <0:
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)


            draw(WIN, birds, pipes, base, bg, score)

    pygame.quit()
    quit() 




def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(main, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


'''
def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultSpeciesSet, neat.DefaultStagnation, neat.DefaultReproduction, config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)
    
'''
    

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)


'''
# species_elitism  --- 2 # no. of species we want to preserse even though they haven't shown any imporvement.. to stop total extenction
# survival_threshold = 0.2  --- fraction of species allowed to reproduce at each generation
#weight_mutate_power     = 0.5 # prob of mutating
#weight_mutate_rate      = 0.8 # prob of mutating by multypling by a factor
#weight_replace_rate     = 0.1 # prob of mutating by choosing a random value from the normal dist...

'''




