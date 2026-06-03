"""生成 exam_meta.xml — 模拟真实教学进度的考试知识点分布"""
import random
import xml.etree.ElementTree as ET
from pathlib import Path
from core.data_manager import DataManager

random.seed(42)

# 从 DataManager 获取实际日期
dm = DataManager()
dates = dm.dates
print(f"实际考试数: {len(dates)}")
print(f"首: {dates[0]}, 末: {dates[-1]}")

# ---- 知识点池 ----
POOL = {
    "函数": [
        "定义域","值域与最值","单调性判断","单调性应用","奇偶性判断",
        "奇偶性应用","二次函数图像与性质","二次函数最值","指数运算",
        "指数函数","对数运算","对数函数","幂函数","函数零点与方程根","函数模型应用",
    ],
    "集合与逻辑": ["集合运算","充分必要条件","全称量词","存在量词"],
    "不等式": ["不等式性质","一元二次不等式","含绝对值不等式","均值不等式","线性规划"],
    "三角函数": [
        "任意角与弧度","同角关系","诱导公式","三角函数图像","三角函数性质",
        "正弦型函数 y=Asin(ωx+φ)","和差公式","倍角半角公式","正弦定理及应用","余弦定理及应用",
    ],
    "数列": ["数列概念与通项","等差数列通项与求和","等差数列性质",
            "等比数列通项与求和","等比数列性质","裂项相消求和","错位相减求和"],
    "向量": ["向量概念","加减与数乘","数量积","坐标表示","平行与垂直","空间向量"],
    "立体几何": ["表面积","体积","线面平行判定","线面垂直判定",
                "面面平行与垂直","空间角计算","空间距离"],
    "解析几何": [
        "直线方程","直线位置关系","圆的方程","直线与圆","椭圆定义与方程",
        "椭圆性质","双曲线定义与方程","双曲线性质","抛物线定义与方程",
        "抛物线性质","直线与圆锥曲线综合",
    ],
    "导数": ["导数定义与意义","基本导数公式","导数四则运算","复合函数求导",
            "导数与单调性","导数与极值","导数与最值","导数综合应用"],
    "概率统计": ["随机抽样","频率分布直方图","均值中位数众数","方差与标准差",
                "古典概型","几何概型","互斥与对立事件","条件概率",
                "离散型随机变量","二项分布","正态分布"],
    "复数": ["复数概念","代数运算","几何意义","三角形式"],
}

N = len(dates)

# ---- 教学进度阶段 (按索引) ----
# 基于实际日期分布：前慢后密
# 0-19:  9月 (函数+集合+不等式，每3天一次)
# 20-39: 10月-11月中 (三角函数)
# 40-57: 11月中-12月底 (数列+向量)
# 58-71: 1月-2月中 (立体几何)
# 72-85: 2月中-4月初 (解析几何)
# 86-95: 4月-5月 (导数+概率统计+复数)
# 96-99: 6月 (综合复习)
SCHEDULE = [
    (0,  20, ["函数","集合与逻辑","不等式"]),
    (20, 40, ["三角函数"]),
    (40, 58, ["数列","向量"]),
    (58, 72, ["立体几何"]),
    (72, 86, ["解析几何"]),
    (86, 96, ["导数","概率统计","复数"]),
    (96, N,  None),  # 综合复习
]


def pick_topics(categories: list[str], count: int) -> list[tuple[str, str, float]]:
    """从指定分类中随机选 count 个知识点，分配合理权重"""
    candidates = []
    for cat in categories:
        for topic in POOL.get(cat, []):
            candidates.append((cat, topic))
    if not candidates:
        return []
    if len(candidates) <= count:
        selected = candidates[:]
    else:
        selected = random.sample(candidates, count)

    raw = [random.uniform(0.10, 0.50) for _ in selected]
    total = sum(raw)
    weights = [round(w / total, 2) for w in raw]
    diff = round(1.0 - sum(weights), 2)
    if diff != 0 and weights:
        weights[0] = round(weights[0] + diff, 2)
    return [(cat, topic, w) for (cat, topic), w in zip(selected, weights)]


def get_active_cats(i: int) -> list[str]:
    """获取第 i 次考试的激活分类，含跨阶段复习"""
    active = []
    for start, end, cats in SCHEDULE:
        if start <= i < end:
            if cats is None:
                # 综合复习
                active = random.sample(list(POOL.keys()), random.randint(4, 6))
            else:
                active = list(cats)
            break

    # 30% 概率加入 1-2 个之前学过的分类做滚动复习
    if i >= 10 and random.random() < 0.35:
        old_cats = set()
        for start, end, cats in SCHEDULE:
            if end <= i and start < i - 8 and cats is not None:
                old_cats.update(cats)
        if old_cats and active:
            old_list = list(old_cats - set(active))
            if old_list:
                extra = random.sample(old_list, min(2, len(old_list)))
                active = active + extra
    return active


# ---- 生成 ----
root = ET.Element("exams")

for i, date in enumerate(dates):
    exam = ET.SubElement(root, "exam", {"date": date})
    active_cats = get_active_cats(i)

    # 客观题知识点（所有考试都有）
    obj_count = random.randint(3, 6)
    obj_topics = pick_topics(active_cats, obj_count)
    sub_obj = ET.SubElement(exam, "subjective")
    for cat, topic, weight in obj_topics:
        ET.SubElement(sub_obj, "topic",
                      {"category": cat, "weight": f"{weight:.2f}"}).text = topic

    # 主观题知识点（~25% 测验型考试无主观题）
    is_quiz = random.random() < 0.25
    sub_elem = ET.SubElement(exam, "objective")
    if not is_quiz:
        sub_count = random.randint(2, 5)
        sub_topics = pick_topics(active_cats, sub_count)
        for cat, topic, weight in sub_topics:
            ET.SubElement(sub_elem, "topic",
                          {"category": cat, "weight": f"{weight:.2f}"}).text = topic


# ---- 写入 ----
def indent_xml(elem, level=0):
    indent_str = "\n" + "  " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent_str + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent_str
        for child in elem:
            indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = "\n" + "  " * level
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent_str

indent_xml(root)
tree = ET.ElementTree(root)
output_path = Path(__file__).parent / "data" / "exam_meta.xml"
tree.write(output_path, encoding="utf-8", xml_declaration=True)

# ---- 统计 ----
obj_total = sub_total = quiz_count = 0
for exam in root.findall("exam"):
    obj = exam.find("subjective")
    sub = exam.find("objective")
    obj_n = len(obj.findall("topic")) if obj is not None else 0
    sub_n = len(sub.findall("topic")) if sub is not None else 0
    obj_total += obj_n
    sub_total += sub_n
    if sub_n == 0:
        quiz_count += 1

print(f"已生成 {output_path}")
print(f"  考试数: {len(dates)}")
print(f"  客观题知识点总数: {obj_total} (平均 {obj_total/len(dates):.1f}/场)")
print(f"  主观题知识点总数: {sub_total} (平均 {sub_total/(len(dates)-quiz_count):.1f}/场)")
print(f"  测验型考试: {quiz_count} 场")
