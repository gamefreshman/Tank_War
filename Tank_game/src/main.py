import pygame
import sys
import time
import random
from map import generate_blocks

tank_L1_1 = pygame.image.load("images/tank_L1_1.png")
tank_L1_2 = pygame.image.load("images/tank_L1_2.png")
tank_L1_3 = pygame.image.load("images/tank_L2_3.png")
tank_L1_4 = pygame.image.load("images/tank_L2_4.png")
tank_L2_1 = pygame.image.load("images/tank_L2_1.png")
tank_L2_2 = pygame.image.load("images/tank_L2_2.png")
tank_L2_3 = pygame.image.load("images/tank_L2_3.png")
tank_L2_4 = pygame.image.load("images/tank_L2_4.png")
tank_L3_1 = pygame.image.load("images/tank_L3_1.png")
tank_L3_2 = pygame.image.load("images/tank_L3_2.png")
tank_L3_3 = pygame.image.load("images/tank_L3_3.png")
tank_L3_4 = pygame.image.load("images/tank_L3_4.png")
bullet_up = pygame.image.load("images/bullet_up.png")
bullet_down = pygame.image.load("images/bullet_down.png")
bullet_left = pygame.image.load("images/bullet_left.png")
bullet_right = pygame.image.load("images/bullet_right.png")
enemy_1_1 = pygame.image.load("images/enemy_1_1.png")
enemy_1_2 = pygame.image.load("images/enemy_1_2.png")
enemy_1_3 = pygame.image.load("images/enemy_1_3.png")
enemy_1_4 = pygame.image.load("images/enemy_1_4.png")
enemy_2_1 = pygame.image.load("images/enemy_2_1.png")
enemy_2_2 = pygame.image.load("images/enemy_2_2.png")
enemy_2_3 = pygame.image.load("images/enemy_2_3.png")
enemy_2_4 = pygame.image.load("images/enemy_2_4.png")  
enemy_3_1 = pygame.image.load("images/enemy_3_1.png")
enemy_3_2 = pygame.image.load("images/enemy_3_2.png")
enemy_3_3 = pygame.image.load("images/enemy_3_3.png")
enemy_3_4 = pygame.image.load("images/enemy_3_4.png")
enemy_4_1 = pygame.image.load("images/enemy_4_1.png")
enemy_4_2 = pygame.image.load("images/enemy_4_2.png")
enemy_4_3 = pygame.image.load("images/enemy_4_3.png")
enemy_4_4 = pygame.image.load("images/enemy_4_4.png")
appear_0 = pygame.image.load("images/appear_0.png")
appear_1 = pygame.image.load("images/appear_1.png")
appear_2 = pygame.image.load("images/appear_2.png")
boom_0 = pygame.image.load("images/boom_0.png")
boom_1 = pygame.image.load("images/boom_1.png")
boom_2 = pygame.image.load("images/boom_2.png")
boom_3 = pygame.image.load("images/boom_3.png")
boom_4 = pygame.image.load("images/boom_4.png")
boom_5 = pygame.image.load("images/boom_5.png")
brick = pygame.image.load("images/brick.png")
iron = pygame.image.load("images/iron.png")
river = pygame.image.load("images/river.png")
tree = pygame.image.load("images/tree.png")

food_gun = pygame.image.load("images/food_gun.png")
food_shell = pygame.image.load("images/food_shell.png")
food_tank = pygame.image.load("images/food_tank.png")
food_star = pygame.image.load("images/food_star.png")

tree = pygame.transform.scale(tree, (60, 70))

map_width, map_height = 630, 630

food_resource = {
    'gun':food_gun,
    'shell':food_shell,
    'tank':food_tank,
    'star':food_star
}
archi = {
    brick:brick,
    iron:iron,
    river:river,
    tree:tree
}
enemy_resource = {
    'level1':{
        'up': enemy_1_1,
        'down': enemy_1_2,
        'left': enemy_1_3,
        'right': enemy_1_4
    },
    'level2':{
        'up': enemy_2_1,    
        'down': enemy_2_2,
        'left': enemy_2_3,
        'right': enemy_2_4
    },
    'level3':{
        'up': enemy_3_1,
        'down': enemy_3_2,
        'left': enemy_3_3,
        'right': enemy_3_4
    },
    'level4':{
        'up': enemy_4_1,
        'down': enemy_4_2,
        'left': enemy_4_3,
        'right': enemy_4_4
    }
}

