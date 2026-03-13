"""
主控模块：组装所有零件，运行森林火灾模拟
"""

import sys
import traceback
from config import Config
from simulator import FireSimulator
from visualizer import Visualizer


def main():
    """主函数：配置、运行、统计"""
    # ========== 1. 配置参数 ==========
    # 你可以在这里直接修改参数，或通过命令行参数、配置文件等方式传入
    config = Config(
        width=100,
        height=100,
        spread_prob=0.105,
        burn_duration=4,
        initial_fire_positions=[(50, 50)],
        random_seed=None,
        terrain_enabled=True,
        # 裸地配置
        bare_random_points=10,      # 点状裸地数量
        bare_patches=2,             # 块状裸地数量
        bare_patch_radius=8,        # 块状裸地半径
        # 水域配置
        generate_river=True,
        river_width=3,
        generate_lake=True,
        lake_radius=6,
        # 风向相关
        wind_enabled=True,
        wind_change_enabled=True,   # 启用风向动态变化
        wind_change_interval=20,
    )

    # 打印配置信息（可选）
    print("=== 模拟配置 ===")
    print(config)
    print()

    # ========== 2. 初始化模拟器和可视化器 ==========
    sim = FireSimulator(config)
    vis = Visualizer(
        grid_size=(config.width, config.height),
        title="Forest Fire Simulation",
        config=config
    )

    # ========== 3. 运行主循环 ==========
    print("模拟开始...")
    step_count = 0
    try:
        while True:
            # 执行一个时间步，返回燃烧格子数
            burning = sim.step()
            step_count += 1

            # 更新可视化（传入当前风向，使风向箭头动态变化）
            vis.render(sim.grid, step=step_count, wind_dir=sim.wind_dir)

            # 检查是否结束（无燃烧格子）
            if burning == 0:
                print(f"\n模拟结束，共运行 {step_count} 步")
                break

    except KeyboardInterrupt:
        # 用户按 Ctrl+C 手动停止
        print("\n用户中断模拟")
    except Exception as e:
        print(f"运行出错: {e}")
        traceback.print_exc()
    finally:
        # ========== 4. 清理资源 ==========
        vis.close()

    # ========== 5. 输出统计信息 ==========
    total_cells = config.width * config.height
    burned_cells = 0
    for cell in sim.grid.get_all_cells():
        if cell.is_burned():
            burned_cells += 1
    burned_ratio = burned_cells / total_cells

    print(f"总格子数: {total_cells}")
    print(f"最终烧毁格子数: {burned_cells}")
    print(f"烧毁比例: {burned_ratio:.2%}")


if __name__ == "__main__":
    main()