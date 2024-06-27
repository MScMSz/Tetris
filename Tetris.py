# Tetris by Metzger Szabolcs
# Python 3.11.2, Ursina Engine 7.0.0
# MX Linux 23
# 2024 Június


from ursina import *
from random import choice

TETRAMINOS = {
    'T': {'shape': [(0,0),(-1,0),(1,0),(0,-1)], 'color':rgb(128,0,128)},
    'O': {'shape': [(0,0),(0,-1),(1,0),(1,-1)], 'color':rgb(255,255,0)},
    'L': {'shape': [(0,0),(0,-1),(0,1),(-1,1)], 'color':rgb(255,192,255)},
    'J': {'shape': [(0,0),(0,-1),(0,1),(1,1)], 'color':rgb(0,0,255)},
    'I': {'shape': [(0,0),(0,-1),(0,-2),(0,1)], 'color':rgb(0,255,255)},
    'S': {'shape': [(0,0),(-1,0),(0,-1),(1,-1)], 'color':rgb(0,255,0)},
    'Z': {'shape': [(0,0),(1,0),(0,-1),(-1,-1)], 'color':rgb(255,0,0)}
    }

VISIBLE = False
DEBUG = False
COLS = 10
ROWS = 20

LEVEL = 2000

WIN_HEIGTH = 800
WIN_WIDTH = int(WIN_HEIGTH * 1.778)

old_shape_list = []
fullrows = 0

app = Ursina(borderless = False, title = 'Tetris', fullscreen= False, size = (WIN_WIDTH,WIN_HEIGTH), 
            development_mode= False)

EditorCamera().scale = 1.8
camera.position = Vec3(0.5,5,-5)
camera.rotation_x = 23


class Game():
    def __init__(self):
        self.background = Entity(model= 'plane', texture='assets/background_milkyway.jpg', scale=50,  
                                position= (0,-.52,-9.5))
        self.board = Entity(model='plane', scale=(COLS,1,ROWS), color= color.hsv(0,0,.5,.8), texture= 'white_cube', 
                       texture_scale= (COLS,ROWS), collider= 'box', position= (0.5, -0.51, -9.5))
        self.ground = Entity(model= 'wireframe_cube', position= (0.5,0,-ROWS), scale= (COLS,1,1), collider= 'box', 
                        visible= VISIBLE)
        self.side_L = Entity(model= 'wireframe_cube', position= (-5,0,-9.5), scale= (1,1,ROWS), collider= 'box',
                        visible= VISIBLE)
        self.side_R = duplicate(self.side_L, x= 6)

        self.next_shapes = [choice(list(TETRAMINOS.keys())) for shape in range(3)]
        self.tetris = Tetramino(self.next_item())
        
        self.score = 0
        self.level = 1

        self.score_text = Text(text= '', position= (-0.45, -0.35), size= .08, color= color.black)
        self.next_shape_text = Text(text= 'Next Shape:', position= (0.41,0.45), size= .1)
        self.pause_text = Text(text='Coffee time!', position=(-0.2,0,0), scale=2, enabled=False)

        self.game_over_text = Text(text='Game Over ! \n Restart with ESC', origin=(0,0,0), scale=2, enabled= False)

        self.pause_handler = Entity(ignore_paused = True)

    def pause_handler_input(self,key):
        if key == 'escape':
            application.paused = not application.paused
            self.pause_text.enabled = application.paused 
            self.game_over_text.enabled = False

    def next_item(self):
        next_shape = self.next_shapes.pop(0)
        self.next_shapes.append(choice(list(TETRAMINOS.keys())))
        #print_on_screen(self.next_shapes, position= (0.7,0.4), scale= 1.3, duration= 5)
        self.preview(self.next_shapes)

        return next_shape
    
    def preview(self,shape_list):
        global old_shape_list

        for old_shape in old_shape_list:
            for block in old_shape.blocks:
                #block.visible_setter(False)
                destroy(block)

        old_shape_list.clear()
        
        for i, new_shape in enumerate(shape_list):
            old_shape_list.append(Preview(new_shape,(8, (-5 * i)-3)))
                         
    def input(self,key):
        self.tetris.control(key)
            
    def scoring(self):
        self.score_text.text = 'Level: '+ str(self.level) + '    Score: '+ str(self.score)
        if self.score > 10 and  self.score % LEVEL == 0:
            self.tetris.speed += 2
            self.level += 1

    def update(self):
        self.tetris.move_down(self.tetris.speed)
        self.scoring()

    def game_over(self):
        for e in scene.children:
            if e.name == 'block':
                destroy(e)
        destroy(self.board)

        self.score_text.text = ''
        Game.__init__(self)

        application.paused = True
        self.game_over_text.enabled = application.paused
        
        self.score = 0

    
class Block(Entity):
    def __init__(self, pos, color):
        super().__init__(self)
        self.pos = pos
        self.color = color
        self.model = 'cube'
        self.texture = 'white_cube'
        self.x= self.pos[0]
        self.y= 0
        self.z= self.pos[1] 
        self.collider = 'box'
        self.old = False
        self.scale = 1


