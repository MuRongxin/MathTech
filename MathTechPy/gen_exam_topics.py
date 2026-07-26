"""为每次考试的题目分配知识点，写入 exam_meta.xml"""
import csv
import hashlib
import math
import random
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from core.data_manager import DataManager

random.seed(42)

# 新高考 19 题固定结构，直接复用 DataManager._EXAM19_STRUCTURE，
# 避免与主程序口径漂移（Q1-8单选/5, Q9-11多选/6, Q12-14填空/5, Q15-19解答/13-17）
EXAM19_STRUCTURE = DataManager._EXAM19_STRUCTURE

DATA_DIR = Path(__file__).parent / "data"
SCORE_DIR = DATA_DIR / "question_scores"
META_PATH = DATA_DIR / "exam_meta.xml"

# ─── 知识点池 ───
POOL = {
    "集合与逻辑": ["集合运算", "充分必要条件", "全称量词", "存在量词"],
    "不等式": ["不等式性质", "一元二次不等式", "含绝对值不等式", "均值不等式", "线性规划"],
    "函数": ["定义域", "值域与最值", "单调性判断", "单调性应用", "奇偶性判断",
             "奇偶性应用", "二次函数图像与性质", "二次函数最值", "指数运算",
             "指数函数", "对数运算", "对数函数", "幂函数", "函数零点与方程根",
             "函数模型应用"],
    "三角函数": ["任意角与弧度", "同角关系", "诱导公式", "三角函数图像",
                 "三角函数性质", "正弦型函数 y=Asin(ωx+φ)", "和差公式",
                 "倍角半角公式", "正弦定理及应用", "余弦定理及应用"],
    "数列": ["数列概念与通项", "等差数列通项与求和", "等差数列性质",
             "等比数列通项与求和", "等比数列性质", "裂项相消求和", "错位相减求和"],
    "向量": ["向量概念", "加减与数乘", "数量积", "坐标表示", "平行与垂直", "空间向量"],
    "立体几何": ["表面积", "体积", "线面平行判定", "线面垂直判定",
                 "面面平行与垂直", "空间角计算", "空间距离"],
    "解析几何": ["直线方程", "直线位置关系", "圆的方程", "直线与圆",
                 "椭圆定义与方程", "椭圆性质", "双曲线定义与方程", "双曲线性质",
                 "抛物线定义与方程", "抛物线性质", "直线与圆锥曲线综合"],
    "概率统计": ["随机抽样", "频率分布直方图", "均值中位数众数", "方差与标准差",
                 "古典概型", "几何概型", "互斥与对立事件", "条件概率",
                 "离散型随机变量", "二项分布", "正态分布"],
    "导数": ["导数定义与意义", "基本导数公式", "导数四则运算", "复合函数求导",
             "导数与单调性", "导数与极值", "导数与最值", "导数综合应用"],
    "复数": ["复数概念", "代数运算", "几何意义", "三角形式"],
}

# ─── 同类知识点组合（同一分类内的自然搭配）───
SAME_CAT_COMBOS = {
    "函数": [
        ["定义域", "值域与最值"],
        ["单调性判断", "单调性应用"],
        ["奇偶性判断", "奇偶性应用"],
        ["二次函数图像与性质", "二次函数最值"],
        ["指数运算", "指数函数"],
        ["对数运算", "对数函数"],
        ["定义域", "值域与最值", "单调性应用"],
    ],
    "三角函数": [
        ["同角关系", "诱导公式"],
        ["三角函数图像", "三角函数性质"],
        ["和差公式", "倍角半角公式"],
        ["正弦定理及应用", "余弦定理及应用"],
        ["正弦型函数 y=Asin(ωx+φ)", "三角函数性质"],
    ],
    "数列": [
        ["等差数列通项与求和", "等差数列性质"],
        ["等比数列通项与求和", "等比数列性质"],
    ],
    "向量": [
        ["加减与数乘", "坐标表示"],
        ["数量积", "坐标表示"],
    ],
    "立体几何": [
        ["线面平行判定", "面面平行与垂直"],
        ["线面垂直判定", "面面平行与垂直"],
        ["体积", "空间角计算"],
    ],
    "解析几何": [
        ["直线方程", "直线位置关系"],
        ["圆的方程", "直线与圆"],
        ["椭圆定义与方程", "椭圆性质"],
        ["双曲线定义与方程", "双曲线性质"],
        ["抛物线定义与方程", "抛物线性质"],
        ["直线与圆锥曲线综合", "椭圆性质"],
        ["直线与圆锥曲线综合", "双曲线性质"],
    ],
    "概率统计": [
        ["古典概型", "互斥与对立事件"],
        ["离散型随机变量", "二项分布"],
    ],
    "导数": [
        ["导数与单调性", "导数与极值"],
        ["导数与最值", "导数综合应用"],
    ],
}

