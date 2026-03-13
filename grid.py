import random
import math
from cell import Cell

class Grid:
    def __init__(self, width, height, terrain_config=None):
        self.width = width
        self.height = height
        # 初始化为全森林格子（地形类型为 FOREST）
        self.cells = [[Cell(terrain_type=Cell.FOREST) for _ in range(width)] for _ in range(height)]

        if terrain_config and terrain_config.terrain_enabled:
            self.generate_terrain(terrain_config)

    # ------------------ 基础网格操作方法 ------------------
    def get_cell(self, x, y):
        """获取指定坐标的格子对象"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x]
        return None

    def set_cell_state(self, x, y, state, burn_duration=None):
        """设置指定坐标格子的状态"""
        cell = self.get_cell(x, y)
        if cell is None:
            return
        if state == Cell.BURNING:
            if burn_duration is not None:
                cell.ignite(burn_duration)
            else:
                raise ValueError("设置燃烧状态时必须提供 burn_duration")
        else:
            cell.state = state
            if state != Cell.BURNING:
                cell.burn_time_remaining = 0

    def get_neighbors(self, x, y):
        """返回邻居列表，每个元素为 (nx, ny, cell)"""
        neighbors = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                cell = self.get_cell(nx, ny)
                if cell:
                    neighbors.append((nx, ny, cell))
        return neighbors

    def get_all_cells(self):
        """返回所有格子对象的迭代器"""
        for row in self.cells:
            for cell in row:
                yield cell

    def count_burning(self):
        """统计当前正在燃烧的格子数"""
        count = 0
        for cell in self.get_all_cells():
            if cell.is_burning():
                count += 1
        return count

    def set_initial_fire(self, x, y, burn_duration):
        """便捷方法：设置初始火源"""
        self.set_cell_state(x, y, Cell.BURNING, burn_duration)

    def reset_states(self):
        """重置所有格子的状态为健康（保留地形）"""
        for cell in self.get_all_cells():
            cell.state = Cell.HEALTHY
            cell.burn_time_remaining = 0

    # ------------------ 地形生成方法 ------------------
    def generate_terrain(self, config):
        """根据配置生成裸地和水域，保证森林面积≥50%"""
        old_state = random.getstate()
        if config.terrain_seed is not None:
            random.seed(config.terrain_seed)
        random.seed(config.terrain_seed)  # 固定种子，结果可重复

        # --- 1. 裸地生成 ---
        # 点状裸地
        for _ in range(config.bare_random_points):
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            self.cells[y][x].terrain_type = Cell.BARE

        # 块状裸地（圆形）
        for _ in range(config.bare_patches):
            cx = random.randint(0, self.width-1)
            cy = random.randint(0, self.height-1)
            r = config.bare_patch_radius
            self._fill_circle(cx, cy, r, Cell.BARE)

        # --- 2. 水域生成 ---
        if config.water_enabled:
            # 河流生成（优先于湖泊，但两者可共存）
            if config.generate_river:
                self._generate_river(config.river_width)

            # 湖泊生成
            if config.generate_lake:
                cx = random.randint(0, self.width-1)
                cy = random.randint(0, self.height-1)
                self._fill_circle(cx, cy, config.lake_radius, Cell.WATER)

        # --- 3. 森林面积检查（如果不足50%，则尝试缩减不可燃区域）---
        self._ensure_forest_cover(config)
        random.setstate(old_state)

    # ------------------ 辅助方法 ------------------
    def _fill_circle(self, cx, cy, radius, terrain_type):
        """以(cx,cy)为中心，填充半径为radius的圆形区域为指定地形类型"""
        for y in range(max(0, cy-radius), min(self.height, cy+radius+1)):
            for x in range(max(0, cx-radius), min(self.width, cx+radius+1)):
                if (x - cx)**2 + (y - cy)**2 <= radius**2:
                    self.cells[y][x].terrain_type = terrain_type

    def _fill_rect(self, left, top, right, bottom, terrain_type):
        """填充矩形区域（包含边界）"""
        for y in range(top, bottom+1):
            for x in range(left, right+1):
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.cells[y][x].terrain_type = terrain_type

    def _generate_river(self, river_width):
        """
        生成一条从屏幕一边进入、另一边出去的河流
        Args:
            river_width (int): 河流宽度（格子数）
        """
        # 定义四个边及对应的初始方向向量索引
        # 方向列表：东、东南、南、西南、西、西北、北、东北
        dirs = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

        # 随机选择入口边（0:左，1:右，2:上，3:下）
        edge = random.randint(0, 3)
        if edge == 0:  # 左边界进入，方向向东
            x, y = 0, random.randint(0, self.height - 1)
            dir_idx = 0  # 东
        elif edge == 1:  # 右边界进入，方向向西
            x, y = self.width - 1, random.randint(0, self.height - 1)
            dir_idx = 4  # 西
        elif edge == 2:  # 上边界进入，方向向南
            x, y = random.randint(0, self.width - 1), 0
            dir_idx = 2  # 南
        else:  # 下边界进入，方向向北
            x, y = random.randint(0, self.width - 1), self.height - 1
            dir_idx = 6  # 北

        path = []
        current_x, current_y = x, y
        current_dir = dir_idx
        max_steps = (self.width + self.height) * 2  # 安全上限

        # 当点在网格内时持续移动
        steps = 0
        while 0 <= current_x < self.width and 0 <= current_y < self.height and steps < max_steps:
            path.append((current_x, current_y))
            # 以一定概率轻微转向（模拟弯曲）
            if random.random() < 0.1:  # 20%概率转向
                turn = random.choice([-1, 1])  # 左转或右转一个方向
                current_dir = (current_dir + turn) % 8
            dx, dy = dirs[current_dir]
            current_x += dx
            current_y += dy
            steps += 1

        # 填充河流（宽度控制）
        half = river_width // 2
        for (px, py) in path:
            for wy in range(py - half, py + half + 1):
                for wx in range(px - half, px + half + 1):
                    if 0 <= wx < self.width and 0 <= wy < self.height:
                        self.cells[wy][wx].terrain_type = Cell.WATER

    def _ensure_forest_cover(self, config):
        """确保森林面积不少于总格子数的一半，否则缩减不可燃区域"""
        total = self.width * self.height
        forest = sum(1 for row in self.cells for cell in row if cell.terrain_type == Cell.FOREST)
        if forest < total * 0.5:
            non_forest = []
            for y in range(self.height):
                for x in range(self.width):
                    if self.cells[y][x].terrain_type != Cell.FOREST:
                        non_forest.append((x, y))
            needed = int(total * 0.5) - forest
            if needed > 0:
                random.shuffle(non_forest)
                for i in range(min(needed, len(non_forest))):
                    x, y = non_forest[i]
                    self.cells[y][x].terrain_type = Cell.FOREST
            print("警告：地形生成后森林面积不足50%，已强制恢复至50%")