class Preview():
    def __init__(self,shape,offset):
        self.key = shape    
        self.shape = TETRAMINOS[self.key]
        self.block_pos = TETRAMINOS[self.key]['shape']
        self.color =  TETRAMINOS[self.key]['color']
        self.blocks = [Block((pos[0]+offset[0],pos[1]+offset[1]), self.color) for pos in self.block_pos]


class Tetramino():
    def __init__(self,shape):
        self.key = shape   
        self.shape = TETRAMINOS[self.key]
        self.block_pos = TETRAMINOS[self.key]['shape']
        self.color =  TETRAMINOS[self.key]['color']
        self.blocks = [Block(pos, self.color) for pos in self.block_pos]
        self.speed = 3

        for block in self.blocks:
            if block != self.blocks[0]:
                block.parent_setter(self.blocks[0]) 

    def new_item(self,shape):
        self.key = shape   
        self.shape = TETRAMINOS[self.key]
        self.block_pos = TETRAMINOS[self.key]['shape']
        self.color =  TETRAMINOS[self.key]['color']
        self.blocks = [Block(pos, self.color) for pos in self.block_pos]

        for block in self.blocks:
            if block != self.blocks[0]:
                block.reparent_to(self.blocks[0]) 

    def hits_ground(self):
        hit_info = boxcast(game.ground.position, direction=(0,0,1), thickness=(COLS,.1), traverse_target= self.blocks[0],
                            distance=.51, debug= False)
        return hit_info
    
    def hit_wall_L(self):
        for block in self.blocks:
            if block.intersects(game.side_L).hit:
                return True
            
    def hit_wall_R(self):
        for block in self.blocks:
             if block.intersects(game.side_R).hit:
                return True
             
    def hit_blocks(self,dir):
        for block in self.blocks:
            for e in scene.entities:
                if e.name == 'block' and e.old == True and distance(block.world_position+dir, e.world_position) < 1: 
                    return True
                    
    def check_rows(self):
        global fullrows 
        blocks_in_row = []

        for row in range(-(ROWS-1),1,1):
            blocks_in_row.clear()
            for e in scene.entities:   
                if e.name == 'block' and e.old == True and round(e.world_z) == row:
                    blocks_in_row.append(e)
        
            if len(blocks_in_row) == COLS:
                for e in blocks_in_row:
                    destroy(e)

                for z in range(row,1,1):
                    for e in scene.entities:
                        if e.name == 'block' and e.old == True and round(e.world_z) == z:
                            e.world_z -=1   
                fullrows += 1
                blocks_in_row.clear()
                self.check_rows()      

                game.score += (fullrows * 40) + ((fullrows + 1) * 30)     
                  
    def move_down(self,speed):
        global fullrows

        if self.hits_ground().hit or self.hit_blocks((0,0,0)):
            for block in self.blocks:
                block.old = True
                block.world_parent_setter(scene)
                block.z = round(block.z)
                
            fullrows = 0    
            self.check_rows()
 
            game.score += 10
            self.new_item(game.next_item())

        if self.hit_blocks((0,0,0)) and self.blocks[0].z == 0:
            game.game_over()
        
        else:
            self.blocks[0].position += Vec3(0,0,-1) * time.dt * speed
                      
    def drop_down(self):
        global fullrows

        for i in range(round(self.blocks[0].z), ROWS, 1):
            if self.hits_ground().hit or self.hit_blocks((0,0,0)):
                for block in self.blocks:
                    block.old = True
                    block.world_parent_setter(scene)
                    block.z = round(block.z)
                
                fullrows = 0    
                self.check_rows()
    
                game.score += 15
                self.new_item(game.next_item())
                return

            if self.hit_blocks((0,0,0)) and self.blocks[0].z == 0:
                game.game_over()
                return

            else:
                self.blocks[0].position += Vec3(0,0,-.5)
           
            

        if self.hit_blocks((0,0,0)) and self.blocks[0].z == 0:
            game.game_over()
                       
    def move_horizontal(self,dir):
        if dir == 'L':
            if self.hit_wall_L() or self.hit_blocks((-1,0,0)):
                return
            else:
                self.blocks[0].world_position -= Vec3(1,0,0)

        if dir == 'R':
            if self.hit_wall_R() or self.hit_blocks((1,0,0)):
                return
            else:
                self.blocks[0].world_position += Vec3(1,0,0)
       
    def do_rotate(self):
        if self.blocks[0].world_x <= -4 or self.blocks[0].world_x >= 5:
            return
        else:
            self.blocks[0].rotation_y = self.blocks[0].world_rotation_y + 90
            self.blocks[0].world_rotation_y = self.blocks[0].rotation_y

    def control(self,key):
        if key == 'w':
            self.do_rotate()
        if key == 'a':
            self.move_horizontal('L')       
        if key == 'd':
            self.move_horizontal('R')
        if key == 'space':
            self.drop_down()


game = Game()

input = game.input
game.pause_handler.input = game.pause_handler_input
update = game.update

app.run()