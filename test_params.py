"""
参数测试脚本
功能：输入蔓延概率和燃烧时长，运行10次模拟，输出每次的过火面积和未燃烧比例
"""

import sys
import numpy as np
from config import Config
from simulator import FireSimulator
from cell import Cell

def run_test(spread_prob, burn_duration, runs=10, width=100, height=100):
    """
    运行多次模拟，统计过火面积和未燃烧比例

    Args:
        spread_prob (float): 蔓延概率
        burn_duration (int): 燃烧持续时间
        runs (int): 模拟次数
        width, height (int): 网格尺寸

    Returns:
        list of (burned_area, unburned_ratio)
    """
    results = []
    for i in range(runs):
        # 创建配置（随机种子设为None，使每次结果不同）
        config = Config(
            width=width,
            height=height,
            spread_prob=spread_prob,
            burn_duration=burn_duration,
            initial_fire_positions=[(width//2, height//2)],  # 中心点火
            random_seed=None
        )
        sim = FireSimulator(config)
        sim.run()  # 运行到火熄灭

        # 统计烧毁格子数
        burned = 0
        total_forest = width * height  # 假设全部为森林（无可燃物类型差异）
        for cell in sim.grid.get_all_cells():
            if cell.is_burned():
                burned += 1
        unburned = total_forest - burned
        unburned_ratio = unburned / total_forest

        results.append((burned, unburned_ratio))
        print(f"Run {i+1:2d}: 烧毁格子数 = {burned:5d}, 未燃烧比例 = {unburned_ratio:.2%}")

    # 计算平均值和标准差
    burned_array = [r[0] for r in results]
    unburned_ratio_array = [r[1] for r in results]
    mean_burned = np.mean(burned_array)
    std_burned = np.std(burned_array)
    mean_ratio = np.mean(unburned_ratio_array)
    std_ratio = np.std(unburned_ratio_array)

    print("\n=== 统计汇总 ===")
    print(f"平均烧毁格子数: {mean_burned:.1f} ± {std_burned:.1f}")
    print(f"平均未燃烧比例: {mean_ratio:.2%} ± {std_ratio:.2%}")

    return results

if __name__ == "__main__":
    # 从命令行参数读取（如果有）否则手动输入
    if len(sys.argv) >= 3:
        spread_prob = float(sys.argv[1])
        burn_duration = int(sys.argv[2])
    else:
        # 提示用户输入
        spread_prob = float(input("蔓延概率: "))
        burn_duration = int(input("燃烧时长: "))

    print(f"\n测试参数: spread_prob={spread_prob}, burn_duration={burn_duration}\n")
    run_test(spread_prob, burn_duration, runs=10)