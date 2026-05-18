"""数据模型 - 替代 C# 的 StudentData 等类"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class StudentData:
    """学生数据"""
    id: int
    name: str
    call_count: int = 0
    # 客观分成绩: [["2024/09/01", "0.78"], ...]
    scores: List[List[str]] = field(default_factory=list)
    # 满分卷成绩: [["2024/09/01", "0.44"], ...]
    scores_full: List[List[str]] = field(default_factory=list)

    @property
    def score_count(self) -> int:
        return len(self.scores)

    @property
    def avg_score(self) -> float:
        """计算该学生客观分平均分"""
        if not self.scores:
            return 0.0
        return sum(float(s[1]) for s in self.scores) / len(self.scores)

    @property
    def avg_score_full(self) -> float:
        """计算该学生满分卷平均分"""
        if not self.scores_full:
            return 0.0
        return sum(float(s[1]) for s in self.scores_full) / len(self.scores_full)


@dataclass
class ClassInfo:
    """班级统计信息"""
    name: str
    count: int
    avg_call: float
    avg_score: float
    avg_score_full: float


@dataclass
class KnowledgeTopic:
    """单个知识点"""
    category: str   # 一级分类，如 "函数"
    name: str       # 二级知识点，如 "单调性判断"
    weight: float = 1.0  # 权重 0.01~1.0，表示该知识点在考试中的占比


@dataclass
class ExamMeta:
    """考试元数据"""
    date: str
    subjective_topics: List[KnowledgeTopic] = field(default_factory=list)  # 客观分知识点
    objective_topics: List[KnowledgeTopic] = field(default_factory=list)   # 满分卷知识点
