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
        bricks = [(x, y) for x in range(100, width - 100, 100)
                  for y in range(100, height // 2, 100)]
        irons = [(x, y) for x in range(200, width - 200, 200)
                 for y in range(150, height // 2, 150)]
        trees = [(x, y) for x in range(300, width - 300, 300)
                 for y in range(200, height // 2, 200)]
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

        possible_base_dirs = [
            os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '',
            os.getcwd(),
            os.path.dirname(os.getcwd()),
            ".",
        ]

        base_dir = None
        for dir_path in possible_base_dirs:
            if dir_path and os.path.exists(os.path.join(dir_path, "images")):
                base_dir = dir_path
                print(f"找到资源目录: {base_dir}")
                break

        if base_dir is None:
            print("警告: 无法找到资源目录，游戏将使用默认图形")
            base_dir = os.getcwd()

        # 定义所有图片路径
        all_image_paths = {
            # 坦克
            **{f'tank_L{l}_{d}': f"images/tank_L{l}_{d}.png" for l in range(1, 4) for d in range(1, 5)},
            # 子弹
            **{f'bullet_{d.value}': f"images/bullet_{d.value}.png" for d in Direction if d != Direction.STOP},
            # 敌人
            **{f'enemy_{l}_{d}': f"images/enemy_{l}_{d}.png" for l in range(1, 5) for d in range(1, 5)},
            # 特效
            **{f'appear_{i}': f"images/appear_{i}.png" for i in range(3)},
            **{f'boom_{i}': f"images/boom_{i}.png" for i in range(6)},
            # 地形
            'brick': "images/brick.png", 'iron': "images/iron.png",
            'river': "images/river.png", 'tree': "images/tree.png",
            # 道具
            'food_gun': "images/food_gun.png", 'food_shell': "images/food_shell.png",
            'food_tank': "images/food_tank.png", 'food_star': "images/food_star.png",
            # 其他
            'gameover': "images/gameover.png",
        }

        loaded_count = 0
        for name, path in all_image_paths.items():
            full_path = os.path.join(base_dir, path)
            try:
                self.images[name] = pygame.image.load(full_path)
                loaded_count += 1
            except pygame.error:
                placeholder = pygame.Surface((TANK_SIZE, TANK_SIZE))
                placeholder.fill((255, 0, 255)) # 使用亮紫色作为占位符颜色
                self.images[name] = placeholder

        print(f"成功加载 {loaded_count}/{len(all_image_paths)} 个图片")

        if 'tree' in self.images:
            try:
                self.images['tree'] = pygame.transform.scale(self.images['tree'], (60, 70))
            except Exception: pass

        sound_files = {
            'fire': "music/fire.wav",
            'enemy_fire': "music/Gunfire.wav",
            'bang': "music/bang.wav",
        }

        class DummySound:
            def play(self): pass

        for name, path in sound_files.items():
            full_path = os.path.join(base_dir, path)
            try:
                self.sounds[name] = pygame.mixer.Sound(full_path)
            except Exception:
                self.sounds[name] = DummySound()

    def get_tank_image(self, level, direction):
        dir_map = {Direction.UP: '1', Direction.DOWN: '2', Direction.LEFT: '3', Direction.RIGHT: '4'}
        key = f'tank_L{level[-1]}_{dir_map.get(direction, "1")}'
        return self.images.get(key, self.images.get('tank_L1_1'))

    def get_enemy_image(self, level, direction):
        dir_map = {Direction.UP: '1', Direction.DOWN: '2', Direction.LEFT: '3', Direction.RIGHT: '4'}
        key = f'enemy_{level[-1]}_{dir_map.get(direction, "1")}'
        return self.images.get(key, self.images.get('enemy_1_1'))

    def get_bullet_image(self, direction):
        key = f'bullet_{direction.value}'
        return self.images.get(key, self.images.get('bullet_up'))

# ==================== 武器系统 ====================
class Weapon(ABC):
    def __init__(self, owner):
        self.owner = owner
        self.cooldown = 0
        self.max_cooldown = 30
    
    @abstractmethod
    def shoot(self): pass
    
    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

class Bullet:
    def __init__(self, x, y, direction, screen, speed=10, damage=1):
        self.direction = direction
        self.screen = screen
        self.speed = speed
        self.damage = damage
        self.image = resources.get_bullet_image(direction)
        self.rect = self.image.get_rect(center=(x, y))
        self._set_velocity()
    
    def _set_velocity(self):
        velocities = {
            Direction.LEFT: (-self.speed, 0), Direction.RIGHT: (self.speed, 0),
            Direction.UP: (0, -self.speed), Direction.DOWN: (0, self.speed)
        }
        self.velocity_x, self.velocity_y = velocities.get(self.direction, (0, -self.speed))
    
    def update(self):
        self.rect.move_ip(self.velocity_x, self.velocity_y)
        return self.screen.get_rect().colliderect(self.rect)
    
    def draw(self):
        self.screen.blit(self.image, self.rect)
    
    def get_rect(self):
        return self.rect

class ChargedBullet(Bullet):
    def __init__(self, x, y, direction, screen, charge_rate):
        super().__init__(x, y, direction, screen)
        self.charge_rate = max(0.1, charge_rate)
        self.speed *= (1 + self.charge_rate * 2)
        self.damage = 1 + int(self.charge_rate * 3)
        self._set_velocity()
        if self.charge_rate > 0.3:
            scale = 1 + self.charge_rate
            self.image = pygame.transform.smoothscale(
                self.image, (int(self.rect.width * scale), int(self.rect.height * scale))
            )
            self.rect = self.image.get_rect(center=self.rect.center)

class LaserBeam:
    def __init__(self, x, y, direction, screen, duration=10):
        self.start_pos = (x, y)
        self.direction = direction
        self.screen = screen
        self.duration = duration
        self.damage = 5
        self.width = 10
        self._calculate_endpoints()
    
    def _calculate_endpoints(self):
        if self.direction == Direction.UP: self.end_pos = (self.start_pos[0], 0)
        elif self.direction == Direction.DOWN: self.end_pos = (self.start_pos[0], SCREEN_HEIGHT)
        elif self.direction == Direction.LEFT: self.end_pos = (0, self.start_pos[1])
        elif self.direction == Direction.RIGHT: self.end_pos = (SCREEN_WIDTH, self.start_pos[1])
    
    def update(self):
        self.duration -= 1
        return self.duration > 0
    
    def draw(self):
        # **OPTIMIZATION**: 绘制多层不同颜色的线条来模拟光晕，避免使用低效的alpha混合
        main_color = (255, 255, 255) if self.duration % 4 > 1 else (255, 200, 200)
        glow_color_1 = (180, 100, 100)
        glow_color_2 = (100, 50, 50)
        
        pygame.draw.line(self.screen, glow_color_2, self.start_pos, self.end_pos, self.width + 8)
        pygame.draw.line(self.screen, glow_color_1, self.start_pos, self.end_pos, self.width + 4)
        pygame.draw.line(self.screen, main_color, self.start_pos, self.end_pos, self.width)
    
    def get_line(self):
        return self.start_pos, self.end_pos

# ==================== 坦克类 ====================
class Tank:
    # **OPTIMIZATION**: 使用常量代替魔法数字
    APPEAR_ANIMATION_SPEED = 10
    APPEAR_FRAME_COUNT = 3
    EXPLODE_ANIMATION_SPEED = 5
    EXPLODE_FRAME_COUNT = 6
    
    def __init__(self, x, y, level='level3', screen=None):
        self.rect = pygame.Rect(x, y, TANK_SIZE, TANK_SIZE)
        self.screen = screen
        self.level = level
        self.direction = Direction.UP
        self.speed = 5
        self.hp = 3
        self.max_hp = 3
        
        self.shoot_mode = ShootMode.NORMAL
        self.bullets = []
        self.lasers = []
        self.max_bullets = 1
        self.bullet_speed = 10
        self.shoot_cooldown = 0
        self.max_cooldown = 30
        
        self.charging = False
        self.charge_power = 0
        self.max_charge_power = 100
        self.charge_speed = 4
        
        self.is_appearing = True
        self.appear_frame = 0
        self.appear_duration = self.APPEAR_FRAME_COUNT * self.APPEAR_ANIMATION_SPEED
        self.is_exploding = False
        self.explode_frame = 0
        self.explode_duration = self.EXPLODE_FRAME_COUNT * self.EXPLODE_ANIMATION_SPEED
        
        self.powerups = {'extra_life': 0, 'bullet_speed': 0, 'max_bullets': 0}
    
    def update(self):
        if self.shoot_cooldown > 0: self.shoot_cooldown -= 1
        self.bullets = [b for b in self.bullets if b.update()]
        self.lasers = [l for l in self.lasers if l.update()]
        if self.is_appearing: self._update_appear_animation()
        if self.is_exploding: self._update_explode_animation()
    
    def move(self, direction, barriers):
        # **OPTIMIZATION**: 返回一个布尔值，表示是否成功移动，用于改进AI
        if direction == Direction.STOP: return True
        self.direction = direction
        
        dx, dy = 0, 0
        if direction == Direction.LEFT: dx = -self.speed
        elif direction == Direction.RIGHT: dx = self.speed
        elif direction == Direction.UP: dy = -self.speed
        elif direction == Direction.DOWN: dy = self.speed
        
        self.rect.move_ip(dx, dy)
        
        # 碰撞检测
        if self.rect.collidelist(barriers) != -1:
            self.rect.move_ip(-dx, -dy) # 发生碰撞，移回原位
            return False
            
        # 边界检测
        self.rect.clamp_ip(self.screen.get_rect())
        return True
    
    def shoot(self):
        if self.shoot_cooldown > 0: return
        if self.shoot_mode == ShootMode.NORMAL: self._shoot_normal()
        elif self.shoot_mode == ShootMode.LASER: self._shoot_laser()
    
    def start_charging(self):
        if self.shoot_mode == ShootMode.CHARGED and self.shoot_cooldown <= 0:
            self.charging = True
            self.charge_power = 0
    
    def release_charge(self):
        if self.charging:
            self.charging = False
            self._shoot_charged(self.charge_power / self.max_charge_power)
            self.charge_power = 0
    
    def update_charge(self):
        if self.charging:
            self.charge_power = min(self.charge_power + self.charge_speed, self.max_charge_power)
    
    def _shoot_normal(self):
        if len(self.bullets) < self.max_bullets:
            bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction, self.screen, self.bullet_speed)
            self.bullets.append(bullet)
            self.shoot_cooldown = self.max_cooldown
            resources.sounds['fire'].play()
    
    def _shoot_charged(self, charge_rate):
        if len(self.bullets) < self.max_bullets:
            bullet = ChargedBullet(self.rect.centerx, self.rect.centery, self.direction, self.screen, charge_rate)
            self.bullets.append(bullet)
            self.shoot_cooldown = int(self.max_cooldown * (1.5 + charge_rate))
            resources.sounds['fire'].play()
    
    def _shoot_laser(self):
        laser = LaserBeam(self.rect.centerx, self.rect.centery, self.direction, self.screen)
        self.lasers.append(laser)
        self.shoot_cooldown = self.max_cooldown * 2
    
    def switch_shoot_mode(self):
        modes = list(ShootMode)
        current_index = modes.index(self.shoot_mode)
        self.shoot_mode = modes[(current_index + 1) % len(modes)]
        self.charging = False
        self.charge_power = 0
    
    def take_damage(self, damage=1):
        self.hp -= damage
        if not self.is_exploding:
            self.is_exploding = True
            self.explode_frame = 0
        return self.hp <= 0
    
    def apply_powerup(self, powerup_type):
        if powerup_type == 'gun': self.bullet_speed = min(self.bullet_speed + 5, 25)
        elif powerup_type == 'shell': self.max_bullets = min(self.max_bullets + 1, 4)
        elif powerup_type == 'tank': self.powerups['extra_life'] += 1
        elif powerup_type == 'star': self.hp = min(self.hp + 1, self.max_hp + 2)
    
    def _update_appear_animation(self):
        self.appear_frame += 1
        if self.appear_frame >= self.appear_duration:
            self.is_appearing = False
    
    def _update_explode_animation(self):
        self.explode_frame += 1
        if self.explode_frame >= self.explode_duration:
            self.is_exploding = False
    
    def draw(self):
        if not self.is_appearing:
            image = resources.get_tank_image(self.level, self.direction)
            self.screen.blit(image, self.rect)
        
        if self.is_appearing:
            frame_index = self.appear_frame // self.APPEAR_ANIMATION_SPEED
            if frame_index < self.APPEAR_FRAME_COUNT:
                appear_image = resources.images.get(f'appear_{frame_index}')
                if appear_image: self.screen.blit(appear_image, self.rect)
        
        if self.is_exploding:
            frame_index = self.explode_frame // self.EXPLODE_ANIMATION_SPEED
            if frame_index < self.EXPLODE_FRAME_COUNT:
                boom_image = resources.images.get(f'boom_{frame_index}')
                if boom_image:
                    boom_rect = boom_image.get_rect(center=self.rect.center)
                    self.screen.blit(boom_image, boom_rect)
        
        for bullet in self.bullets: bullet.draw()
        for laser in self.lasers: laser.draw()
    
    def get_rect(self): return self.rect

# ==================== 敌人坦克类 ====================
class EnemyTank(Tank):
    def __init__(self, x, y, level='level1', screen=None):
        super().__init__(x, y, level, screen)
        self.direction = Direction.DOWN
        self.current_ai_direction = Direction.DOWN
        self.ai_interval = random.randint(50, 80)
        self.ai_timer = 0
        self._set_level_attributes()
    
    def _set_level_attributes(self):
        configs = {
            'level1': {'hp': 1, 'speed': 2, 'max_bullets': 1, 'shoot_interval': 80},
            'level2': {'hp': 2, 'speed': 3, 'max_bullets': 1, 'shoot_interval': 60},
            'level3': {'hp': 3, 'speed': 2, 'max_bullets': 2, 'shoot_interval': 50},
            'level4': {'hp': 4, 'speed': 1, 'max_bullets': 1, 'shoot_interval': 40}
        }
        config = configs.get(self.level, configs['level1'])
        self.hp, self.speed, self.max_bullets = config['hp'], config['speed'], config['max_bullets']
        self.shoot_interval = random.randint(config['shoot_interval'] - 10, config['shoot_interval'] + 10)
        self.shoot_timer = 0
    
    def update(self, barriers):
        super().update() # 更新子弹等
        
        # **OPTIMIZATION**: 改进的AI逻辑
        self.ai_timer += 1
        moved_successfully = self.move(self.current_ai_direction, barriers)
        
        # 如果撞墙或计时器到时，则重新决策
        if not moved_successfully or self.ai_timer >= self.ai_interval:
            self.current_ai_direction = random.choice(list(Direction)[:-1])
            self.ai_timer = 0
            self.ai_interval = random.randint(50, 80)
        
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_interval:
            self._shoot_normal()
            self.shoot_timer = 0
    
    def draw(self):
        if not self.is_appearing:
            image = resources.get_enemy_image(self.level, self.direction)
            self.screen.blit(image, self.rect)
        
        # 复用父类的动画和子弹绘制
        super().draw()

# ==================== 地图管理器 ====================
class MapManager:
    def __init__(self, screen):
        self.screen = screen
        self.brick_positions, self.iron_positions, self.tree_positions, river_data = \
            generate_blocks(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # **OPTIMIZATION**: 预计算碰撞矩形列表
        self.brick_rects = [pygame.Rect(pos[0], pos[1], TILE_SIZE, TILE_SIZE) for pos in self.brick_positions]
        self.iron_rects = [pygame.Rect(pos[0], pos[1], TILE_SIZE, TILE_SIZE) for pos in self.iron_positions]
        
        self.river_images = []
        if resources and 'river' in resources.images:
            for (x, y), (w, h) in river_data:
                img = pygame.transform.scale(resources.images['river'], (w, h))
                self.river_images.append((img, (x, y)))
        
        self.player_tank = None
        self.enemy_tanks = []
        self.powerups = []
        
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 300
        self.total_enemies_spawned = 0
        self.max_enemies_on_screen = 6
        self.max_enemies_total = 20
        self.level4_spawn_chance = 0.1
        
        self._create_player_tank()
        self._spawn_initial_enemies()
    
    def _create_player_tank(self):
        self.player_tank = Tank(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, 'level3', self.screen)
    
    def _spawn_initial_enemies(self):
        for _ in range(4): self._spawn_enemy()
    
    def _spawn_enemy(self):
        if self.total_enemies_spawned >= self.max_enemies_total or len(self.enemy_tanks) >= self.max_enemies_on_screen:
            return
            
        spawn_points = [(50, 50), (SCREEN_WIDTH // 2, 50), (SCREEN_WIDTH - 100, 50)]
        x, y = random.choice(spawn_points)
        
        if random.random() < self.level4_spawn_chance:
            enemy_type = 'level4'
            self.level4_spawn_chance = 0.05 # 降低下次出现几率
        else:
            enemy_type = random.choice(['level1', 'level2', 'level3'])
            self.level4_spawn_chance += 0.02

        enemy = EnemyTank(x, y, enemy_type, self.screen)
        self.enemy_tanks.append(enemy)
        self.total_enemies_spawned += 1
    
    def get_all_barriers(self):
        return self.brick_rects + self.iron_rects
    
    def update(self):
        barriers = self.get_all_barriers()
        self.player_tank.update()
        for enemy in self.enemy_tanks: enemy.update(barriers)
        
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self._spawn_enemy()
            self.enemy_spawn_timer = 0
        
        self._update_powerups()
        game_over = self._check_collisions()
        
        if game_over or (self.total_enemies_spawned >= self.max_enemies_total and not self.enemy_tanks):
            return True # 游戏胜利或失败
        return False
    
    def _update_powerups(self):
        for powerup_rect, ptype in self.powerups[:]:
            if self.player_tank.get_rect().colliderect(powerup_rect):
                self.player_tank.apply_powerup(ptype)
                self.powerups.remove((powerup_rect, ptype))
    
    def _check_collisions(self):
        # **OPTIMIZATION**: 使用高效的碰撞检测函数
        self._check_bullet_collisions(self.player_tank, self.enemy_tanks, is_player=True)
        for enemy in self.enemy_tanks:
            if self._check_bullet_collisions(enemy, [self.player_tank], is_player=False):
                return True # 玩家被击败，游戏结束
        self._check_laser_collisions()
        return self.player_tank.hp <= 0

    def _check_bullet_collisions(self, shooter, targets, is_player):
        target_rects = [t.get_rect() for t in targets]
        for bullet in shooter.bullets[:]:
            collided = False
            # 与砖块碰撞
            hit_indices = bullet.get_rect().collidelistall(self.brick_rects)
            if hit_indices:
                for i in sorted(hit_indices, reverse=True):
                    del self.brick_rects[i]
                collided = True
            # 与铁墙碰撞
            if not collided and bullet.get_rect().collidelist(self.iron_rects) != -1:
                if isinstance(bullet, ChargedBullet) and bullet.charge_rate > 0.8:
                    pass # 蓄力弹可摧毁铁墙，此处省略
                collided = True
            # 与目标坦克碰撞
            if not collided:
                hit_index = bullet.get_rect().collidelist(target_rects)
                if hit_index != -1:
                    target = targets[hit_index]
                    if target.take_damage(bullet.damage):
                        if is_player and target.level == 'level4':
                            ptype = random.choice(['gun', 'shell', 'tank', 'star'])
                            powerup_rect = pygame.Rect(target.rect.topleft, (TANK_SIZE, TANK_SIZE))
                            self.powerups.append((powerup_rect, ptype))
                        targets.pop(hit_index)
                    collided = True
            if collided:
                shooter.bullets.remove(bullet)
                resources.sounds['bang'].play()
        return not targets if not is_player else False

    def _check_laser_collisions(self):
        # **OPTIMIZATION**: 使用 clipline 进行高效的线段-矩形碰撞检测
        for laser in self.player_tank.lasers:
            laser_line = laser.get_line()
            
            for i in range(len(self.brick_rects) - 1, -1, -1):
                if self.brick_rects[i].clipline(laser_line):
                    del self.brick_rects[i]

            for i in range(len(self.enemy_tanks) - 1, -1, -1):
                enemy = self.enemy_tanks[i]
                if enemy.get_rect().clipline(laser_line):
                    if enemy.take_damage(laser.damage):
                        if enemy.level == 'level4':
                            ptype = random.choice(['gun', 'shell', 'tank', 'star'])
                            powerup_rect = pygame.Rect(enemy.rect.topleft, (TANK_SIZE, TANK_SIZE))
                            self.powerups.append((powerup_rect, ptype))
                        del self.enemy_tanks[i]

    def draw(self):
        for rect in self.brick_rects: self.screen.blit(resources.images['brick'], rect)
        for rect in self.iron_rects: self.screen.blit(resources.images['iron'], rect)
        for img, pos in self.river_images: self.screen.blit(img, pos)
        
        for powerup_rect, ptype in self.powerups:
            image_key = f'food_{ptype}'
            if image_key in resources.images:
                self.screen.blit(resources.images[image_key], powerup_rect)
        
        self.player_tank.draw()
        for enemy in self.enemy_tanks: enemy.draw()
        
        for pos in self.tree_positions:
            self.screen.blit(resources.images['tree'], pos)

# ==================== UI管理器 ====================
class UIManager:
    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()
        self.font = pygame.font.SysFont("SimHei", 30)
        self.small_font = pygame.font.SysFont("SimHei", 20)
    
    def draw_button(self, text, rect, inactive_color, active_color, is_hover):
        color = active_color if is_hover else inactive_color
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        text_surface = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def draw_main_menu(self, is_hovering_start):
        title = self.font.render("坦克大战", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)))
        info_text = self.small_font.render("TAB切换射击模式 | 空格射击 | 方向键移动", True, (200, 200, 200))
        self.screen.blit(info_text, info_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))
        
        button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 65, SCREEN_HEIGHT // 2 - 25, 130, 50)
        self.draw_button("开始游戏", button_rect, (0, 200, 0), (0, 255, 0), is_hovering_start)

    def draw_game_ui(self, player_tank):
        status_text = (f"生命: {player_tank.hp} | "
                       f"弹速: {player_tank.bullet_speed} | "
                       f"弹数: {player_tank.max_bullets} | "
                       f"模式: {player_tank.shoot_mode.value}")
        text_surface = self.small_font.render(status_text, True, (255, 255, 255), (0,0,0))
        self.screen.blit(text_surface, (10, 10))
        
        if player_tank.shoot_mode == ShootMode.CHARGED and player_tank.charging:
            self._draw_charge_bar(player_tank.charge_power / player_tank.max_charge_power)

    def _draw_charge_bar(self, charge_rate):
        bar_rect = pygame.Rect((SCREEN_WIDTH - 200) // 2, SCREEN_HEIGHT - 30, 200, 20)
        pygame.draw.rect(self.screen, (100, 100, 100), bar_rect)
        progress_width = int(bar_rect.width * charge_rate)
        color = (0, 255, 0) if charge_rate < 0.33 else (255, 255, 0) if charge_rate < 0.66 else (255, 0, 0)
        pygame.draw.rect(self.screen, color, (bar_rect.x, bar_rect.y, progress_width, bar_rect.height))
        pygame.draw.rect(self.screen, (255, 255, 255), bar_rect, 2)
    
    def draw_game_over(self):
        if 'gameover' in resources.images:
            img = resources.images['gameover']
            self.screen.blit(img, img.get_rect(center=self.screen.get_rect().center))
        hint = self.small_font.render("按任意键返回主菜单", True, (255, 255, 255))
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)))

# ==================== 主游戏类 ====================
class TankBattle:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        global resources
        if resources is None: resources = ResourceManager()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("坦克大战 - 优化版")
        self.clock = pygame.time.Clock()
        self.game_state = GameState.MENU
        
        self.ui_manager = UIManager(self.screen)
        self.map_manager = None
        self.is_start_hovered = False

    def run(self):
        # **OPTIMIZATION**: 重构主循环，分离事件、更新和绘制
        running = True
        while running:
            # 1. 事件处理
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                self._handle_events(event)
            
            # 2. 逻辑更新
            self._update()
            
            # 3. 画面绘制
            self._draw()
            
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def _handle_events(self, event):
        if self.game_state == GameState.GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.game_state = GameState.MENU
                elif event.key == pygame.K_TAB: self.map_manager.player_tank.switch_shoot_mode()
                elif event.key == pygame.K_SPACE:
                    tank = self.map_manager.player_tank
                    if tank.shoot_mode == ShootMode.CHARGED: tank.start_charging()
                    else: tank.shoot()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    tank = self.map_manager.player_tank
                    if tank.shoot_mode == ShootMode.CHARGED: tank.release_charge()
        elif self.game_state == GameState.GAMEOVER:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.game_state = GameState.MENU
        elif self.game_state == GameState.MENU:
             if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_start_hovered:
                self.game_state = GameState.GAME
                self.map_manager = MapManager(self.screen)

    def _update(self):
        if self.game_state == GameState.GAME and self.map_manager:
            keys = pygame.key.get_pressed()
            direction = Direction.STOP
            if keys[pygame.K_w] or keys[pygame.K_UP]: direction = Direction.UP
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]: direction = Direction.DOWN
            elif keys[pygame.K_a] or keys[pygame.K_LEFT]: direction = Direction.LEFT
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]: direction = Direction.RIGHT
            
            self.map_manager.player_tank.move(direction, self.map_manager.get_all_barriers())
            self.map_manager.player_tank.update_charge()
            
            if self.map_manager.update():
                self.game_state = GameState.GAMEOVER
        elif self.game_state == GameState.MENU:
            # **OPTIMIZATION**: 将UI逻辑判断放在更新阶段
            button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 65, SCREEN_HEIGHT // 2 - 25, 130, 50)
            self.is_start_hovered = button_rect.collidepoint(pygame.mouse.get_pos())
    
    def _draw(self):
        self.screen.fill((0, 0, 0)) # 统一清屏
        
        if self.game_state == GameState.MENU:
            self.ui_manager.draw_main_menu(self.is_start_hovered)
        elif self.game_state == GameState.GAME and self.map_manager:
            self.map_manager.draw()
            self.ui_manager.draw_game_ui(self.map_manager.player_tank)
        elif self.game_state == GameState.GAMEOVER:
            self.ui_manager.draw_game_over()
        
        pygame.display.flip()

# ==================== 程序入口 ====================
if __name__ == "__main__":
    try:
        print("正在启动坦克大战...")
        game = TankBattle()
        game.run()
    except Exception as e:
        print(f"游戏发生严重错误: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")
