"""
Config 模块 - 配置参数管理类
集中存放所有可调参数，便于修改、验证和扩展。
"""

class Config:
    """森林火灾模拟的配置类，包含所有可调参数"""

    def __init__(self, **kwargs):
        """
        初始化配置参数，允许通过关键字参数覆盖默认值。

        Args:
            **kwargs: 可配置参数，包括：

                网格基础参数:
                    width (int): 网格宽度（列数），默认 100
                    height (int): 网格高度（行数），默认 100
                    spread_prob (float): 基础蔓延概率 [0,1]，默认 0.3
                    burn_duration (int): 燃烧持续时间（时间步数），默认 5
                    initial_fire_positions (list of tuple): 初始火源坐标列表，
                        如 [(x1,y1), (x2,y2)]，默认 [(50,50)]
                    random_seed (int, optional): 随机种子，用于可重复实验，默认 None

                风向相关:
                    wind_enabled (bool): 是否启用风向影响，默认 False
                    wind_direction (str): 初始风向，可选 'N','S','E','W'，默认 'E'
                    wind_factor_downwind (float): 顺风因子（>1），默认 1.5
                    wind_factor_upwind (float): 逆风因子（<1），默认 0.5

                风向动态变化（仅当 wind_enabled=True 且 wind_change_enabled=True 时生效）:
                    wind_change_enabled (bool): 是否启用风向随时间变化，默认 False
                    wind_calm_prob (float): 从有风状态变为静风的概率（每步），默认 0.05
                    wind_calm_stay_prob (float): 静风状态持续的概率，默认 0.3
                    wind_dir_freq (list of float): 四个基本方向（E,S,W,N）的长期频率，
                        用于静风转为有风时的分布，默认 [0.3, 0.2, 0.3, 0.2]（总和应为1）
                    wind_change_interval (int): 风向更新间隔（步数），默认 10

                地形生成开关及种子:
                    terrain_enabled (bool): 是否启用地形生成，默认 True
                    terrain_seed (int, optional): 地形随机种子，None 表示随机，默认 None

                裸地配置:
                    bare_random_points (int): 点状裸地数量，默认 5
                    bare_patches (int): 块状裸地数量（建议 0~2），默认 1
                    bare_patch_radius (int): 块状裸地半径（圆形或矩形半边长），默认 8

                水域配置:
                    water_enabled (bool): 是否启用水域生成，默认 True
                    generate_river (bool): 是否生成河流，默认 True
                    river_length (int): 河流长度（格子数），默认 30
                    river_width (int): 河流宽度（格子数），默认 3
                    generate_lake (bool): 是否生成湖泊，默认 True
                    lake_radius (int): 湖泊半径，默认 8
                    water_ratio_max (float): 水域最大占比（可选，用于调整），默认 0.4
        """
        # 网格基础参数
        self.width = 100
        self.height = 100
        self.spread_prob = 0.3
        self.burn_duration = 5
        self.initial_fire_positions = [(50, 50)]
        self.random_seed = None

        # 风向相关
        self.wind_enabled = False
        self.wind_direction = 'E'
        self.wind_factor_downwind = 1.5
        self.wind_factor_upwind = 0.5

        # 风向动态变化参数
        self.wind_change_enabled = False
        self.wind_calm_prob = 0.05
        self.wind_calm_stay_prob = 0.3
        self.wind_dir_freq = [0.3, 0.2, 0.3, 0.2]  # 顺序：E, S, W, N
        self.wind_change_interval = 10  # 新增：风向更新间隔（步数）

        # 地形生成开关及种子
        self.terrain_enabled = True
        self.terrain_seed = None

        # 裸地配置
        self.bare_random_points = 5          # 点状裸地数量
        self.bare_patches = 1                # 块状裸地数量（0-2）
        self.bare_patch_radius = 8           # 块状裸地半径（圆形）或半边长（矩形）

        # 水域配置
        self.water_enabled = True
        self.generate_river = True            # 是否生成河流
        self.river_length = 30                 # 河流长度（格子数）
        self.river_width = 3                    # 河流宽度（格子数，建议3-4）
        self.generate_lake = True               # 是否生成湖泊
        self.lake_radius = 8                     # 湖泊半径
        self.water_ratio_max = 0.4               # 水域最大占比（可选，用于调整）

        # 用传入的关键字参数覆盖默认值
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"Config 对象没有属性 '{key}'，请检查参数名")

        # 参数验证（确保参数合法）
        self._validate()

    def _validate(self):
        """
        验证配置参数的合法性，不合法时抛出 ValueError。
        包括网格尺寸、蔓延概率、燃烧时长、风向方向、地形参数等。
        """
        # 网格尺寸验证
        if self.width <= 0 or self.height <= 0:
            raise ValueError(f"网格尺寸必须为正整数，当前 width={self.width}, height={self.height}")

        # 蔓延概率验证
        if not (0.0 <= self.spread_prob <= 1.0):
            raise ValueError(f"蔓延概率必须在 [0,1] 范围内，当前 spread_prob={self.spread_prob}")

        # 燃烧持续时间验证
        if self.burn_duration < 1:
            raise ValueError(f"燃烧持续时间必须 >=1，当前 burn_duration={self.burn_duration}")

        # 风向方向验证
        if self.wind_direction not in ['N', 'S', 'E', 'W']:
            raise ValueError("wind_direction 必须是 'N','S','E','W' 之一")

        # 风向动态变化参数验证
        if self.wind_change_enabled:
            if not (0.0 <= self.wind_calm_prob <= 1.0):
                raise ValueError(f"wind_calm_prob 必须在 [0,1] 范围内，当前 {self.wind_calm_prob}")
            if not (0.0 <= self.wind_calm_stay_prob <= 1.0):
                raise ValueError(f"wind_calm_stay_prob 必须在 [0,1] 范围内，当前 {self.wind_calm_stay_prob}")
            if len(self.wind_dir_freq) != 4:
                raise ValueError(f"wind_dir_freq 必须包含4个概率值，当前长度 {len(self.wind_dir_freq)}")
            if abs(sum(self.wind_dir_freq) - 1.0) > 1e-6:
                raise ValueError(f"wind_dir_freq 总和必须为1，当前总和 {sum(self.wind_dir_freq)}")
            for freq in self.wind_dir_freq:
                if freq < 0:
                    raise ValueError(f"风向频率不能为负数，当前 {self.wind_dir_freq}")
            if not isinstance(self.wind_change_interval, int) or self.wind_change_interval < 1:
                raise ValueError(f"wind_change_interval 必须为正整数，当前 {self.wind_change_interval}")

        # 地形参数合理性检查（如果启用地形）
        if self.terrain_enabled:
            if self.bare_random_points < 0:
                raise ValueError("bare_random_points 不能为负数")
            if self.bare_patches < 0 or self.bare_patches > 2:
                raise ValueError("bare_patches 应在 0~2 之间")
            if self.bare_patch_radius < 1:
                raise ValueError("bare_patch_radius 必须 >=1")
            if self.river_length < 1:
                raise ValueError("river_length 必须 >=1")
            if self.river_width < 1:
                raise ValueError("river_width 必须 >=1")
            if self.lake_radius < 1:
                raise ValueError("lake_radius 必须 >=1")
            # water_ratio_max 仅作为参考，可在生成时动态约束，不强制验证

        # 初始火源验证：确保所有坐标在网格范围内
        for (x, y) in self.initial_fire_positions:
            if not (0 <= x < self.width and 0 <= y < self.height):
                raise ValueError(f"初始火源坐标 ({x}, {y}) 超出网格范围 [0,{self.width-1}]x[0,{self.height-1}]")

        # 随机种子可以是任意整数或 None，无需验证

    def __repr__(self):
        """返回配置的字符串表示，便于调试（仅显示关键参数）"""
        return (f"Config(width={self.width}, height={self.height}, "
                f"spread_prob={self.spread_prob}, burn_duration={self.burn_duration}, "
                f"initial_fire_positions={self.initial_fire_positions}, "
                f"random_seed={self.random_seed}, wind_enabled={self.wind_enabled}, "
                f"wind_change_enabled={self.wind_change_enabled}, "
                f"wind_change_interval={self.wind_change_interval}, "
                f"terrain_enabled={self.terrain_enabled})")