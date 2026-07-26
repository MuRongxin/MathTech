"""数据模型 - 替代 C# 的 StudentData 等类"""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class StudentData:
    """学生数据"""
    id: int
    name: str
    call_count: int = 0
    # 客观分: [["2025/09/01", "30.00"], ...]
    scores: List[List[str]] = field(default_factory=list)
    # 主观分: [["2025/09/01", "45.00"], ...]
    scores_sub: List[List[str]] = field(default_factory=list)
    # 全卷总分: [["2025/09/01", "75.00"], ...]
    scores_full: List[List[str]] = field(default_factory=list)
    # 逐题分: {date: {question_id: score}}
    question_scores: Dict[str, Dict[str, float]] = field(default_factory=dict)

    @property
    def avg_score(self) -> float:
        """计算该学生客观分平均分（跳过无法解析的畸形条目）"""
        vals = []
        for s in self.scores:
            try:
                vals.append(float(s[1]))
            except (ValueError, TypeError, IndexError):
                continue
        return sum(vals) / len(vals) if vals else 0.0

    @property
    def avg_score_full(self) -> float:
        """计算该学生满分卷平均分（跳过无法解析的畸形条目）"""
        vals = []
        for s in self.scores_full:
            try:
                vals.append(float(s[1]))
            except (ValueError, TypeError, IndexError):
                continue
        return sum(vals) / len(vals) if vals else 0.0


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
class Question:
    """单道题目"""
    id: str                                    # 题号，如 "1", "2a"
    qtype: str = "choice"                      # choice / fill / answer
    max_score: float = 5.0                     # 满分
    topics: List[KnowledgeTopic] = field(default_factory=list)  # 考察的知识点


@dataclass
class ExamMeta:
    """考试元数据"""
    date: str
    questions: List[Question] = field(default_factory=list)  # 题目列表