# ─── 跨分类逻辑组合（有数学关联的跨类搭配）───
CROSS_CAT_COMBOS = [
    # 函数 + 不等式
    (["函数", "不等式"], [["函数零点与方程根", "一元二次不等式"],
                          ["单调性应用", "均值不等式"]]),
    # 函数 + 集合
    (["集合与逻辑", "函数"], [["集合运算", "定义域"],
                              ["充分必要条件", "函数零点与方程根"]]),
    # 三角 + 向量
    (["向量", "三角函数"], [["数量积", "和差公式"],
                            ["坐标表示", "正弦型函数 y=Asin(ωx+φ)"]]),
    # 向量 + 立体几何
    (["向量", "立体几何"], [["空间向量", "空间角计算"],
                            ["空间向量", "体积"]]),
    # 立体几何 + 解析几何（空间坐标系）
    (["立体几何", "解析几何"], [["空间角计算", "直线方程"]]),
    # 导数 + 函数
    (["导数", "函数"], [["导数与单调性", "单调性应用"],
                        ["导数与最值", "值域与最值"],
                        ["导数综合应用", "函数零点与方程根"]]),
    # 导数 + 不等式
    (["导数", "不等式"], [["导数与最值", "均值不等式"]]),
    # 概率 + 数列（递推概率）
    (["概率统计", "数列"], [["条件概率", "数列概念与通项"]]),
]

# ─── 教学进度：日期 → 活跃知识点分类 ───
def get_active_cats(date_str: str) -> list[str]:
    """根据日期返回当前教学阶段的重点分类 + 复习分类"""
    month = int(date_str.split("/")[1])
    day = int(date_str.split("/")[2])

    if month == 9:
        if day <= 7:
            primary = ["集合与逻辑", "不等式"]
            review = []
        elif day <= 14:
            primary = ["函数"]
            review = ["集合与逻辑"]
        elif day <= 21:
            primary = ["函数", "三角函数"]
            review = ["不等式"]
        else:
            primary = ["三角函数"]
            review = ["函数", "集合与逻辑"]
    elif month == 10:
        if day <= 10:
            primary = ["三角函数", "数列"]
            review = ["函数"]
        elif day <= 20:
            primary = ["数列", "向量"]
            review = ["三角函数", "不等式"]
        else:
            primary = ["向量", "立体几何"]
            review = ["数列", "函数"]
    else:
        primary = ["立体几何", "解析几何"]
        review = ["三角函数", "函数"]

    return primary + review


def pick_topic(cats: list[str]) -> tuple[str, str]:
    """从指定分类中随机选一个知识点"""
    cat = random.choice(cats)
    topic = random.choice(POOL[cat])
    return cat, topic


