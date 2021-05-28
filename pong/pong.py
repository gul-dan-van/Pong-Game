from warnings import resetwarnings
import pygame
from pygame.locals import *
import pymunk
import random

pygame.init()

def game_to_munk(p):
    return p[0],screen_height-p[1]
def munk_to_game(p):
    return map(int,[p[0],screen_height-p[1]])

clock=pygame.time.Clock()
fps=120

screen_width=1300
screen_height=700
margin=30
paddle_dist=margin+45
score1=0
score2=0
all_tasks=6
balls=[]

BLACK=(0,0,0)
WHITE=(255,255,255)
BLUE=(0,0,255)
RED=(255,0,0)
GREEN=(0,255,0)
LIGHT_GREY=(220,220,220)
DARK_GREY=(30,30,30)

all_colors=[(255,255,0),(0,0,255),(255,0,0),(0,255,0),(220,220,220),(30,30,30),(0,255,255),(255,0,255),(100,0,23)]
# all_colors=[GREEN,(255,255,0)]

screen=pygame.display.set_mode((screen_width,screen_height))
space=pymunk.Space()
pygame.display.set_caption('Pong')


'''  Sweet little Background  '''

def draw_bg():
    screen.fill(BLACK)
    height=screen_height-2*margin
    n=8
    ratio=0.3
    gap=int(ratio*(height/(n+1)))
    length=int((1-ratio)*(height/n))
    for i in range(n):
        pygame.draw.line(screen,DARK_GREY,(screen_width//2,margin+i*(length+gap)+gap),(screen_width//2,margin+gap+i*(length+gap)+length),2)
        
def draw_text(text,x,y):
    font=pygame.font.SysFont("Algerian",20,False,False)
    f=font.render(text,False,WHITE)
    screen.blit(f,(x,y))
    
def f1(ball):
    ball.color=DARK_GREY

def f2(ball):
    ball.color=ball.back_up

def f3(ball):
    ball.body.velocity=ball.body.velocity[0]*1.5,0

def f4(ball):
    u,v=ball.body.velocity
    ball.body.velocity=u*0.5,800*(2*(v>1)-1)

def f5(ball):
    if len(balls)<2:
        balls.append(Ball(color=random.choice(all_colors)))
        balls[-1].body.velocity=600*random.choice([1,-1]),100*random.choice([1,-1])
    if len(balls)==2:
        x=random.randint(1,100)
        if x==49:
            balls.append(Ball(color=random.choice(all_colors)))
            balls[-1].body.velocity=600*random.choice([1,-1]),100*random.choice([1,-1])

def f6(ball):
    if len(balls)>1:
        x=balls[random.choice(range(len(balls)))]
        space._remove_body(x.body)
        space._remove_shape(x.shape)
        del x

class Ball():
    def __init__(self,x=screen_width//2,y=screen_height//2,rad=10,color=RED):
        self.body=pymunk.Body()
        self.body.velocity=0,0
        self.body.position=x,y
        self.shape=pymunk.Circle(self.body,rad)
        self.shape.density=1
        self.shape.elasticity=1
        self.shape.collision_type=1
        self.rad=rad
        space.add(self.body,self.shape)
        self.color=color
        self.back_up=color

    def draw(self):
        x,y=map(int,self.body.position)
        pygame.draw.circle(screen,self.color,(x,y),self.rad)

    def reset(self):
        self.color=self.back_up
        v,u=self.body.velocity
        if u==0:
            self.body.velocity=600*(2*(v>1)-1),random.choice([1,-1])*100
        if abs(u)>600:
            self.body.velocity=600*(2*(v>1)-1),(2*(u>1)-1)*100

    def restart(self):
        self.body.velocity=0,0
        self.body.position=screen_width//2,screen_height//2
        self.color=self.back_up
    
    def flay(self,space,arbiter,data):
        self.reset()
        self.body.velocity=self.body.velocity*(700/self.body.velocity.length)
        exec('f'+str(random.randint(1,all_tasks))+'(self);')
        return False

    def point(self,space1,arbiter,data):
        global score1
        global score2
        global space
        if self.body.position[0]<screen_width//2:
            score2+=1
        else:
            score1+=1
        self.reset()
        if len(balls)>1:
            x=balls[random.choice(range(len(balls)))]
            space._remove_body(x.body)
            space._remove_shape(x.shape)
            del x
        return True

class Wall():
    def __init__(self,x1,y1,x2,y2,width,collision_number=None):
        self.width=width
        self.body=pymunk.Body(body_type=pymunk.Body.STATIC)
        self.shape=pymunk.Segment(self.body,(x1,y1),(x2,y2),width)
        self.shape.elasticity=1
        self.shape.collision_type=1
        space.add(self.body,self.shape)
        self.x1=x1
        self.x2=x2
        self.y1=y1
        self.y2=y2
        if collision_number:
            self.shape.collision_type=collision_number

    def draw(self):
        pygame.draw.line(screen,LIGHT_GREY,(self.x1,self.y1),(self.x2,self.y2),self.width)
    
class Paddle():
    def __init__(self,x,is_cpu=False):
        self.body=pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.body.position=x,screen_height//2
        self.shape=pymunk.Segment(self.body,[0,-30],[0,30],10)
        self.shape.elasticity=1
        self.shape.collision_type=10
        space.add(self.body,self.shape)
        self.is_cpu=is_cpu
        self.score=0
    
    def draw(self):
        p1=self.body.local_to_world(self.shape.a)
        p2=self.body.local_to_world(self.shape.b)
        pygame.draw.line(screen,WHITE,p1,p2,10)
    
    def on_edge(self):
        if self.body.local_to_world(self.shape.a)[1]<margin:
            self.body.velocity=0,0
            self.body.position=self.body.position[0],margin+30
            return True
        if self.body.local_to_world(self.shape.b)[1]>screen_height-margin:
            self.body.velocity=0,0
            self.body.position=self.body.position[0],screen_height-margin-30
            return True
        return False
    
    def stop(self):
        self.body.velocity=0,0

    def move(self,up=False):
        if up:
            self.body.velocity=0,-900
        else:
            self.body.velocity=0,900

    def move_self(self):
            x,y=ball.body.position
            a,b=self.body.position
            if ball.body.velocity[0]<0:
                if y>b:self.body.velocity=0,500
                else:self.body.velocity=0,-500
            else:
                self.stop()


'''   Defining Walls  '''

wall_width=2
left_wall=Wall(margin,margin,margin,screen_height-margin,wall_width,2)
right_wall=Wall(screen_width-margin,margin,screen_width-margin,screen_height-margin,wall_width,2)
up_wall=Wall(margin,margin,screen_width-margin,margin,wall_width)
down_wall=Wall(margin,screen_height-margin,screen_width-margin,screen_height-margin,wall_width)

balls.append(Ball(color=BLUE))

# paddle1=Paddle(paddle_dist,10,75)
paddle1=Paddle(paddle_dist,True)
paddle2=Paddle(screen_width-paddle_dist,False)


run=True
while run:
    clock.tick(fps)
    space.step(1/fps)

    draw_bg()
    
    for ball in balls:
        scored=space.add_collision_handler(1,2)
        scored.begin=ball.point
        contact_with_paddle=space.add_collision_handler(1,10)
        contact_with_paddle.post_solve=ball.flay

        ball.draw()


    draw_text(f"Score : {score1}",margin+30,5)
    draw_text(f"Score : {score2}",screen_width-145,5)
    draw_text(f"Ball Count : {len(balls)}",screen_width//2-80,5)

    left_wall.draw()
    right_wall.draw()
    up_wall.draw()
    down_wall.draw()


    '''  Moving paddles  '''
    
    keys=pygame.key.get_pressed()
    if paddle1.is_cpu and not paddle1.on_edge():
        paddle1.move_self()
    elif ~paddle1.on_edge():
        if keys[K_w]:
            paddle1.move(True)
        elif keys[K_s]:
            paddle1.move()
        else:
            paddle1.stop()
    if paddle2.is_cpu and not paddle2.on_edge():
        paddle2.move_self()
    elif ~paddle2.on_edge():
        if keys[K_UP]:
            paddle2.move(True)
        elif keys[K_DOWN]:
            paddle2.move()
        else:
            paddle2.stop()


    paddle1.draw()
    paddle2.draw()


    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            run=False
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:
                for i in balls[:0:-1]:
                    balls.remove(i)
                balls[0].restart()
            if event.key==pygame.K_SPACE:
                balls[0].body.velocity=600*random.choice([1,-1]),100*random.choice([1,-1])
                

    pygame.display.update()

pygame.quit()