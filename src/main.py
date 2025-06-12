import pygame
import sys
import time
import random
from enum import Enum
from abc import ABC, abstractmethod
import os

# 禁用pygame的提示信息
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# 尝试导入地图生成模块
try:
    from map import generate_blocks
except ImportError:
    print("Warning: Could not import map module, using default map")
    def generate_blocks(width, height):
        # 返回默认的简单地图
        bricks = [(x, y) for x in range(100, width-100, 100) 
                  for y in range(100, height//2, 100)]
        irons = [(x, y) for x in range(200, width-200, 200) 
                 for y in range(150, height//2, 150)]
        trees = [(x, y) for x in range(300, width-300, 300) 
                for y in range(200, height//2, 200)]
        rivers = []
        return bricks[:10], irons[:5], trees[:5], rivers

# ==================== 常量定义 ====================
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1200
FPS = 50
TILE_SIZE = 24
TANK_SIZE = 50

# ==================== 枚举类 ====================
class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    STOP = "stop"

class ShootMode(Enum):
    NORMAL = "普通射击"
    CHARGED = "蓄力射击"
    LASER = "激光射击"

class GameState(Enum):
    MENU = "menu"
    GAME = "game"
    GAMEOVER = "gameover"

# ==================== 全局资源管理器 ====================
resources = None

# ==================== 资源管理器 ====================
class ResourceManager:
    """统一管理游戏资源"""
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.load_resources()
    
    def load_resources(self):
        """加载所有游戏资源"""
        import os
        
        # 尝试不同的路径策略
        possible_base_dirs = []
        
        # 尝试获取脚本目录
        try:
            possible_base_dirs.append(os.path.dirname(os.path.abspath(__file__)))
        except:
            pass
        
        # 添加其他可能的目录
        possible_base_dirs.extend([
            os.getcwd(),  # 当前工作目录
            os.path.dirname(os.getcwd()),  # 父目录
            ".",  # 当前目录
        ])
        
        base_dir = None
        for dir in possible_base_dirs:
            if os.path.exists(os.path.join(dir, "images")):
                base_dir = dir
                print(f"找到资源目录: {base_dir}")
                break
        
        if base_dir is None:
            print("警告: 无法找到资源目录，游戏将使用默认图形")
            base_dir = os.getcwd()
        
        # 坦克图片
        tank_images = {
            'tank_L1_1': "images/tank_L1_1.png",
            'tank_L1_2': "images/tank_L1_2.png",
            'tank_L1_3': "images/tank_L2_3.png",
            'tank_L1_4': "images/tank_L2_4.png",
            'tank_L2_1': "images/tank_L2_1.png",
            'tank_L2_2': "images/tank_L2_2.png",
            'tank_L2_3': "images/tank_L2_3.png",
            'tank_L2_4': "images/tank_L2_4.png",
            'tank_L3_1': "images/tank_L3_1.png",
            'tank_L3_2': "images/tank_L3_2.png",
            'tank_L3_3': "images/tank_L3_3.png",
            'tank_L3_4': "images/tank_L3_4.png",
        }
        
        # 子弹图片
        bullet_images = {
            'bullet_up': "images/bullet_up.png",
            'bullet_down': "images/bullet_down.png",
            'bullet_left': "images/bullet_left.png",
            'bullet_right': "images/bullet_right.png",
        }
        
        # 敌人图片
        enemy_images = {}
        for level in range(1, 5):
            for dir in ['1', '2', '3', '4']:
                enemy_images[f'enemy_{level}_{dir}'] = f"images/enemy_{level}_{dir}.png"
        
        # 特效图片
        effect_images = {
            'appear_0': "images/appear_0.png",
            'appear_1': "images/appear_1.png",
            'appear_2': "images/appear_2.png",
            'boom_0': "images/boom_0.png",
            'boom_1': "images/boom_1.png",
            'boom_2': "images/boom_2.png",
            'boom_3': "images/boom_3.png",
            'boom_4': "images/boom_4.png",
            'boom_5': "images/boom_5.png",
        }
        
        # 地形图片
        terrain_images = {
            'brick': "images/brick.png",
            'iron': "images/iron.png",
            'river': "images/river.png",
            'tree': "images/tree.png",
        }
        
        # 食物图片
        food_images = {
            'food_gun': "images/food_gun.png",
            'food_shell': "images/food_shell.png",
            'food_tank': "images/food_tank.png",
            'food_star': "images/food_star.png",
        }
        
        # 其他图片
        other_images = {
            'gameover': "images/gameover.png",
        }
        
        # 加载所有图片
        all_images = {**tank_images, **bullet_images, **enemy_images, 
                     **effect_images, **terrain_images, **food_images, **other_images}
        
        loaded_count = 0
        for name, path in all_images.items():
            full_path = os.path.join(base_dir, path)
            try:
                self.images[name] = pygame.image.load(full_path)
                loaded_count += 1
            except:
                # 创建占位图片
                self.images[name] = pygame.Surface((50, 50))
                self.images[name].fill((255, 0, 255))
        
        print(f"成功加载 {loaded_count}/{len(all_images)} 个图片")
        
        # 特殊处理
        if 'tree' in self.images:
            try:
                self.images['tree'] = pygame.transform.scale(self.images['tree'], (60, 70))
            except:
                pass
        
        # 加载音效
        sound_files = {
            'fire': "music/fire.wav",
            'enemy_fire': "music/Gunfire.wav",
            'bang': "music/bang.wav",
        }
        
        for name, path in sound_files.items():
            full_path = os.path.join(base_dir, path)
            try:
                self.sounds[name] = pygame.mixer.Sound(full_path)
            except Exception as e:
                # 创建一个虚拟音效对象
                class DummySound:
                    def play(self):
                        pass
                self.sounds[name] = DummySound()

    
    def get_tank_image(self, level, direction):
        """获取坦克图片"""
        if not isinstance(direction, Direction):
            return self.images.get('tank_L3_1')  # 默认图片
        dir_map = {Direction.UP: '1', Direction.DOWN: '2', 
                  Direction.LEFT: '3', Direction.RIGHT: '4'}
        key = f'tank_L{level[-1]}_{dir_map.get(direction, "1")}'
        return self.images.get(key)
    
    def get_enemy_image(self, level, direction):
        """获取敌人图片"""
        if not isinstance(direction, Direction):
            return self.images.get('enemy_1_1')  # 默认图片
        dir_map = {Direction.UP: '1', Direction.DOWN: '2', 
                  Direction.LEFT: '3', Direction.RIGHT: '4'}
        key = f'enemy_{level[-1]}_{dir_map.get(direction, "1")}'
        return self.images.get(key)
    
    def get_bullet_image(self, direction):
        """获取子弹图片"""
        if not isinstance(direction, Direction):
            return self.images.get('bullet_up')  # 默认图片
        key = f'bullet_{direction.value}'
        return self.images.get(key)

# ==================== 武器系统 ====================
class Weapon(ABC):
    """武器基类"""
    def __init__(self, owner):
        self.owner = owner
        self.cooldown = 0
        self.max_cooldown = 30
    
    @abstractmethod
    def shoot(self):
        pass
    
    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

class Bullet:
    """普通子弹"""
    def __init__(self, x, y, direction, screen, speed=10, damage=1):
        self.x = x
        self.y = y
        self.direction = direction
        self.screen = screen
        self.speed = speed
        self.damage = damage
        # 安全获取图片
        if resources and hasattr(resources, 'get_bullet_image'):
            self.image = resources.get_bullet_image(direction)
        else:
            self.image = None
        self._set_velocity()
    
    def _set_velocity(self):
        """设置速度向量"""
        velocities = {
            Direction.LEFT: (-self.speed, 0),
            Direction.RIGHT: (self.speed, 0),
            Direction.UP: (0, -self.speed),
            Direction.DOWN: (0, self.speed)
        }
        self.velocity = velocities.get(self.direction, (self.speed, 0))
    
    def update(self):
        """更新子弹位置"""
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        return 0 <= self.x <= SCREEN_WIDTH and 0 <= self.y <= SCREEN_HEIGHT
    
    def draw(self):
        """绘制子弹"""
        if self.image:
            self.screen.blit(self.image, (self.x - self.image.get_width()/2, self.y- self.image.get_height()/2))
        else:
            pygame.draw.rect(self.screen, (255, 255, 0), (self.x, self.y, 5, 5))
    
    def get_rect(self):
        """获取碰撞矩形"""
        if self.image:
            return pygame.Rect(self.x, self.y, 
                             self.image.get_width(), self.image.get_height())
        return pygame.Rect(self.x, self.y, 5, 5)

class ChargedBullet(Bullet):
    """蓄力子弹"""
    def __init__(self, x, y, direction, screen, charge_rate):
        super().__init__(x, y, direction, screen)
        self.charge_rate = max(0.1, charge_rate)  # 确保最小值
        self.speed *= (1 + self.charge_rate * 2)  # 速度加成
        self.damage = 1 + int(self.charge_rate * 3)  # 伤害加成
        self._set_velocity()
        self._scale_image()
    
    def _scale_image(self):
        """缩放子弹图片"""
        if self.image and self.charge_rate > 0.3:
            scale = 1 + self.charge_rate * 2
            width = int(self.image.get_width() * scale)
            height = int(self.image.get_height() * scale)
            self.image = pygame.transform.scale(self.image, (width, height))
            self.x -= (width - self.image.get_width()) / 2 * (scale - 1)
            self.y -= (height - self.image.get_height()) / 2 * (scale - 1)
            

class LaserBeam:
    """激光束"""
    def __init__(self, x, y, direction, screen, duration=10):
        self.x = x
        self.y = y
        self.start_pos = (x, y)
        self.direction = direction
        self.screen = screen
        self.duration = duration
        self.damage = 5
        self.width = 10
        self._calculate_endpoints()
    
    def _calculate_endpoints(self):
        """计算激光束的端点"""
        if self.direction == Direction.UP:
            self.end_x, self.end_y = self.x, 0
        elif self.direction == Direction.DOWN:
            self.end_x, self.end_y = self.x, SCREEN_HEIGHT
        elif self.direction == Direction.LEFT:
            self.end_x, self.end_y = 0, self.y
        elif self.direction == Direction.RIGHT:
            self.end_x, self.end_y = SCREEN_WIDTH, self.y

        self.end_pos = (self.end_x, self.end_y)
    
    def update(self):
        """更新激光束"""
        self.duration -= 1
        return self.duration > 0
    
    def draw(self):
        """绘制激光束"""

        main_color = (255, 255, 255) if self.duration % 4 > 1 else (255, 200, 200)
        glow_color_1 = (180, 100, 100)
        glow_color_2 = (100, 50, 50)
        
        pygame.draw.line(self.screen, glow_color_2, self.start_pos, self.end_pos, self.width + 8)
        pygame.draw.line(self.screen, glow_color_1, self.start_pos, self.end_pos, self.width + 4)
        pygame.draw.line(self.screen, main_color, self.start_pos, self.end_pos, self.width)
    
    def get_collision_rects(self):
        """获取碰撞检测用的矩形列表"""
        rects = []
        if self.direction in [Direction.UP, Direction.DOWN]:
            # 垂直激光
            step = 10
            current_y = min(self.y, self.end_y)
            max_y = max(self.y, self.end_y)
            while current_y <= max_y:
                rects.append(pygame.Rect(self.x - self.width//2, current_y, 
                                       self.width, step))
                current_y += step
        else:
            # 水平激光
            step = 10
            current_x = min(self.x, self.end_x)
            max_x = max(self.x, self.end_x)
            while current_x <= max_x:
                rects.append(pygame.Rect(current_x, self.y - self.width//2, 
                                       step, self.width))
                current_x += step
        return rects

# ==================== 坦克类 ====================
class Tank:
    """玩家坦克类"""
    def __init__(self, x, y, level='level3', screen=None):
        self.x = x
        self.y = y
        self.screen = screen
        self.level = level
        self.direction = Direction.UP
        self.speed = 5
        self.hp = 3
        self.max_hp = 3
        
        # 射击系统
        self.shoot_mode = ShootMode.NORMAL
        self.bullets = []
        self.lasers = []
        self.max_bullets = 1
        self.bullet_speed = 10
        self.shoot_cooldown = 0
        self.max_cooldown = 30
        
        # 蓄力系统
        self.charging = False
        self.charge_power = 0
        self.max_charge_power = 100
        self.charge_speed = 4
        
        # 动画系统
        self.is_appearing = True
        self.appear_frame = 0
        self.is_exploding = False
        self.explode_frame = 0
        
        # 升级系统
        self.powerups = {
            'extra_life': 0,
            'bullet_speed': 0,
            'max_bullets': 0
        }
    
    def update(self):
        """更新坦克状态"""
        # 更新冷却
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # 更新子弹
        self.bullets = [b for b in self.bullets if b.update()]
        
        # 更新激光
        self.lasers = [l for l in self.lasers if l.update()]
        
        # 更新动画
        if self.is_appearing:
            self._update_appear_animation()
        if self.is_exploding:
            self._update_explode_animation()
    
    def move(self, direction, barriers):
        """移动坦克"""
        if direction == Direction.STOP:
            return
        
        self.direction = direction
        
        # 计算新位置
        dx, dy = 0, 0
        if direction == Direction.LEFT:
            dx = -self.speed
        elif direction == Direction.RIGHT:
            dx = self.speed
        elif direction == Direction.UP:
            dy = -self.speed
        elif direction == Direction.DOWN:
            dy = self.speed
        
        new_x = max(0, min(self.x + dx, SCREEN_WIDTH - TANK_SIZE))
        new_y = max(0, min(self.y + dy, SCREEN_HEIGHT - TANK_SIZE))
        
        # 碰撞检测
        new_rect = pygame.Rect(new_x, new_y, TANK_SIZE, TANK_SIZE)
        for barrier in barriers:
            if new_rect.colliderect(barrier):
                return
        
        self.x, self.y = new_x, new_y
    
    def shoot(self):
        """根据当前模式射击"""
        if self.shoot_cooldown > 0:
            return
        
        if self.shoot_mode == ShootMode.NORMAL:
            self._shoot_normal()
        elif self.shoot_mode == ShootMode.LASER:
            self._shoot_laser()
    
    def start_charging(self):
        """开始蓄力"""
        if self.shoot_mode == ShootMode.CHARGED and self.shoot_cooldown <= 0:
            self.charging = True
            self.charge_power = 0
    
    def release_charge(self):
        """释放蓄力射击"""
        if self.charging:
            self.charging = False
            charge_rate = self.charge_power / self.max_charge_power
            self._shoot_charged(charge_rate)
            self.charge_power = 0
    
    def update_charge(self):
        """更新蓄力状态"""
        if self.charging:
            self.charge_power = min(self.charge_power + self.charge_speed, 
                                  self.max_charge_power)
    
    def _shoot_normal(self):
        """普通射击"""
        if len(self.bullets) < self.max_bullets:
            bullet_x = self.x + TANK_SIZE / 2
            bullet_y = self.y + TANK_SIZE / 2
            bullet = Bullet(bullet_x, bullet_y, self.direction, self.screen, 
                          self.bullet_speed)
            self.bullets.append(bullet)
            self.shoot_cooldown = self.max_cooldown
            if resources and 'fire' in resources.sounds:
                resources.sounds['fire'].play()
    
    def _shoot_charged(self, charge_rate):
        """蓄力射击"""
        if len(self.bullets) < self.max_bullets:
            bullet_x = self.x + TANK_SIZE // 2 - 2
            bullet_y = self.y + TANK_SIZE // 2 - 2
            bullet = ChargedBullet(bullet_x, bullet_y, self.direction, 
                                 self.screen, charge_rate)

            self.bullets.append(bullet)
            self.shoot_cooldown = int(self.max_cooldown * (1 + charge_rate))
            if resources and 'fire' in resources.sounds:
                resources.sounds['fire'].play()
    
    def _shoot_laser(self):
        """激光射击"""
        laser_x = self.x + TANK_SIZE / 2
        laser_y = self.y + TANK_SIZE / 2
        laser = LaserBeam(laser_x, laser_y, self.direction, self.screen)
        self.lasers.append(laser)
        self.shoot_cooldown = self.max_cooldown * 2
        # 可以添加激光音效
    
    def switch_shoot_mode(self):
        """切换射击模式"""
        modes = list(ShootMode)
        current_index = modes.index(self.shoot_mode)
        next_index = (current_index + 1) % len(modes)
        self.shoot_mode = modes[next_index]
        self.charging = False
        self.charge_power = 0
    
    def take_damage(self, damage=1):
        """受到伤害"""
        self.hp -= damage
        self.is_exploding = True
        self.explode_frame = 0
        return self.hp <= 0
    
    def apply_powerup(self, powerup_type):
        """应用道具效果"""
        if powerup_type == 'gun':
            self.bullet_speed += 5
        elif powerup_type == 'shell':
            self.max_bullets += 1
        elif powerup_type == 'tank':
            self.powerups['extra_life'] += 1
        elif powerup_type == 'star':
            self.hp = min(self.hp + 1, self.max_hp + 2)
    
    def _update_appear_animation(self):
        """更新出场动画"""
        self.appear_frame += 1
        if self.appear_frame >= 30:  # 3帧 * 10
            self.is_appearing = False
            self.appear_frame = 0
    
    def _update_explode_animation(self):
        """更新爆炸动画"""
        self.explode_frame += 1
        if self.explode_frame >= 30:  # 6帧 * 5
            self.is_exploding = False
            self.explode_frame = 0
    
    def draw(self):
        """绘制坦克及相关元素"""
        # 绘制坦克
        if not self.is_appearing:
            if resources:
                image = resources.get_tank_image(self.level, self.direction)
                if image:
                    self.screen.blit(image, (self.x, self.y))
                else:
                    # 如果没有图片，绘制一个简单的矩形
                    pygame.draw.rect(self.screen, (0, 255, 0), (self.x, self.y, TANK_SIZE, TANK_SIZE))
                    # 绘制方向指示器
                    center_x = self.x + TANK_SIZE // 2
                    center_y = self.y + TANK_SIZE // 2
                    if self.direction == Direction.UP:
                        pygame.draw.line(self.screen, (255, 255, 255), (center_x, center_y), (center_x, self.y), 3)
                    elif self.direction == Direction.DOWN:
                        pygame.draw.line(self.screen, (255, 255, 255), (center_x, center_y), (center_x, self.y + TANK_SIZE), 3)
                    elif self.direction == Direction.LEFT:
                        pygame.draw.line(self.screen, (255, 255, 255), (center_x, center_y), (self.x, center_y), 3)
                    elif self.direction == Direction.RIGHT:
                        pygame.draw.line(self.screen, (255, 255, 255), (center_x, center_y), (self.x + TANK_SIZE, center_y), 3)
            else:
                # 如果没有resources，绘制简单图形
                pygame.draw.rect(self.screen, (0, 255, 0), (self.x, self.y, TANK_SIZE, TANK_SIZE))
        
        # 绘制动画
        if self.is_appearing and resources:
            frame = self.appear_frame // 10
            if frame < 3:
                appear_image = resources.images.get(f'appear_{frame}')
                if appear_image:
                    self.screen.blit(appear_image, (self.x, self.y))
        
        if self.is_exploding and resources:
            frame = self.explode_frame // 5
            if frame < 6:
                boom_image = resources.images.get(f'boom_{frame}')
                if boom_image:
                    self.screen.blit(boom_image, (self.x - 25, self.y - 25))
        
        # 绘制子弹
        for bullet in self.bullets:
            bullet.draw()
        
        # 绘制激光
        for laser in self.lasers:
            laser.draw()
    
    def get_rect(self):
        """获取碰撞矩形"""
        return pygame.Rect(self.x, self.y, TANK_SIZE, TANK_SIZE)

# ==================== 敌人坦克类 ====================
class EnemyTank(Tank):
    """敌人坦克类"""
    def __init__(self, x, y, level='level1', screen=None):
        super().__init__(x, y, level, screen)
        self.direction = Direction.DOWN
        self.ai_timer = 0
        self.ai_interval = 60
        self.current_ai_direction = Direction.DOWN
        
        # 根据等级设置属性
        self._set_level_attributes()
    
    def _set_level_attributes(self):
        """根据等级设置属性"""
        level_configs = {
            'level1': {'hp': 1, 'speed': 2, 'max_bullets': 1, 'shoot_interval': 60},
            'level2': {'hp': 2, 'speed': 2, 'max_bullets': 2, 'shoot_interval': 40},
            'level3': {'hp': 3, 'speed': 2, 'max_bullets': 1, 'shoot_interval': 60},
            'level4': {'hp': 4, 'speed': 2, 'max_bullets': 1, 'shoot_interval': 40}
        }
        
        config = level_configs.get(self.level, level_configs['level1'])
        self.hp = config['hp']
        self.speed = config['speed']
        self.max_bullets = config['max_bullets']
        self.shoot_interval = config['shoot_interval']
        self.shoot_timer = 0
    
    def update(self, barriers):
        """更新敌人状态"""
        super().update()
        
        # AI决策
        self.ai_timer += 1
        if self.ai_timer >= self.ai_interval:
            self.current_ai_direction = random.choice(list(Direction)[:-1])  # 排除STOP
            self.ai_timer = 0
        
        # 移动
        self.move(self.current_ai_direction, barriers)
        
        # 射击
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_interval:
            self._shoot_normal()
            self.shoot_timer = 0
    
    def draw(self):
        """绘制敌人坦克"""
        if not self.is_appearing:
            if resources:
                image = resources.get_enemy_image(self.level, self.direction)
                if image:
                    self.screen.blit(image, (self.x, self.y))
                else:
                    # 如果没有图片，绘制一个简单的矩形
                    pygame.draw.rect(self.screen, (255, 0, 0), (self.x, self.y, TANK_SIZE, TANK_SIZE))
            else:
                # 如果没有resources，绘制简单图形
                pygame.draw.rect(self.screen, (255, 0, 0), (self.x, self.y, TANK_SIZE, TANK_SIZE))
        
        # 绘制动画和子弹（复用父类方法）
        if self.is_appearing and resources:
            frame = self.appear_frame // 10
            if frame < 3:
                appear_image = resources.images.get(f'appear_{frame}')
                if appear_image:
                    self.screen.blit(appear_image, (self.x, self.y))
        
        if self.is_exploding and resources:
            frame = self.explode_frame // 5
            if frame < 6:
                boom_image = resources.images.get(f'boom_{frame}')
                if boom_image:
                    self.screen.blit(boom_image, (self.x - 25, self.y - 25))
        
        for bullet in self.bullets:
            bullet.draw()

# ==================== 地图管理器 ====================
class MapManager:
    """地图管理器"""
    def __init__(self, screen):
        self.screen = screen
        self.brick_positions = []
        self.iron_positions = []
        self.tree_positions = []
        self.river_positions = []
        self.river_images = []
        
        # 游戏对象
        self.player_tank = None
        self.enemy_tanks = []
        self.powerups = []
        self.explosions = []
        
        # 游戏状态
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 300
        self.total_enemies_spawned = 0
        self.max_enemies = 20
        self.level4_count = 0
        
        self._init_map()
        self._create_player_tank()
        self._spawn_initial_enemies()
    
    def _init_map(self):
        """初始化地图"""
        self.brick_positions, self.iron_positions, self.tree_positions, river_data = \
            generate_blocks(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # 处理河流
        self.river_positions = river_data
        if resources and 'river' in resources.images:
            for (x, y), (w, h) in river_data:
                river_image = pygame.transform.scale(resources.images['river'], (w, h))
                self.river_images.append(river_image)
    
    def _create_player_tank(self):
        """创建玩家坦克"""
        barriers = self.get_barriers()
        
        # 尝试在安全位置创建
        for _ in range(10):
            x = random.randint(0, SCREEN_WIDTH - TANK_SIZE)
            y = random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT - TANK_SIZE - 100)
            
            if self._is_position_valid(x, y, barriers):
                self.player_tank = Tank(x, y, 'level3', self.screen)
                return
        
        # 默认位置
        self.player_tank = Tank(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, 'level3', self.screen)
    
    def _spawn_initial_enemies(self):
        """生成初始敌人"""
        barriers = self.get_barriers()
        for _ in range(4):
            self._spawn_enemy(barriers)
    
    def _spawn_enemy(self, barriers):
        """生成单个敌人"""
        if self.total_enemies_spawned >= self.max_enemies:
            return
        
        # 尝试找到有效位置
        for _ in range(20):
            x = random.randint(0, SCREEN_WIDTH - TANK_SIZE)
            y = random.randint(50, 250)
            
            if self._is_position_valid(x, y, barriers, check_player=True):
                # 选择敌人类型
                if self.level4_count < 3:
                    enemy_type = random.choice(['level1', 'level2', 'level3', 'level4'])
                    if enemy_type == 'level4':
                        self.level4_count = 0
                    else:
                        self.level4_count += 1
                else:
                    enemy_type = 'level4'
                    self.level4_count = 0
                
                enemy = EnemyTank(x, y, enemy_type, self.screen)
                self.enemy_tanks.append(enemy)
                self.total_enemies_spawned += 1
                return
    
    def _is_position_valid(self, x, y, barriers, check_player=False):
        """检查位置是否有效"""
        new_rect = pygame.Rect(x, y, TANK_SIZE, TANK_SIZE)
        
        # 检查障碍物
        for barrier in barriers:
            if new_rect.colliderect(barrier):
                return False
        
        # 检查其他坦克
        for enemy in self.enemy_tanks:
            if new_rect.colliderect(enemy.get_rect()):
                return False
        
        # 检查玩家坦克
        if check_player and self.player_tank:
            if new_rect.colliderect(self.player_tank.get_rect()):
                return False
        
        return True
    
    def get_barriers(self):
        """获取所有障碍物"""
        barriers = []
        
        # 砖块
        for pos in self.brick_positions:
            barriers.append(pygame.Rect(pos[0], pos[1], TILE_SIZE, TILE_SIZE))
        
        # 铁墙
        for pos in self.iron_positions:
            barriers.append(pygame.Rect(pos[0], pos[1], TILE_SIZE, TILE_SIZE))
        
        return barriers
    
    def update(self):
        """更新地图状态"""
        barriers = self.get_barriers()
        
        # 更新玩家坦克
        self.player_tank.update()
        
        # 更新敌人坦克
        for enemy in self.enemy_tanks[:]:
            enemy.update(barriers)
        
        # 生成新敌人
        self.enemy_spawn_timer += 1
        if (self.enemy_spawn_timer >= self.enemy_spawn_interval and 
            len(self.enemy_tanks) < 8 and self.total_enemies_spawned < self.max_enemies):
            self._spawn_enemy(barriers)
            self.enemy_spawn_timer = 0
            self.enemy_spawn_interval = max(150, self.enemy_spawn_interval - 5)
        
        # 更新道具
        self._update_powerups()
        
        # 检查碰撞
        game_over = self._check_collisions()
        
        # 检查游戏结束条件
        # 杀够一定数量的敌人或玩家坦克被摧毁
        if game_over or self.total_enemies_spawned >= self.max_enemies and not self.enemy_tanks:
            return True
        
        return False
    
    def _update_powerups(self):
        """更新道具"""
        player_rect = self.player_tank.get_rect()
        
        for powerup in self.powerups[:]:
            x, y, ptype = powerup
            powerup_rect = pygame.Rect(x, y, TANK_SIZE, TANK_SIZE)
            
            if player_rect.colliderect(powerup_rect):
                self.player_tank.apply_powerup(ptype)
                self.powerups.remove(powerup)
    
    def _check_collisions(self):
        """检查所有碰撞"""
        # 玩家子弹碰撞检测
        for bullet in self.player_tank.bullets[:]:
            bullet_rect = bullet.get_rect()
            
            # 与砖块碰撞
            for pos in self.brick_positions[:]:
                if bullet_rect.colliderect(pygame.Rect(pos[0], pos[1], TILE_SIZE, TILE_SIZE)):
                    self.brick_positions.remove(pos)
                    self.player_tank.bullets.remove(bullet)
                    if resources and 'bang' in resources.sounds:
                        resources.sounds['bang'].play()
                    break
            else:
                # 与铁墙碰撞
                for pos in self.iron_positions:
                    if bullet_rect.colliderect(pygame.Rect(pos[0], pos[1], TILE_SIZE, TILE_SIZE)):
                        self.player_tank.bullets.remove(bullet)
                        if resources and 'bang' in resources.sounds:
                            resources.sounds['bang'].play()
                        break
                else:
                    # 与敌人碰撞
                    for enemy in self.enemy_tanks[:]:
                        if bullet_rect.colliderect(enemy.get_rect()):
                            damage = getattr(bullet, 'damage', 1)
                            if enemy.take_damage(damage):
                                self.enemy_tanks.remove(enemy)
                                # 特殊敌人掉落道具
                                if enemy.level == 'level4':
                                    ptype = random.choice(['gun', 'shell', 'tank', 'star'])
                                    self.powerups.append((enemy.x, enemy.y, ptype))
                            self.player_tank.bullets.remove(bullet)
                            if resources and 'bang' in resources.sounds:
                                resources.sounds['bang'].play()
                            break
        
        # 玩家激光碰撞检测
        for laser in self.player_tank.lasers:
            for rect in laser.get_collision_rects():
                # 与砖块碰撞
                for pos in self.brick_positions[:]:
                    if rect.colliderect(pygame.Rect(pos[0], pos[1], TILE_SIZE, TILE_SIZE)):
                        self.brick_positions.remove(pos)
                
                # 与敌人碰撞
                for enemy in self.enemy_tanks[:]:
                    if rect.colliderect(enemy.get_rect()):
                        if enemy.take_damage(laser.damage):
                            self.enemy_tanks.remove(enemy)
                            if enemy.level == 'level4':
                                ptype = random.choice(['gun', 'shell', 'tank', 'star'])
                                self.powerups.append((enemy.x, enemy.y, ptype))
        
        # 敌人子弹碰撞检测
        player_rect = self.player_tank.get_rect()
        for enemy in self.enemy_tanks:
            for bullet in enemy.bullets[:]:
                bullet_rect = bullet.get_rect()
                
                # 与砖块碰撞
                for pos in self.brick_positions[:]:
                    if bullet_rect.colliderect(pygame.Rect(pos[0], pos[1], TILE_SIZE, TILE_SIZE)):
                        self.brick_positions.remove(pos)
                        enemy.bullets.remove(bullet)
                        if resources and 'bang' in resources.sounds:
                            resources.sounds['bang'].play()
                        break
                else:
                    # 与铁墙碰撞
                    for pos in self.iron_positions:
                        if bullet_rect.colliderect(pygame.Rect(pos[0], pos[1], TILE_SIZE, TILE_SIZE)):
                            enemy.bullets.remove(bullet)
                            if resources and 'bang' in resources.sounds:
                                resources.sounds['bang'].play()
                            break
                    else:
                        # 与玩家碰撞
                        if bullet_rect.colliderect(player_rect):
                            enemy.bullets.remove(bullet)
                            if self.player_tank.take_damage():
                                return True  # 游戏结束
        
        return False
    
    def draw(self):
        """绘制地图"""
        # 绘制地形
        for pos in self.brick_positions:
            if resources and 'brick' in resources.images:
                self.screen.blit(resources.images['brick'], pos)
            else:
                pygame.draw.rect(self.screen, (139, 69, 19), (pos[0], pos[1], TILE_SIZE, TILE_SIZE))
        
        for pos in self.iron_positions:
            if resources and 'iron' in resources.images:
                self.screen.blit(resources.images['iron'], pos)
            else:
                pygame.draw.rect(self.screen, (192, 192, 192), (pos[0], pos[1], TILE_SIZE, TILE_SIZE))
        
        for i, (pos, _) in enumerate(self.river_positions):
            if i < len(self.river_images):
                self.screen.blit(self.river_images[i], pos)
            else:
                pygame.draw.rect(self.screen, (0, 0, 255), pos)
        
        # 绘制道具
        for x, y, ptype in self.powerups:
            if resources:
                image_key = f'food_{ptype}'
                if image_key in resources.images:
                    self.screen.blit(resources.images[image_key], (x, y))
                else:
                    # 绘制简单的道具标识
                    pygame.draw.circle(self.screen, (255, 255, 0), (x + 25, y + 25), 20)
                    text = self.screen.get_rect()  # 这里可以添加文字标识
            else:
                pygame.draw.circle(self.screen, (255, 255, 0), (x + 25, y + 25), 20)
        
        # 绘制坦克
        self.player_tank.draw()
        for enemy in self.enemy_tanks:
            enemy.draw()
        
        # 绘制树木（最上层）
        for pos in self.tree_positions:
            if resources and 'tree' in resources.images:
                self.screen.blit(resources.images['tree'], pos)
            else:
                pygame.draw.rect(self.screen, (0, 128, 0), (pos[0], pos[1], 60, 70))

# ==================== UI管理器 ====================
class UIManager:
    """UI管理器"""
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("SimHei", 30)
        self.small_font = pygame.font.SysFont("SimHei", 20)
    
    def draw_button(self, text, x, y, w, h, inactive_color, active_color):
        """绘制按钮"""
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        button_rect = pygame.Rect(x, y, w, h)
        is_hover = button_rect.collidepoint(mouse)
        
        # 绘制按钮背景
        color = active_color if is_hover else inactive_color
        pygame.draw.rect(self.screen, color, button_rect, border_radius=8)
        
        # 绘制按钮文字
        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)
        
        return is_hover and click[0]
    
    def draw_main_menu(self):
        """绘制主菜单"""
        # 不在这里清屏，让主循环控制
        
        # 标题
        title = self.font.render("坦克大战", True, (255, 255, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(title, title_rect)
        
        # 说明文字
        info_text = self.small_font.render("TAB切换射击模式 | 空格射击 | 方向键移动", True, (200, 200, 200))
        info_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(info_text, info_rect)
        
        # 开始按钮
        button_w, button_h = 130, 50
        button_x = SCREEN_WIDTH // 2 - button_w // 2
        button_y = SCREEN_HEIGHT // 2 - button_h // 2
        
        return self.draw_button("开始游戏", button_x, button_y, button_w, button_h,
                               (0, 200, 0), (0, 255, 0))
    
    def draw_game_ui(self, player_tank):
        """绘制游戏UI"""
        # 玩家状态
        status_text = (f"生命: {player_tank.hp} | "
                       f"弹速: {player_tank.bullet_speed} | "
                       f"弹数: {player_tank.max_bullets} | "
                       f"模式: {player_tank.shoot_mode.value}")
        text_surface = self.small_font.render(status_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (10, 10))
        
        # 蓄力条
        if player_tank.shoot_mode == ShootMode.CHARGED and player_tank.charging:
            self._draw_charge_bar(player_tank.charge_power / player_tank.max_charge_power)
    
    def _draw_charge_bar(self, charge_rate):
        """绘制蓄力条"""
        bar_width = 200
        bar_height = 20
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = SCREEN_HEIGHT - bar_height - 10
        
        # 背景
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # 进度
        progress_width = int(bar_width * charge_rate)
        if charge_rate < 0.33:
            color = (0, 255, 0)
        elif charge_rate < 0.66:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)
        
        pygame.draw.rect(self.screen, color, 
                        (bar_x, bar_y, progress_width, bar_height))
        
        # 边框
        pygame.draw.rect(self.screen, (255, 255, 255), 
                        (bar_x, bar_y, bar_width, bar_height), 2)
    
    def draw_game_over(self):
        """绘制游戏结束画面"""
        self.screen.fill((0, 0, 0))
        
        if resources and 'gameover' in resources.images:
            scaled_image = pygame.transform.scale(resources.images['gameover'], 
                                                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen.blit(scaled_image, (0, 0))

            hint = self.small_font.render("按任意键返回主菜单", True, (255, 255, 255))
            hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(hint, hint_rect)

# ==================== 主游戏类 ====================
class TankBattle:
    """主游戏类"""
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # 确保资源管理器已初始化
        global resources
        if resources is None:
            resources = ResourceManager()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("坦克大战")
        
        self.clock = pygame.time.Clock()
        self.game_state = GameState.MENU
        print("游戏状态初始化为菜单")
        
        # 初始化管理器
        self.ui_manager = UIManager(self.screen)
        self.map_manager = None
        
        # 输入状态
        self.key_states = {
            Direction.UP: False,
            Direction.DOWN: False,
            Direction.LEFT: False,
            Direction.RIGHT: False,
        }

        print("游戏初始化完成，准备开始主循环")
    
    def run(self):
        """运行游戏主循环"""
        running = True
        
        while running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.game_state == GameState.GAME:
                    self._handle_game_events(event)
                elif self.game_state == GameState.GAMEOVER:
                    if event.type == pygame.KEYDOWN:
                        self.screen.fill((0, 0, 0))
                        self.game_state = GameState.MENU
            
            # 更新游戏状态
            if self.game_state == GameState.MENU:
                self._update_menu()
            elif self.game_state == GameState.GAME:
                self._update_game()
            elif self.game_state == GameState.GAMEOVER:
                self._update_gameover()
            
            # 绘制
            self._draw()
            
            # 控制帧率
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def _handle_game_events(self, event):
        """处理游戏中的事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_state = GameState.MENU
            elif event.key == pygame.K_TAB:
                # 切换射击模式
                self.map_manager.player_tank.switch_shoot_mode()
            elif event.key == pygame.K_SPACE:
                tank = self.map_manager.player_tank
                if tank.shoot_mode == ShootMode.CHARGED:
                    tank.start_charging()
                else:
                    tank.shoot()
        
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                tank = self.map_manager.player_tank
                if tank.shoot_mode == ShootMode.CHARGED:
                    tank.release_charge()
    
    def _update_menu(self):
        """更新菜单状态"""
        # 绘制菜单并检查按钮点击
        if self.ui_manager.draw_main_menu():
            self.game_state = GameState.GAME
            self.map_manager = MapManager(self.screen)
    
    def _update_game(self):
        """更新游戏状态"""
        # 获取按键状态
        keys = pygame.key.get_pressed()
        self.key_states[Direction.UP] = keys[pygame.K_w] or keys[pygame.K_UP]
        self.key_states[Direction.DOWN] = keys[pygame.K_s] or keys[pygame.K_DOWN]
        self.key_states[Direction.LEFT] = keys[pygame.K_a] or keys[pygame.K_LEFT]
        self.key_states[Direction.RIGHT] = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        
        # 确定移动方向
        direction = Direction.STOP
        for dir, pressed in self.key_states.items():
            if pressed:
                direction = dir
                break
        
        # 移动玩家坦克
        barriers = self.map_manager.get_barriers()
        self.map_manager.player_tank.move(direction, barriers)
        
        # 更新蓄力
        self.map_manager.player_tank.update_charge()
        
        # 更新地图
        if self.map_manager.update():
            self.game_state = GameState.GAMEOVER
    
    def _update_gameover(self):
        """更新游戏结束状态"""
        pass
    
    def _draw(self):
        """绘制游戏画面"""
        # 总是先清屏
        if not self.game_state == GameState.MENU:
            self.screen.fill((0, 0, 0))
        
        if self.game_state == GameState.MENU:
            # 菜单状态下不需要额外绘制，_update_menu会处理
            # 事实上 没有绘制
            pass # 
        elif self.game_state == GameState.GAME:
            self.map_manager.draw()
            self.ui_manager.draw_game_ui(self.map_manager.player_tank)
        elif self.game_state == GameState.GAMEOVER:
            self.ui_manager.draw_game_over()
        
        pygame.display.flip()

# ==================== 程序入口 ====================
if __name__ == "__main__":
    try:
        print("正在启动坦克大战...")
        print(f"Python版本: {sys.version}")
        print(f"Pygame版本: {pygame.version.ver}")
        print(f"当前目录: {os.getcwd()}")
        
        # 初始化资源管理器
        print("正在加载资源...")
        resources = ResourceManager()
        print("资源加载完成")
        
        # 启动游戏
        print("正在启动游戏...")
        game = TankBattle()
        game.run()
    except Exception as e:
        print(f"游戏启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")