import numpy as np
import random
from typing import Tuple, List

def generate_blocks(map_width, map_height) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]], List[Tuple[int, int]], List[Tuple[Tuple[int, int], Tuple[int, int]]]]:
    width, height = map_width, map_height
        
    occupied = np.zeros((height, width), dtype=bool)
    
    def mark_occupied(x: int, y: int, w: int, h: int) -> bool:
        if x < 0 or y < 0 or x + w > width or y + h > height:
            return False
        if np.any(occupied[y:y+h, x:x+w]):
            return False
        occupied[y:y+h, x:x+w] = True
        return True
    
    # 生成类型1和类型2块 (各60个)
    grid_size = 24
    grid_cols = width // grid_size
    grid_rows = height // grid_size
    grid_positions = [(i * grid_size, j * grid_size) 
                     for i in range(grid_cols) for j in range(grid_rows)]
    random.shuffle(grid_positions)
    
    # 生成2-4个相邻块组成的图形
    def generate_cluster(positions: list, max_blocks: int) -> List[Tuple[int, int]]:
        blocks = []
        while len(blocks) < max_blocks and len(positions) > 1:
            size = random.randint(2, 4)
            start_idx = random.randint(0, len(positions) - 1)
            start_x, start_y = positions.pop(start_idx)
            cluster = [(start_x, start_y)]
            
            directions = [(grid_size, 0), (-grid_size, 0), 
                         (0, grid_size), (0, -grid_size)]
            
            for _ in range(size - 1):
                added = False
                random.shuffle(cluster)
                for cx, cy in cluster:
                    random.shuffle(directions)
                    for dx, dy in directions:
                        nx, ny = cx + dx, cy + dy
                        if (nx, ny) in positions and 0 <= nx <= width-grid_size and 0 <= ny <= height-grid_size:
                            idx = positions.index((nx, ny))
                            positions.pop(idx)
                            cluster.append((nx, ny))
                            added = True
                            break
                    if added:
                        break
                if not added:
                    break
            blocks.extend(cluster)
            if len(blocks) >= max_blocks:
                break
        return blocks[:max_blocks]  # 确保不超过最大数量
    
    # 生成类型1和类型2块 (各60个)
    type1_blocks = generate_cluster(grid_positions.copy(), 60)
    type2_blocks = generate_cluster(grid_positions.copy(), 60)
    
    # 标记占用
    for blocks in [type1_blocks, type2_blocks]:
        for x, y in blocks:
            mark_occupied(x, y, grid_size, grid_size)
    
    # 生成类型3块 (5个)
    type3_blocks = []
    for _ in range(5):
        placed = False
        for _ in range(100):  # 最多重试100次
            x = random.randint(0, width - 60)
            y = random.randint(0, height - 70)
            if mark_occupied(x, y, 60, 70):
                type3_blocks.append((x, y))
                placed = True
                break
        if not placed:  # 如果空间不足，放在左上角
            type3_blocks.append((0, 0))
    
    # 生成河流 (2个区域)
    river_list = []
    river_shapes = [
        # 水平直线
        lambda x, y: [((x, y), (min(300, width-x), 20))],
        # 垂直直线
        lambda x, y: [((x, y), (20, min(300, height-y)))],
        # L形
        lambda x, y: [
            ((x, y), (seg1_len, 20)),
            ((x + seg1_len - 20, y), (20, seg2_len))
        ],
        # 反L形
        lambda x, y: [
            ((x, y), (20, seg1_len)),
            ((x, y + seg1_len - 20), (seg2_len, 20))
        ]
    ]
    
    # 生成两个河流区域
    for _ in range(2):
        placed = False
        for attempt in range(100):  # 最多重试100次
            shape_idx = random.randint(0, 3)
            x = random.randint(0, width - 300)
            y = random.randint(0, height - 300)
            seg1_len = random.randint(150, 300)
            seg2_len = random.randint(150, 300)
            
            shape_func = river_shapes[shape_idx]
            segments = shape_func(x, y)
            
            # 检查所有段是否可放置
            valid = True
            for (sx, sy), (sw, sh) in segments:
                if sx + sw > width or sy + sh > height:
                    valid = False
                    break
                if np.any(occupied[sy:sy+sh, sx:sx+sw]):
                    valid = False
                    break
            
            if valid:
                # 标记占用
                for (sx, sy), (sw, sh) in segments:
                    if not mark_occupied(sx, sy, sw, sh):
                        valid = False
                        break
                if valid:
                    river_list.extend(segments)
                    placed = True
                    break
        
        if not placed:  # 如果无法放置，使用简单河流
            # 尝试在四个角落放置简单河流
            corners = [(0, 300), (0, 400), (400, 0), (400, 500)]
            for x, y in corners:
                if mark_occupied(x, y, 200, 20):
                    river_list.append(((x, y), (200, 20)))
                    placed = True
                    break
            if not placed:  # 如果所有角落都失败，放在左上角
                river_list.append(((0, 0), (200, 20)))
    
    return type1_blocks, type2_blocks, type3_blocks, river_list



