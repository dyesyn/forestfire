"""
Cell 模块 - 表示森林火灾模拟中的单个格子
每个格子具有状态、燃烧剩余时间和地形类型。
"""

class Cell:
    """森林火灾模拟中的基本单元 - 一个格子"""

    # 状态常量
    HEALTHY = 0
    BURNING = 1
    BURNED = 2

    # 地形类型常量（新增）
    FOREST = 0
    BARE = 1
    WATER = 2

    def __init__(self, initial_state=HEALTHY, terrain_type=FOREST):
        """
        初始化格子

        Args:
            initial_state (int): 初始状态，默认为 HEALTHY
            terrain_type (int): 地形类型，默认为 FOREST
        """
        self.state = initial_state          # 当前状态
        self.burn_time_remaining = 0        # 剩余燃烧时间步数
        self.terrain_type = terrain_type    # 新增：地形类型

    def ignite(self, burn_duration):
        """
        点燃格子，将其设为燃烧状态（仅当地形可燃时有效，但由调用方控制）
        """
        if self.state == Cell.HEALTHY:      # 地形是否可燃由外部判断
            self.state = Cell.BURNING
            self.burn_time_remaining = burn_duration

    def update(self):
        """更新格子状态（每个时间步调用一次）"""
        if self.state == Cell.BURNING:
            self.burn_time_remaining -= 1
            if self.burn_time_remaining <= 0:
                self.state = Cell.BURNED

    # 状态查询方法
    def is_healthy(self):
        return self.state == Cell.HEALTHY

    def is_burning(self):
        return self.state == Cell.BURNING

    def is_burned(self):
        return self.state == Cell.BURNED

    # 新增：地形是否可燃
    def is_burnable(self):
        """返回格子是否可被燃烧（即地形为森林）"""
        return self.terrain_type == Cell.FOREST

    def __repr__(self):
        state_map = {Cell.HEALTHY: 'H', Cell.BURNING: 'B', Cell.BURNED: 'D'}
        terrain_map = {Cell.FOREST: 'F', Cell.BARE: 'R', Cell.WATER: 'W'}
        return f"{terrain_map[self.terrain_type]}{state_map[self.state]}"