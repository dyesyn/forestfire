# forestfire
用于存储工程智能基础的元胞自动机的森林火灾模拟模型的python代码
Forest Fire Simulation

一个基于 Python 的森林火灾蔓延模拟程序，采用元胞自动机算法，支持动态风向变化、随机地形生成（裸地、河流、湖泊），模块化设计便于扩展。程序利用 matplotlib 提供实时可视化，所有参数可通过配置文件灵活调整。

主要特性

- 元胞自动机引擎：在二维网格上模拟火势蔓延，可配置点燃概率和燃烧持续时间。
- 动态风向系统：风向（东、南、西、北）及顺风/逆风因子影响火势蔓延；风向可固定或随时间随机变化（采用马尔可夫链，包含静风状态）。
- 随机地形生成：
  - 裸地：点状或块状分布（不可燃，灰色）。
  - 水域：河流（弯曲带状）和湖泊（圆形块状，蓝色）。
  - 自动保证森林面积不少于总格点的一半。
- 实时可视化：使用 matplotlib 动态显示网格状态（绿色为健康森林，红色为燃烧，黑色为烧尽，灰色为裸地，蓝色为水域），并展示当前风向箭头或静风文字。
- 模块化设计：分为 Cell、Grid、Config、FireSimulator、Visualizer 等独立模块，代码清晰易扩展。
- 参数集中配置：所有运行参数（网格大小、蔓延概率、风向因子、地形选项等）均通过 Config 类管理。
- 可重复实验：支持设置随机种子，保证相同参数下结果可重现。

依赖库

- Python 3.6 或更高版本
- numpy
- matplotlib

安装依赖：

pip install numpy matplotlib

快速开始

1. 克隆或下载本仓库。
2. 运行主程序：
   python main.py
3. 如需调整参数，可直接编辑 main.py 中的 Config 配置，然后重新运行。

项目文件结构

cell.py          - 单个网格单元（包含状态、地形类型等）
grid.py          - 二维网格管理，地形生成逻辑
config.py        - 配置参数类，所有可调参数集中于此
simulator.py     - 火灾蔓延引擎（火势传播、风向更新）
visualizer.py    - 实时绘图模块（基于 matplotlib）
main.py          - 程序入口：配置、运行、可视化
README.md        - 本说明文件

使用示例

from config import Config
from simulator import FireSimulator
from visualizer import Visualizer

config = Config(
    width=100,
    height=100,
    spread_prob=0.105,
    burn_duration=4,
    wind_enabled=True,
    wind_change_enabled=True,
    terrain_enabled=True,
    bare_random_points=10,
    generate_river=True,
    river_width=3,
    generate_lake=True,
    lake_radius=6
)

sim = FireSimulator(config)
vis = Visualizer((config.width, config.height), config=config)

while True:
    burning = sim.step()
    vis.render(sim.grid, wind_dir=sim.wind_dir)
    if burning == 0:
        break
vis.close()

未来可扩展方向

- 添加消防员智能体（手动或自动干预灭火）。
- 集成粒子群优化算法（PSO）寻找最优隔离带位置。
- 支持真实气象数据或更复杂的风场模型。
- 将模拟结果保存为动画（GIF 或视频）。

许可证

MIT License（或您自选的开源许可证）

欢迎 fork 和贡献！