def pick_multi_topics(qtype: str, max_score: float, cats: list[str]) -> list[dict]:
    """为一道题选择 1-3 个知识点（含权重）

    选择题: 通常1个，偶尔2-3个（同分类或逻辑跨分类）
    填空: 1个
    解答: 1-2个（同分类为主）
    """
    # 选择题（5分或6分）
    if max_score <= 6:
        r = random.random()
        if r < 0.70:
            # 70% 单知识点
            cat, topic = pick_topic(cats)
            return [{"category": cat, "name": topic, "weight": 1.0}]
        elif r < 0.90:
            # 20% 同分类双知识点
            for cat in cats:
                if cat in SAME_CAT_COMBOS:
                    combo = random.choice(SAME_CAT_COMBOS[cat])
                    w1 = round(random.uniform(0.4, 0.6), 2)
                    w2 = round(1.0 - w1, 2)
                    return [
                        {"category": cat, "name": combo[0], "weight": w1},
                        {"category": cat, "name": combo[1], "weight": w2},
                    ]
            # 没有预定义组合，退化为单知识点
            cat, topic = pick_topic(cats)
            return [{"category": cat, "name": topic, "weight": 1.0}]
        else:
            # 10% 跨分类组合
            valid_cross = [(cc, combos) for cc, combos in CROSS_CAT_COMBOS
                           if all(c in cats for c in cc)]
            if valid_cross:
                cc, combos = random.choice(valid_cross)
                combo = random.choice(combos)
                w1 = round(random.uniform(0.4, 0.6), 2)
                return [
                    {"category": cc[0], "name": combo[0], "weight": w1},
                    {"category": cc[1], "name": combo[1], "weight": round(1.0 - w1, 2)},
                ]
            cat, topic = pick_topic(cats)
            return [{"category": cat, "name": topic, "weight": 1.0}]

    # 填空题
    if max_score <= 10:
        cat, topic = pick_topic(cats)
        return [{"category": cat, "name": topic, "weight": 1.0}]

    # 解答题（>10分）
    r = random.random()
    if r < 0.40:
        # 40% 单知识点
        cat, topic = pick_topic(cats)
        return [{"category": cat, "name": topic, "weight": 1.0}]
    elif r < 0.85:
        # 45% 同分类双知识点
        for cat in cats:
            if cat in SAME_CAT_COMBOS:
                combo = random.choice(SAME_CAT_COMBOS[cat])
                w1 = round(random.uniform(0.4, 0.6), 2)
                return [
                    {"category": cat, "name": combo[0], "weight": w1},
                    {"category": cat, "name": combo[1], "weight": round(1.0 - w1, 2)},
                ]
        cat, topic = pick_topic(cats)
        return [{"category": cat, "name": topic, "weight": 1.0}]
    else:
        # 15% 跨分类组合
        valid_cross = [(cc, combos) for cc, combos in CROSS_CAT_COMBOS
                       if all(c in cats for c in cc)]
        if valid_cross:
            cc, combos = random.choice(valid_cross)
            combo = random.choice(combos)
            w1 = round(random.uniform(0.4, 0.6), 2)
            return [
                {"category": cc[0], "name": combo[0], "weight": w1},
                {"category": cc[1], "name": combo[1], "weight": round(1.0 - w1, 2)},
            ]
        cat, topic = pick_topic(cats)
        return [{"category": cat, "name": topic, "weight": 1.0}]


def _qnum(qid: str) -> int:
    """提取题号数字（与 DataManager._detect_questions 同口径）"""
    m = re.search(r"\d+", qid)
    return int(m.group(0)) if m else 0


def detect_qtype(max_score: float, all_scores: list[float], etype: str = "quiz") -> str:
    """按观测得分推断题型，与 DataManager._detect_questions 的推断分支对齐"""
    # 存在 0 与满分之外的中间分 → 多选
    if max_score == 6 and any(0 < s < max_score for s in all_scores):
        return "multi_select"
    if etype == "quiz":
        return "choice"          # 测验默认选择题
    if max_score > 10:
        return "answer"
    return "fill"