tank_resources = {
    'level1':{
        'up': tank_L1_1,
        'down': tank_L1_2,
        'left': tank_L1_3,
        'right': tank_L1_4
    },
    'level2':{
        'up': tank_L2_1,
        'down': tank_L2_2,
        'left': tank_L2_3,
        'right': tank_L2_4
    },
    'level3':{
        'up': tank_L3_1,
        'down': tank_L3_2,
        'left': tank_L3_3,
        'right': tank_L3_4
    }
}
bullet_resources = {
    'up': bullet_up,
    'down': bullet_down,
    'left': bullet_left,
    'right': bullet_right
}




# 绘制开始按钮
def draw_button(msg, x, y, w, h, ic, ac,screen):
    font = pygame.font.SysFont("SimHei", 30)
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    # 绘制按钮
    button_rect = pygame.Rect(x, y, w, h)
    is_hover = button_rect.collidepoint(mouse)
    
    # 根据状态改变颜色
    btn_color = ac if is_hover else ic
    pygame.draw.rect(screen, btn_color, button_rect, border_radius=8)
    
    # 按钮文字
    text = font.render(msg, True, (0, 0, 0))
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)
    
    # 返回点击状态
    return is_hover and click[0]


class Bullet:
    def __init__(self, x, y, direction,screen,BULLET_SPEED=10):
        self.screen = screen
        self.x = x
        self.y = y
        self.image = bullet_resources[direction]  # 根据方向选择子弹图片
        self.direction = direction
        # 根据方向设置速度向量
        if direction == 'left':
            self.speed = (-BULLET_SPEED, 0)
        elif direction == 'right':
            self.speed = (BULLET_SPEED, 0)
        elif direction == 'up':
            self.speed = (0, -BULLET_SPEED)
        elif direction == 'down':
            self.speed = (0, BULLET_SPEED)
        else:  # 默认向右
            self.speed = (BULLET_SPEED, 0)
    
    def update(self):
        self.x += self.speed[0]
        self.y += self.speed[1]
        if self.x < 0 or self.x > map_width or self.y < 0 or self.y > map_height:
            return False
        return True  # 返回True表示子弹仍在屏幕内
    def draw(self, screen):
        self.screen.blit(self.image, (self.x, self.y))

