"""
Visualizer 模块 - 使用 matplotlib 实现森林火灾模拟的可视化
显示健康（绿色）、燃烧（红色）、烧尽（黑色）的格子，以及当前风向（可选）
"""

import matplotlib
matplotlib.use('TkAgg')  # 或 'Qt5Agg'
import matplotlib.pyplot as plt
import numpy as np
from cell import Cell


class Visualizer:
    """森林火灾模拟的可视化器，基于 matplotlib"""

    def __init__(self, grid_size, title="Forest Fire Simulation", config=None):
        """
        初始化可视化器

        Args:
            grid_size (tuple): (width, height) 网格尺寸
            title (str): 图形窗口标题
            config (Config, optional): 配置对象，用于读取风向等设置（可选）
        """
        self.width, self.height = grid_size
        self.title = title
        self.config = config

        # 读取风向设置（如果提供了 config）
        if config:
            self.wind_enabled = config.wind_enabled
            self.wind_direction = config.wind_direction
        else:
            self.wind_enabled = False
            self.wind_direction = 'E'

        # 开启交互模式
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.ax.set_title(title)
        self.ax.set_xlim(-0.5, self.width - 0.5)
        self.ax.set_ylim(-0.5, self.height - 0.5)
        self.ax.invert_yaxis()
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        # 初始化图像数据
        self.image_data = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.image_data[:] = [0, 255, 0]  # 默认绿色

        self.im = self.ax.imshow(
            self.image_data,
            origin='upper',
            extent=[-0.5, self.width - 0.5, self.height - 0.5, -0.5],
            interpolation='nearest'
        )
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

        # 用于保存风向箭头和文本对象，以便后续移除
        self.wind_arrow = None
        self.wind_text = None

    def render(self, grid, step=None, wind_dir=None):
        """
        更新可视化，并根据传入的风向显示风向箭头或静风文字

        Args:
            grid (Grid): 包含 Cell 对象的网格实例
            step (int, optional): 当前模拟步数，用于显示在标题中
            wind_dir (str, optional): 当前风向，如 'E', 'S', 'W', 'N' 或 'CALM'
        """
        # 1. 更新格子颜色
        for y in range(self.height):
            for x in range(self.width):
                cell = grid.get_cell(x, y)
                if cell.terrain_type == Cell.BARE:
                    self.image_data[y, x] = [128, 128, 128]  # 灰色（裸地）
                elif cell.terrain_type == Cell.WATER:
                    self.image_data[y, x] = [0, 0, 255]      # 蓝色（水域）
                else:  # 森林
                    if cell.is_burning():
                        self.image_data[y, x] = [255, 0, 0]      # 红色
                    elif cell.is_burned():
                        self.image_data[y, x] = [0, 0, 0]        # 黑色
                    else:
                        self.image_data[y, x] = [0, 255, 0]      # 绿色
        self.im.set_data(self.image_data)

        # 2. 移除之前绘制的风向箭头和文本（避免重叠）
        if self.wind_arrow:
            self.wind_arrow.remove()
            self.wind_arrow = None
        if self.wind_text:
            self.wind_text.remove()
            self.wind_text = None

        # 3. 根据当前风向绘制新箭头或文字
        if wind_dir is not None and wind_dir != 'CALM':
            # 箭头方向映射：起点到终点的方向应与风吹方向一致
            # 例如东风（风从东吹向西），箭头应指向左（西）
            if wind_dir == 'E':
                start = (0.88, 0.95)   # 起点在右
                end   = (0.82, 0.95)   # 终点在左
            elif wind_dir == 'W':
                start = (0.82, 0.95)
                end   = (0.88, 0.95)
            elif wind_dir == 'N':
                start = (0.85, 0.97)   # 起点在上
                end   = (0.85, 0.93)   # 终点在下
            elif wind_dir == 'S':
                start = (0.85, 0.93)
                end   = (0.85, 0.97)
            else:
                start = (0.82, 0.95)
                end   = (0.88, 0.95)   # 默认指向右（东）

            # 绘制箭头
            self.wind_arrow = self.ax.annotate(
                '', xy=end, xytext=start,
                xycoords='axes fraction', textcoords='axes fraction',
                arrowprops=dict(arrowstyle='->', color='blue', lw=2)
            )
            # 添加风向文字
            self.wind_text = self.ax.text(
                0.85, 0.90, f'Wind: {wind_dir}',
                transform=self.ax.transAxes, fontsize=10,
                color='blue', ha='center',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.7)
            )
        elif wind_dir == 'CALM':
            # 静风：只显示文字
            self.wind_text = self.ax.text(
                0.85, 0.90, 'Wind: Calm',
                transform=self.ax.transAxes, fontsize=10,
                color='gray', ha='center',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.7)
            )

        # 4. 更新标题（显示当前步数）
        if step is not None:
            self.ax.set_title(f"{self.title} - Step {step}")
        else:
            self.ax.set_title(self.title)

        # 5. 刷新画布
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.1)  # 控制动画速度

    def close(self):
        """关闭可视化窗口，退出交互模式"""
        plt.ioff()
        plt.close(self.fig)