def process_file(fpath: Path, etype: str = "quiz") -> dict:
    """解析一个CSV文件，返回 {qid: max_score, qtype, all_scores}

    exam 且题号恰为 Q1-Q19 时直接套用 EXAM19_STRUCTURE（与主程序
    DataManager._detect_questions 的固定结构分支一致）；其余按观测推断。
    """
    with open(fpath, "r", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    if not rows:
        return {}

    headers = [h.strip() for h in rows[0]]
    q_cols = [(i, h) for i, h in enumerate(headers)
              if h.startswith("Q") and h[1:].isdigit()]

    qid_data = {}  # {qid: [scores]}
    for row in rows[1:]:
        if not row or len(row) < 2:
            continue
        for idx, qid in q_cols:
            if idx < len(row) and row[idx]:
                try:
                    qid_data.setdefault(qid, []).append(float(row[idx]))
                except ValueError:
                    qid_data.setdefault(qid, []).append(0.0)

    # 新高考 19 题卷：题号恰为 1-19 时套用固定结构
    use_fixed = (etype == "exam" and len(qid_data) == 19
                 and sorted(_qnum(q) for q in qid_data) == list(range(1, 20)))
    if not use_fixed:
        print(f"  提示: {fpath.name} 的题目结构按全班最高得分推断，"
              f"若无人得满分则满分/题型可能被低估")

    result = {}
    for qid in sorted(qid_data.keys(),
                      key=lambda x: (not x[1:].isdigit(), int(x[1:]) if x[1:].isdigit() else 0)):
        scores = qid_data[qid]
        if use_fixed:
            qtype, max_score = EXAM19_STRUCTURE[_qnum(qid)]
        else:
            max_seen = max(scores) if scores else 0.0
            # 满分取不小于观测最大值的整数（ceil 避免 round 低估）
            max_score = float(max(1, math.ceil(max_seen))) if max_seen > 0 else 5.0
            qtype = detect_qtype(max_score, scores, etype)
        result[qid] = {"max_score": max_score, "qtype": qtype, "scores": scores}

    return result


def build_exam_meta(fpath: Path, date_str: str, etype: str = "quiz") -> tuple[str, list[dict]]:
    """为一个文件生成考试元数据"""
    cats = get_active_cats(date_str)
    q_info = process_file(fpath, etype)

    questions = []
    for qid, info in q_info.items():
        topics = pick_multi_topics(info["qtype"], info["max_score"], cats)
        topic_objs = []
        for t in topics:
            topic_objs.append({
                "category": t["category"],
                "name": t["name"],
                "weight": t["weight"],
            })
        questions.append({
            "id": qid,
            "type": info["qtype"],
            "max": info["max_score"],
            "topics": topic_objs,
        })

    return date_str, questions


def main():
    if not META_PATH.exists():
        raise SystemExit(f"错误: 未找到 {META_PATH}\n"
                         f"请先运行主程序（它会自动生成空的 exam_meta.xml），再运行本脚本")

    # 扫描所有文件
    files = sorted(SCORE_DIR.glob("*.csv"))
    exam_data = {}  # date_str → questions (以 A01 为准)

    for fpath in files:
        parts = fpath.stem.split("_")
        if len(parts) < 5:
            continue
        etype = parts[0]
        date_str = f"{parts[1]}/{parts[2]}/{parts[3]}"
        cls = parts[4].replace("A", "")

        # 只用 A01 的文件推断题目结构（各班题目相同）
        if cls != "01":
            continue

        # 用稳定哈希做种子，保证同一日期多次运行结果一致
        # （字符串 hash() 受 PYTHONHASHSEED 随机化，不可复现）
        random.seed(int(hashlib.md5(date_str.encode()).hexdigest()[:8], 16))
        date_str, questions = build_exam_meta(fpath, date_str, etype)
        exam_data[date_str] = questions

        n_topics = sum(len(q["topics"]) for q in questions)
        print(f"{date_str} ({etype}): {len(questions)}题, {n_topics}个知识点标注")

    # 读取现有 exam_meta.xml，保留已有结构
    tree = ET.parse(META_PATH)
    root = tree.getroot()
    xml_dates = {e.get("date", "") for e in root.findall("exam")}

    for dt in sorted(set(exam_data) - xml_dates):
        print(f"[WARN] {dt} 有逐题分数据但 exam_meta.xml 中无对应 <exam> 节点，已跳过")

    for exam_elem in root.findall("exam"):
        dt = exam_elem.get("date", "")
        if dt not in exam_data:
            continue

        questions = exam_data[dt]

        # 移除旧的 questions 节点
        old_qs = exam_elem.find("questions")
        if old_qs is not None:
            exam_elem.remove(old_qs)

        # 写入新的 questions
        qnode = ET.SubElement(exam_elem, "questions")
        for q in questions:
            qelem = ET.SubElement(qnode, "question",
                                  {"id": q["id"], "type": q["type"],
                                   "max": str(q["max"])})
            for t in q["topics"]:
                attrs = {"category": t["category"]}
                w = t["weight"]
                if w != 1.0:
                    attrs["weight"] = f"{w:.2f}"
                ET.SubElement(qelem, "topic", attrs).text = t["name"]

    # 缩进
    def indent(elem, level=0):
        indent_str = "\n" + "  " * level
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent_str + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent_str
            for child in elem:
                indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = "\n" + "  " * level
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent_str

    indent(root)
    ET.ElementTree(root).write(META_PATH, encoding="utf-8", xml_declaration=True)
    print(f"\n已写入 {META_PATH}")


if __name__ == "__main__":
    main()