class Tank:
    def __init__(self, x, y, level='level1',screen=None):
        self.foodtank = False
        self.screen = screen
        self.is_appearing = True 
        self.x = x
        self.y = y
        self.speed = 5
        self.level = level  # 坦克等级
        self.direction = 'up'  # 初始方向
        self.image = None  # 初始图片
        self.bullets = []  # 存储子弹
        self.bullet_speed = 10
        self.current_appear_frame = 0  # 当前动画帧索引
        self.appear_frames = [
            appear_0,
            appear_1,
            appear_2
        ]
        self.appear()
        self.HP = 3
        self.is_booming = False
        self.current_boom_frame = 0  # 当前爆炸动画帧索引
        self.boom_frames = [
            boom_0,
            boom_1,
            boom_2,
            boom_3,
            boom_4,
            boom_5
        ]
        self.shootsound = pygame.mixer.Sound("music/fire.wav")
        self.bullet_boom = []
        self.MAX_BULLETS = 1  # 坦克最多可发射的子弹数
    # 定义一个名为appear的函数,创建坦克的同时在连续三帧播放三个显示动画，一帧一个
    def appear(self):
        """更新出场动画状态（需每帧调用）"""
        if self.is_appearing:
            frame = self.current_appear_frame//10
            self.screen.blit(self.appear_frames[frame], (self.x, self.y))
            self.current_appear_frame += 1
            # 动画播放完毕（3帧）
            if self.current_appear_frame >= len(self.appear_frames)*10:
                self.is_appearing = False
                self.current_appear_frame = 0
    
    def boom(self):
        if self.is_booming:
            frame = self.current_boom_frame//5
            self.screen.blit(self.boom_frames[frame], (self.x-25, self.y-25))
            self.current_boom_frame += 1
            # 动画播放完毕（6帧）
            if self.current_boom_frame >= len(self.boom_frames)*5:
                self.is_booming = False
                self.current_boom_frame = 0
    
    def bulletBoom(self,x,y,frame = 0):
        cur_frame = frame//3
        self.screen.blit(self.boom_frames[cur_frame], (x-25, y-25))
        frame += 1
        if frame >= len(self.boom_frames)*3:
            return None
        return x,y,frame

    def move(self, direction, last_direction, barriers):
        if direction == 'stop':
            # 停止移动时不改变位置
            self.direction = last_direction
        dx, dy = 0, 0
        if direction == 'left':
            dx = -self.speed
        elif direction == 'right':
            dx = self.speed
        elif direction == 'up':
            dy = -self.speed
        elif direction == 'down':
            dy = self.speed
        
        new_x, new_y = self.x + dx, self.y + dy
        new_rect = pygame.Rect(new_x, new_y, 50, 50)
        # 检查新的位置是否与障碍物重叠
        collision = False
        for barrier_rect in barriers:
            if new_rect.colliderect(barrier_rect):
                collision = True
                break
        if not collision:
            self.x = new_x
            self.y = new_y
        if(self.x < 0):
            self.x = 0
        if(self.x > map_width - 50):  # 假设坦克宽度为50
            self.x = map_width - 50
        if(self.y < 0):
            self.y = 0
        if(self.y > map_height - 50):  # 假设坦克高度为50
            self.y = map_height - 50
        # 更新坦克图片
        self.draw()       
    
    def shoot(self):
        if len(self.bullets) < self.MAX_BULLETS:  # 检查子弹数量限制
            self.bullet = Bullet(self.x+20, self.y+20, self.direction,self.screen)  # 创建新子弹
            self.bullets.append(self.bullet)
            
        self.shootsound.play()
        self.draw()

    def be_shoot(self):
        self.HP -= 1
        self.is_booming  = True
        if self.HP == 0:
            return True
        return False

    def draw_tank(self,level):
        return tank_resources[level][self.direction]
    
    def draw(self):
        self.image = self.draw_tank(self.level)
        self.screen.blit(self.image, (self.x, self.y))  # 绘制坦克
        for bullet in self.bullets:
            if not bullet.update():  # 更新子弹位置
                self.bullets.remove(bullet)  # 如果子弹超出屏幕，移除它
            else:  # 如果子弹仍在屏幕内，绘制它
                bullet.draw(self.screen)
        if self.is_appearing:
            self.appear()
        if self.is_booming:
            self.boom()
        self.bullet_boom = [self.bulletBoom(x, y, frame) for x, y, frame in self.bullet_boom if self.bulletBoom(x, y, frame)]

#创建敌方坦克
class EnemyTank(Tank):
    def __init__(self, x, y, level='level1', screen=None):
        super().__init__(x, y, level, screen)
        self.direction = 'down'
        self.ai_timer = 0  # AI决策计时器
        self.shoot_time = 0  # 射击计时器
        self.shoot_timer = 60  # 射击计时器
        self.current_ai_dir = 'down'  # 当前AI选择的方向
        if self.level == 'level1':
            self.HP = 1
            self.speed = 2
            self.MAX_BULLETS = 1
            self.shoot_timer = 60
        elif self.level == 'level2':
            self.HP = 2
            self.speed = 2
            self.shoot_timer = 40
            self.MAX_BULLETS = 2
        elif self.level == 'level3':
            self.HP = 3
            self.speed = 2
            self.shoot_timer = 60
            self.MAX_BULLETS = 1
        elif self.level == 'level4':
            self.HP = 4
            self.speed = 2
            self.shoot_timer = 40
            self.MAX_BULLETS = 1
        self.shootsound = pygame.mixer.Sound("music/Gunfire.wav")
    
    def draw_tank(self, level):
        return enemy_resource[level][self.direction]

    def shoot(self):
        if len(self.bullets) < self.MAX_BULLETS:  # 检查子弹数量限制
            self.bullet = Bullet(self.x+20, self.y+20, self.direction,self.screen)  # 创建新子弹
            self.bullets.append(self.bullet)

    def update(self, barriers):
        """每帧更新（需在主循环中调用）"""
        # AI决策间隔（每60帧一次）
        self.ai_timer += 1
        self.shoot_time += 1
        if self.ai_timer >= 60:
            self.current_ai_dir = random.choice(['left','right','up','down'])
            self.ai_timer = 0
        
        # 调用修改后的父类移动
        super().move(direction=self.current_ai_dir, last_direction=self.direction, barriers=barriers)
        if self.shoot_time >= self.shoot_timer:
            self.shoot() 
            self.shoot_time = 0
    # 添加敌方专属标识（如红色描边）
        super().draw()  # 先执行父类绘制

    


