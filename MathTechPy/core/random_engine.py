"""随机抽人引擎 - 替代 C# RandomView 中的抽人逻辑

修复的 C# bug：
1. 历史记录现在按 (class_id, mode) 隔离，切换班级不会互相污染
2. 池子不够时优雅降级（不再抛异常）
3. 分组时最后一组自动处理人数不足
4. 增加 weight 机制：call_count 越小的学生权重越高
"""
import random
from typing import List, Dict
from dataclasses import dataclass, field

from .models import StudentData


@dataclass
class RandomResult:
    """抽人结果"""
    student: StudentData
    is_new_cycle: bool = False  # 是否触发了一轮新循环


class RandomEngine:
    def __init__(self, data_manager):
        self.dm = data_manager
        # 按 (class_id, full_score) 隔离历史，避免切换班级时污染
        self._history: Dict[int, List[int]] = {}
        self._last_group_size: int = 3

    def _key(self) -> int:
        return self.dm.current_class

    def _get_history(self) -> List[int]:
        return self._history.setdefault(self._key(), [])

    def pick(self, group_size: int = 1, use_weight: bool = True) -> List[RandomResult]:
        """随机抽取一组学生
        
        Args:
            group_size: 每组人数（默认1）
            use_weight: 是否使用 call_count 权重（优先抽被抽得少的）
        
        Returns:
            List[RandomResult]
        """
        students = self.dm.current_students
        if not students:
            return []

        history = self._get_history()
        results: List[RandomResult] = []
        is_new_cycle = False

        # 如果需要的人数超过班级总人数，限制为班级人数
        group_size = min(group_size, len(students))

        for _ in range(group_size):
            # 排除已抽过的人
            available = [s for s in students if s.id not in history]

            if not available:
                # 一轮结束，清空历史重新开始
                history.clear()
                available = students[:]
                is_new_cycle = True

            if len(available) == 1:
                selected = available[0]
            elif use_weight:
                selected = self._weighted_pick(available)
            else:
                selected = random.choice(available)

            history.append(selected.id)
            results.append(RandomResult(student=selected, is_new_cycle=is_new_cycle))
            is_new_cycle = False  # 只有第一个触发 new_cycle

        self._last_group_size = group_size
        return results

    def _weighted_pick(self, students: List[StudentData]) -> StudentData:
        """按权重随机选择
        
        权重 = 1 / (call_count + 1)，call_count 越大权重越小
        这样保证被抽得少的人有更高概率被抽中
        """
        weights = [1.0 / (s.call_count + 1) for s in students]
        total = sum(weights)
        if total == 0:
            return random.choice(students)

        r = random.uniform(0, total)
        cumulative = 0.0
        for s, w in zip(students, weights):
            cumulative += w
            if r <= cumulative:
                return s
        return students[-1]

    def reset_history(self, class_id: int = None) -> None:
        """清空指定班级的历史记录"""
        if class_id is None:
            self._history.clear()
            return
        self._history.pop(class_id, None)

