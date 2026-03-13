"""
FireSimulator 模块 - 森林火灾模拟的核心引擎
负责执行元胞自动机的蔓延规则，驱动网格状态演化，并支持风向动态变化。
"""

import random
from grid import Grid
from cell import Cell


class FireSimulator:
    """森林火灾模拟器，管理网格和蔓延逻辑"""

    def __init__(self, config):
        """
        初始化模拟器

        Args:
            config: 配置对象，必须包含以下属性：
                - width (int): 网格宽度
                - height (int): 网格高度
                - spread_prob (float): 基础蔓延概率 (0~1)
                - burn_duration (int): 燃烧持续时间（时间步数）
                - initial_fire_positions (list of tuple): 初始火源坐标列表
                - terrain_enabled (bool): 是否启用地形
                - wind_enabled (bool): 是否启用风向影响
                - wind_direction (str): 初始风向 ('N','S','E','W')
                - wind_factor_downwind (float): 顺风因子
                - wind_factor_upwind (float): 逆风因子
                - wind_change_enabled (bool): 是否启用风向随时间变化
                - wind_calm_prob (float): 从有风状态变为静风的概率（每步）
                - wind_calm_stay_prob (float): 静风状态持续的概率
                - wind_dir_freq (list of float): 四个方向（E,S,W,N）的长期频率，总和为1
                - wind_change_interval (int): 风向更新间隔（步数）
                - random_seed (int, optional): 随机种子（用于可重复实验）
        """
        self.config = config
        self.spread_prob = config.spread_prob
        self.burn_duration = config.burn_duration

        # 如果提供了随机种子，则固定随机数生成器（影响风向变化和蔓延随机性）
        if config.random_seed is not None:
            random.seed(config.random_seed)

        # 创建网格，如果启用地形则传入配置（用于生成地形）
        terrain_conf = config if config.terrain_enabled else None
        self.grid = Grid(config.width, config.height, terrain_config=terrain_conf)

        # 风向相关参数
        self.wind_enabled = config.wind_enabled
        self.wind_dir = config.wind_direction
        self.wind_factor_downwind = config.wind_factor_downwind
        self.wind_factor_upwind = config.wind_factor_upwind

        # 风向动态变化相关参数
        self.wind_change_enabled = config.wind_change_enabled
        self.wind_calm_prob = config.wind_calm_prob
        self.wind_calm_stay_prob = config.wind_calm_stay_prob
        self.wind_dir_freq = config.wind_dir_freq  # 四个方向（E,S,W,N）的频率
        self.wind_change_interval = config.wind_change_interval  # 新增：更新间隔
        self._wind_step_counter = 0  # 步数计数器，用于控制更新间隔

        # 定义方向列表和索引映射（用于风向变化）
        self.wind_directions = ['E', 'S', 'W', 'N']          # 顺序固定，与风向频率对应
        self.wind_index_map = {d: i for i, d in enumerate(self.wind_directions)}
        self.CALM_INDEX = 4                                   # 静风索引（无风）

        # 初始化当前风向索引（从配置的 wind_direction 转换）
        if self.wind_dir in self.wind_index_map:
            self.wind_dir_index = self.wind_index_map[self.wind_dir]
        else:
            # 默认东风
            self.wind_dir_index = 0
            self.wind_dir = 'E'

        # 设置初始火源
        # 注意：火源坐标可能位于不可燃地形（如裸地、水域），
        # 但点燃操作本身会检查格子是否健康，而不可燃格子保持健康状态但不可燃，
        # 因此即使火源设在不可燃格子上，它不会蔓延，但会在当前步显示为燃烧（视觉上不合理）。
        # 为了简化，假设初始火源总是设在森林上。
        for (x, y) in config.initial_fire_positions:
            self.grid.set_cell_state(x, y, Cell.BURNING, self.burn_duration)

        # 当前模拟步数（用于统计）
        self.current_step = 0

    def _update_wind_direction(self):
        """
        根据马尔可夫链更新风向（包括静风状态）。
        每步调用一次，修改 self.wind_dir_index 和 self.wind_dir。
        """
        if not self.wind_change_enabled:
            return

        r = random.random()

        # 当前有风（索引 0~3）
        if self.wind_dir_index != self.CALM_INDEX:
            # 先判断是否变为静风
            if r < self.wind_calm_prob:
                self.wind_dir_index = self.CALM_INDEX
                self.wind_dir = 'CALM'
                return
            else:
                # 有风状态间转移：获取从当前风向转移到四个有风方向的概率
                probs = self._get_four_dir_transition_probs(self.wind_dir_index)
                next_idx = random.choices(range(4), weights=probs)[0]
                self.wind_dir_index = next_idx
                self.wind_dir = self.wind_directions[next_idx]
        else:
            # 当前静风
            if r < self.wind_calm_stay_prob:
                # 保持静风
                return
            else:
                # 从静风转为有风，按长期频率选择方向
                next_idx = random.choices(range(4), weights=self.wind_dir_freq)[0]
                self.wind_dir_index = next_idx
                self.wind_dir = self.wind_directions[next_idx]

    def _get_four_dir_transition_probs(self, current_idx):
        """
        根据当前风向索引（0~3）生成转移到四个有风方向的概率列表（总和为1）。

        规则（可自定义）：
        - 维持原方向概率 0.4
        - 左右相邻方向（顺时针和逆时针）各 0.2
        - 相反方向概率 0.1
        - 总和为 0.4+0.2+0.2+0.1=0.9，剩余 0.1 按比例分配到所有方向（归一化处理）
        """
        probs = [0.0] * 4
        probs[current_idx] = 0.4                      # 自保持
        probs[(current_idx - 1) % 4] = 0.2             # 左邻
        probs[(current_idx + 1) % 4] = 0.2             # 右邻
        probs[(current_idx + 2) % 4] = 0.1             # 对面

        # 归一化（确保总和为1，避免浮点误差）
        total = sum(probs)
        return [p / total for p in probs]

    def step(self):
        """
        执行一个时间步的更新：
        1. 更新风向（按间隔触发）
        2. 收集当前所有燃烧格子的坐标
        3. 每个燃烧格子尝试点燃其健康且可燃烧的邻居（考虑风向因子）
        4. 更新所有格子的状态（燃烧时间减1，烧尽状态转换）
        5. 返回当前时间步结束后的燃烧格子数量

        Returns:
            int: 当前燃烧的格子数
        """
        # 1. 风向更新（按间隔触发）
        if self.wind_change_enabled:
            self._wind_step_counter += 1
            if self._wind_step_counter >= self.wind_change_interval:
                self._update_wind_direction()
                self._wind_step_counter = 0

        # 2. 收集当前所有燃烧格子的坐标
        burning_positions = []
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                if self.grid.get_cell(x, y).is_burning():
                    burning_positions.append((x, y))

        # 3. 蔓延：每个燃烧格子尝试点燃其邻居
        for (x, y) in burning_positions:
            # 获取所有邻居（包括坐标和单元格对象）
            neighbors = self.grid.get_neighbors(x, y)   # 每个元素为 (nx, ny, cell)
            for (nx, ny, neighbor) in neighbors:
                # 只对健康且可燃烧的格子尝试点燃
                if neighbor.is_healthy() and neighbor.is_burnable():
                    prob = self.spread_prob

                    # 如果启用风向且当前不是静风，则计算风向因子
                    if self.wind_enabled and self.wind_dir != 'CALM':
                        factor = 1.0
                        # 根据当前风向确定顺风/逆风方向
                        if self.wind_dir == 'E':      # 东风 -> 向西吹
                            if nx < x:                 # 邻居在西侧，顺风
                                factor = self.wind_factor_downwind
                            elif nx > x:               # 邻居在东侧，逆风
                                factor = self.wind_factor_upwind
                        elif self.wind_dir == 'W':      # 西风 -> 向东吹
                            if nx > x:                  # 邻居在东侧，顺风
                                factor = self.wind_factor_downwind
                            elif nx < x:                # 邻居在西侧，逆风
                                factor = self.wind_factor_upwind
                        elif self.wind_dir == 'N':      # 北风 -> 向南吹
                            if ny > y:                  # 邻居在南侧，顺风
                                factor = self.wind_factor_downwind
                            elif ny < y:                # 邻居在北侧，逆风
                                factor = self.wind_factor_upwind
                        elif self.wind_dir == 'S':      # 南风 -> 向北吹
                            if ny < y:                  # 邻居在北侧，顺风
                                factor = self.wind_factor_downwind
                            elif ny > y:                # 邻居在南侧，逆风
                                factor = self.wind_factor_upwind
                        # 侧风（同 x 或同 y）因子保持 1.0
                        prob *= factor
                    # 如果 wind_enabled=False 或当前静风，则 prob 保持不变（即无风向影响）

                    # 随机点燃
                    if random.random() < prob:
                        neighbor.ignite(self.burn_duration)

        # 4. 更新所有格子的状态（燃烧倒计时、烧尽转换）
        for cell in self.grid.get_all_cells():
            cell.update()

        self.current_step += 1

        # 5. 返回当前燃烧格子数
        return self.grid.count_burning()

    def run(self, max_steps=None):
        """
        连续运行模拟，直到没有燃烧格子或达到最大步数

        Args:
            max_steps (int, optional): 最大运行步数，None 表示无限直到自然熄灭

        Returns:
            int: 实际运行的总步数
        """
        steps = 0
        while True:
            burning = self.step()
            steps += 1
            if burning == 0:
                break
            if max_steps is not None and steps >= max_steps:
                break
        return steps

    def reset(self):
        """重置模拟器：保留地形，只重置格子状态、初始火源和风向"""
        # 重置所有格子的状态（健康/燃烧/烧尽），保留地形类型
        self.grid.reset_states()

        # 重新设置初始火源
        for (x, y) in self.config.initial_fire_positions:
            self.grid.set_cell_state(x, y, Cell.BURNING, self.burn_duration)

        # 重置风向为初始配置
        self.wind_dir = self.config.wind_direction
        if self.wind_dir in self.wind_index_map:
            self.wind_dir_index = self.wind_index_map[self.wind_dir]
        else:
            self.wind_dir_index = 0
            self.wind_dir = 'E'

        # 重置步数计数器和风向更新计数器
        self.current_step = 0
        self._wind_step_counter = 0