class map():
    def __init__(self,screen,WIDEH=map_width, HEIGHT=map_width):
        self.iron_pos = []
        self.brick_pos = []
        self.tree_pos = []
        self.river = []
        self.river_pos = []
        self.mapinit()
        self.bang = pygame.mixer.Sound("music/bang.wav")
        self.WIDEH = WIDEH
        self.HEIGHT = HEIGHT
        self.screen = screen
        self.enemy_tanks = []  # 存储敌方坦克
        self.enemy_timmer = 300  # 敌方坦克生成计时器
        self.enemy_time = 0
        self.enemy_num = 0
        self.enemy4 = 0
        self.tank = self.tank_create()
        self.enemy_first_create()
        self.food = []
        self.collision = []
        self.boom_frames = [
            boom_0,
            boom_1,
            boom_2,
            boom_3,
            boom_4,
            boom_5
        ]

    def prepare_barriers(self):
        """准备障碍物矩形列表用于碰撞检测"""
        barriers = []
        
        # 将砖块位置转换为矩形
        for pos in self.brick_pos:
            barriers.append(pygame.Rect(pos[0], pos[1], 24, 24))
            
        # 将铁墙位置转换为矩形
        for pos in self.iron_pos:
            barriers.append(pygame.Rect(pos[0], pos[1], 24, 24))
            
        return barriers
    
    def mapinit(self):
        self.brick_pos,self.iron_pos,self.tree_pos,self.river_pos = generate_blocks()
        global river
        for (sx, sy), (sw, sh) in self.river_pos:
            river = pygame.transform.scale(river, (sw, sh))
            self.river.append(river)

    def drawmap(self):
        for pos in self.brick_pos:
            self.screen.blit(brick, pos)
        for pos in self.iron_pos:
            self.screen.blit(iron, pos)
        i = 0
        for pos,_ in self.river_pos:
            self.screen.blit(self.river[i], pos)
            i += 1

    def drawtree(self):
        for pos in self.tree_pos:
            self.screen.blit(tree, pos)
    def check_collision(self):
        # 检测碰撞
        player_rect = pygame.Rect(self.tank.x, self.tank.y, 50, 50)

        for x,y,type in self.food:
            if player_rect.colliderect(pygame.Rect(x, y, 50, 50)):
                self.food.remove((x,y,type))
                if type == 'gun':
                    self.tank.bullet_speed += 5
                elif type == 'shell':
                    self.tank.MAX_BULLETS += 1
                elif type == 'tank':
                    self.tank.foodtank += 1
                elif type == 'star':
                    self.tank.HP += 1
        for bullet in self.tank.bullets:
            bullet_rect = pygame.Rect(bullet.x, bullet.y, 5, 5)
            flag = False
            for pos in self.brick_pos:
                if bullet_rect.colliderect(pygame.Rect(pos[0], pos[1], 24, 24)):
                    self.bang.play()
                    self.brick_pos.remove(pos)
                    flag = True
                    break
            for pos in self.iron_pos:
                if bullet_rect.colliderect(pygame.Rect(pos[0], pos[1], 24, 24)):
                    self.bang.play()
                    flag = True
                    break
            if flag:
                self.tank.bullets.remove(bullet)
                continue
            for enemy in self.enemy_tanks[:]:
                    if bullet_rect.colliderect(pygame.Rect(enemy.x, enemy.y, 50, 50)):
                        self.tank.bullets.remove(bullet)
                        self.bang.play()
                        if enemy.be_shoot():
                            self.collision.append((enemy.x,enemy.y,0))
                            if enemy.level == 'level4':
                                #随机选一个1-4的随机数，对应四种不同食物
                                food_type = random.choice(['gun','shell','tank','star'])
                                self.food.append((enemy.x,enemy.y,food_type))
                            self.enemy_tanks.remove(enemy)
                        break
        

        for enemy in self.enemy_tanks:     
            flag = False
            for bullet in enemy.bullets[:]:
                bullet_rect = pygame.Rect(bullet.x, bullet.y, 5, 5)
                for pos in self.brick_pos:
                    if bullet_rect.colliderect(pygame.Rect(pos[0], pos[1], 24, 24)):
                        self.bang.play()
                        self.brick_pos.remove(pos)
                        flag = True
                        break
                for pos in self.iron_pos:
                    if bullet_rect.colliderect(pygame.Rect(pos[0], pos[1], 24, 24)):
                        self.bang.play()
                        flag = True
                        break
                if flag:
                    enemy.bullets.remove(bullet)
                    continue
                for my_bullet in self.tank.bullets[:]:
                    if bullet_rect.colliderect(pygame.Rect(my_bullet.x, my_bullet.y, 50, 50)):
                        enemy.bullets.remove(bullet)
                        self.bang.play()
                        self.tank.bullets.remove(my_bullet)
                        flag = True
                        self.tank.bullet_boom.append((my_bullet.x, my_bullet.y, 0))
                        break
                if flag:
                    continue
                if bullet_rect.colliderect(player_rect):
                    enemy.bullets.remove(bullet)
                    if self.tank.be_shoot():
                        return True
        return False
    def boom_draw(self,x,y,frame=0):
        cur_frame = frame//3
        self.screen.blit(self.boom_frames[cur_frame], (x-25, y-25))
        frame += 1
        if frame >= len(self.boom_frames)*3:
            return None
        return x,y,frame
    
    def food_draw(self):    
        for x,y,type in self.food:
            self.screen.blit(food_resource[type], (x, y)) 

    def text_draw(self):
        font = pygame.font.SysFont("SimHei", 20)  # 设置字体
        text = font.render(f"HP: {self.tank.HP} Speed: {self.tank.bullet_speed} Bullet: {self.tank.MAX_BULLETS} ", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))  # 在屏幕上绘制文本

    def is_position_valid(self, x, y, barriers):
        """检查位置是否与障碍物重叠"""
        # 坦克尺寸为50x50
        tank_rect = pygame.Rect(x, y, 50, 50)
        
        # 检查所有障碍物
        for barrier in barriers:
            if tank_rect.colliderect(barrier):
                return False
                
        # 检查与已有坦克的碰撞
        for tank in self.enemy_tanks:
            if tank.x - 50 < x < tank.x + 50 and tank.y - 50 < y < tank.y + 50:
                return False
        
        # 检查与玩家坦克的碰撞
        if self.tank.x - 50 < x < self.tank.x + 50 and self.tank.y - 50 < y < self.tank.y + 50:
            return False
            
        return True
      
    def tank_create(self):
        barriers = self.prepare_barriers()
        
        # 检查玩家坦克是否存在的方法
        def position_valid_without_player_tank(x, y):
            """检查位置是否有效，但不考虑玩家坦克（因为玩家坦克尚未创建）"""
            tank_rect = pygame.Rect(x, y, 50, 50)
            
            # 1. 检查障碍物碰撞
            for barrier in barriers:
                if tank_rect.colliderect(barrier):
                    return False
                    
            # 2. 检查敌方坦克碰撞（如果已存在）
            for enemy in self.enemy_tanks:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, 50, 50)
                if tank_rect.colliderect(enemy_rect):
                    return False
                    
            return True
        
        # 尝试在屏幕下半部分随机位置
        for attempt in range(10):
            x = random.randint(0, self.WIDEH - 50)
            y = random.randint(400, 600)  # 屏幕下半部分
            
            if position_valid_without_player_tank(x, y):
                return Tank(x, y, 'level3', self.screen)
        
        # 如果随机位置无效，尝试安全位置
        safe_positions = [
            (self.WIDEH // 4, 500),
            (self.WIDEH // 2, 500),
            (3 * self.WIDEH // 4, 500),
            (100, 500),
            (self.WIDEH - 100, 500)
        ]
        
        # 随机打乱安全位置顺序
        random.shuffle(safe_positions)
        
        for x, y in safe_positions:
            if position_valid_without_player_tank(x, y):
                return Tank(x, y, 'level3', self.screen)
        
        # 如果所有位置都无效，返回默认位置
        return Tank(self.WIDEH // 2, 500, 'level3', self.screen)

    def enemy_first_create(self):
        barriers = self.prepare_barriers()
        for i in range(4):
            # 随机尝试生成位置，确保在上半屏(y < 315)
            for attempt in range(10):  # 最多尝试10次
                x = random.randint(0, self.WIDEH - 50)
                y = random.randint(50, 200)  # 上半屏位置，y在50-200之间
                
                if self.is_position_valid(x, y, barriers):
                    enemy_type = random.choice(['level1','level2','level3','level4'])
                    if enemy_type == 'level4':
                        self.enemy4 += 1
                    self.enemy_tanks.append(EnemyTank(x, y, enemy_type, self.screen))
                    self.enemy_num += 1
                    break
            else:  # 如果10次都没找到合适位置，使用默认安全位置
                enemy_type = random.choice(['level1','level2','level3','level4'])
                if enemy_type == 'level4':
                    self.enemy4 += 1
                # 默认位置：屏幕顶部中间
                self.enemy_tanks.append(EnemyTank(self.WIDEH // 2, 50, enemy_type, self.screen))
                self.enemy_num += 1
    
    def enemy_create(self):
        if self.enemy_num < 20 and self.enemy_time >= self.enemy_timmer:
            barriers = self.prepare_barriers()
            self.enemy_timmer -= 5
            self.enemy_time = 0
            
            # 尝试找到有效位置（上半屏）
            for attempt in range(20):  # 最多尝试20次
                x = random.randint(0, self.WIDEH - 50)
                y = random.randint(50, 250)  # 上半屏位置
                
                if self.is_position_valid(x, y, barriers):
                    if self.enemy4 < 3:
                        enemy_type = random.choice(['level1','level2','level3','level4'])
                        if enemy_type == 'level4':
                            self.enemy4 = 0
                        else:
                            self.enemy4 += 1
                    else:
                        enemy_type = 'level4'
                        self.enemy4 = 0
                    
                    self.enemy_tanks.append(EnemyTank(x, y, enemy_type, self.screen))
                    self.enemy_num += 1
                    return  # 找到位置后立即返回
                    
            # 如果没找到合适位置，尝试用安全位置
            safe_positions = [
                (self.WIDEH // 4, 50),
                (self.WIDEH // 2, 50),
                (3 * self.WIDEH // 4, 50),
                (50, 50),
                (self.WIDEH - 100, 50)
            ]
            
            for pos in safe_positions:
                if self.is_position_valid(pos[0], pos[1], barriers):
                    if self.enemy4 < 3:
                        enemy_type = random.choice(['level1','level2','level3','level4'])
                        if enemy_type == 'level4':
                            self.enemy4 = 0
                        else:
                            self.enemy4 += 1
                    else:
                        enemy_type = 'level4'
                        self.enemy4 = 0
                    
                    self.enemy_tanks.append(EnemyTank(pos[0], pos[1], enemy_type, self.screen))
                    self.enemy_num += 1
                    return

            # 如果仍然找不到，使用顶部中央位置
            if self.enemy4 < 3:
                enemy_type = random.choice(['level1','level2','level3','level4'])
                if enemy_type == 'level4':
                    self.enemy4 = 0
                else:
                    self.enemy4 += 1
            else:
                enemy_type = 'level4'
                self.enemy4 = 0
            
            self.enemy_tanks.append(EnemyTank(self.WIDEH // 2, 50, enemy_type, self.screen))
            self.enemy_num += 1


    def updata(self,tank_status,last_tank_status):
        self.food_draw()
        self.drawmap()
        self.enemy_time += 1
        self.enemy_create()
        self.text_draw()
        barriers = self.prepare_barriers()
        self.tank.move(tank_status,last_tank_status,barriers)
        self.collision = [self.boom_draw(x, y, frame) for x, y, frame in self.collision if self.boom_draw(x, y, frame)]
        for enemy_tank in self.enemy_tanks:
            enemy_tank.update(barriers)
        if self.check_collision() or self.enemy_num >20:
            return True
        for pos in self.tree_pos:
            self.screen.blit(tree, pos)
        return False
        
        


class  MainGame():
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.WIDTH = map_width
        self.HEIGHT = map_width
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.UI_status = "menu"  # 初始状态为菜单
        self.last_tank_status = 'up'
        self.bullets = []  # 存储所有活动中的子弹
        self.Map = map(self.screen)
        self.key_status = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
            "shoot": False
        }
        self.background = pygame.image.load("images/background.png")
        self.shoot_cooldown = 0
        self.enemy_tank = []
        
    def start(self):
        pygame.display.set_caption("Tank Battle")
        #绘制背景
        self.screen.blit(self.background, (0, 0))
        # 游戏主循环
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.UI_status == "game":
                    # 射击触发（KEYDOWN确保单次按下）
                    if event.type == pygame.KEYDOWN: 
                        if event.key == pygame.K_SPACE and self.shoot_cooldown <= 0:
                            self.Map.tank.shoot()
                            self.shoot_cooldown = 30  # 设置冷却时间（假设60帧/s）
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                self.UI_status = "menu"

            # 绘制主菜单
            if self.UI_status == "menu":
                self.UI_status = self.main_menu()

            elif self.UI_status == "game":
                keys = pygame.key.get_pressed()
                self.key_status["up"] = keys[pygame.K_w] or keys[pygame.K_UP]
                self.key_status["down"] = keys[pygame.K_s] or keys[pygame.K_DOWN]   
                self.key_status["left"] = keys[pygame.K_a] or keys[pygame.K_LEFT]
                self.key_status["right"] = keys[pygame.K_d] or keys[pygame.K_RIGHT]
                self.game_loop()
            
            elif self.UI_status == "gameover":
                self.gameover()
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        self.UI_status = "menu"
            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= 1
            pygame.display.flip()
            time.sleep(0.02)  # 控制帧率
          
    
    
    def gameover(self):
        self.screen.fill((0, 0, 0))  # 清屏
        #设置字体
        self.screen.blit(self.background, (0, 0))  # 绘制背景
        gameover = pygame.image.load("images/gameover.png")
        scaled_gameover_image = pygame.transform.scale(gameover, (self.WIDTH, self.HEIGHT))
        self.screen.blit(scaled_gameover_image, (0, 0))

    def main_menu(self):
        self.screen.fill((0, 0, 0))  # 清屏
        font = pygame.font.SysFont("SimHei", 30)  # 设置字体
        #设置字体
        self.screen.blit(self.background, (0, 0))  # 绘制背景
        text = font.render("Tank Battle", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 100))
        self.screen.blit(text, text_rect)
        
        if draw_button("开始游戏", 250, 300, 130, 50, (0, 200, 0), (0, 255, 0),self.screen):
            print("开始游戏按钮被点击")
            self.Map = map(self.screen)
            return "game"
        return "menu"


    def game_loop(self):
        self.screen.fill((0, 0, 0))  
        self.screen.blit(self.background, (0, 0))

        if self.key_status["up"]:
            tank_status = 'up'
        elif self.key_status["down"]:
            tank_status = 'down'
        elif self.key_status["left"]:
            tank_status = 'left'
        elif self.key_status["right"]:
            tank_status = 'right'
        else:
            tank_status = 'stop'

        if self.Map.updata(tank_status,self.last_tank_status):
            self.UI_status = "gameover"
        if tank_status != 'stop' :
            self.last_tank_status = tank_status

       

MainGame().start()