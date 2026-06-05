"""批量生成两个月的模拟考试数据"""
import csv
import random
import xml.etree.ElementTree as ET
from pathlib import Path

random.seed(42)

DATA_DIR = Path(__file__).parent / "data"
SCORE_DIR = DATA_DIR / "question_scores"
SCORE_DIR.mkdir(exist_ok=True)

CLASSES = ["A01", "A02", "A03"]

QUIZ_DATES = [
    "2025_09_01", "2025_09_02", "2025_09_03", "2025_09_04", "2025_09_05",
    "2025_09_08", "2025_09_09", "2025_09_10", "2025_09_11", "2025_09_12",
    "2025_09_15", "2025_09_16", "2025_09_17", "2025_09_18", "2025_09_19",
    "2025_09_22", "2025_09_23", "2025_09_24", "2025_09_25", "2025_09_26",
    "2025_10_06", "2025_10_07", "2025_10_08", "2025_10_09", "2025_10_10",
    "2025_10_13", "2025_10_14", "2025_10_15", "2025_10_16", "2025_10_17",
    "2025_10_20", "2025_10_21", "2025_10_22", "2025_10_23", "2025_10_24",
    "2025_10_27", "2025_10_28", "2025_10_29", "2025_10_30", "2025_10_31",
]
EXAM_DATES = [
    "2025_09_07",
    "2025_09_21",
    "2025_10_12",
    "2025_10_26",
]

EXAM_MAX = [5]*8 + [6]*3 + [5]*3 + [13, 15, 15, 17, 17]


def load_students(cls_name: str) -> list[dict]:
    tree = ET.parse(DATA_DIR / f"data_{cls_name}.xml")
    return [
        {"id": e.get("id", ""), "name": e.findtext("name", "").strip()}
        for e in tree.findall("student")
    ]


def gen_quiz_config() -> tuple[int, int]:
    """生成测验题目配置，返回 (总题数, 多选题数)"""
    n_total = random.randint(6, 12)
    n_multi = random.randint(2, min(4, n_total - 2))
    return n_total, n_multi


def gen_quiz_scores(ability: float, n_single: int, n_multi: int) -> list[int]:
    """生成一个学生的测验得分

    单选: 5分，对/错
    多选: 6分，全对=6，部分对按比例(如2/3=4)，有错选=0
    """
    scores = []
    # 单选题
    for _ in range(n_single):
        scores.append(5 if random.random() < ability else 0)
    # 多选题
    for _ in range(n_multi):
        n_correct = random.randint(2, 3)  # 正确选项数(2或3个)
        r = random.random()
        if r < ability * 0.6:
            # 全对
            scores.append(6)
        elif r < ability * 0.85:
            # 部分对(选中部分正确选项，无错选)
            n_picked = random.randint(1, n_correct - 1)
            partial = round(6 * n_picked / n_correct)
            scores.append(partial)
        else:
            # 错选(选了错误选项)
            scores.append(0)
    return scores


def gen_exam_row(ability: float) -> list[int]:
    scores = []
    # 单选 Q1-Q8: 5分
    for _ in range(8):
        scores.append(5 if random.random() < ability else 0)
    # 多选 Q9-Q11: 6分
    for _ in range(3):
        n_correct = random.randint(2, 3)
        r = random.random()
        if r < ability * 0.6:
            scores.append(6)
        elif r < ability * 0.85:
            n_picked = random.randint(1, n_correct - 1)
            scores.append(round(6 * n_picked / n_correct))
        else:
            scores.append(0)
    # 填空 Q12-Q14: 5分
    for _ in range(3):
        scores.append(5 if random.random() < ability else 0)
    # 解答 Q15-Q19: 13,15,15,17,17分
    for mx in [13, 15, 15, 17, 17]:
        ratio = ability * random.uniform(0.5, 1.0)
        score = round(mx * ratio)
        score = min(score, mx - 1) if ability > 0.95 else score
        scores.append(max(0, min(score, mx)))
    return scores


# 《实力主义至上教室》角色 —— 高能力学生
ELITE_OVERRIDES = {
    # 绫小路清隆：隐藏实力的天才，全年级最强
    "绫小路清隆": (0.93, 0.98),
    # 坂柳有栖：A班领袖，天才级
    "坂柳有栖": (0.90, 0.96),
    # 堀北铃音：优等生，成绩拔尖
    "堀北铃音": (0.85, 0.92),
    # 一之濑帆波：B班领袖，综合能力强
    "一之濑帆波": (0.82, 0.90),
    # 龙园翔：C班领袖，策略型，成绩中上
    "龙园翔": (0.70, 0.82),
    # 栉田桔梗：表面乖巧，成绩中上
    "栉田桔梗": (0.72, 0.82),
    # 轻井泽惠：隐藏实力型，成绩中等偏上
    "轻井泽惠": (0.65, 0.78),
}


def assign_abilities(names: list[str], seed_offset: int = 0) -> list[float]:
    random.seed(42 + seed_offset)
    abilities = []
    for name in names:
        if name in ELITE_OVERRIDES:
            lo, hi = ELITE_OVERRIDES[name]
            abilities.append(random.uniform(lo, hi))
        else:
            abilities.append(random.uniform(0.20, 0.95))
    return abilities


def write_csv(path: Path, header: list[str], rows: list[list]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def fix_perfect(rows: list[list], score_start: int, n_score_cols: int, max_total: int):
    for row in rows:
        scores = row[score_start:score_start + n_score_cols]
        if sum(scores) >= max_total:
            for i in range(len(scores)-1, -1, -1):
                if row[score_start + i] > 0:
                    row[score_start + i] -= 1
                    break


def wrong_obj_questions(scores: list[int], maxs: list[int], n_obj: int) -> str:
    """客观题中得0分的题号"""
    wrong = []
    for i in range(n_obj):
        if scores[i] == 0:
            wrong.append(f"Q{i+1}")
    return ",".join(wrong)


def generate_for_class(cls_name: str, ability_seed: int):
    students = load_students(cls_name)
    n = len(students)
    names = [s["name"] for s in students]
    abilities = assign_abilities(names, ability_seed)
    quiz_count = 0
    exam_count = 0

    # 测验：题数不固定，含多选
    for date in QUIZ_DATES:
        random.seed(hash(date + cls_name) % 2**31)
        n_total, n_multi = gen_quiz_config()
        n_single = n_total - n_multi
        maxs = [5]*n_single + [6]*n_multi
        max_total = sum(maxs)

        header = ["考号", "姓名"] + [f"Q{i+1}" for i in range(n_total)] + \
                 ["客观总分", "主观总分", "全卷总分", "客观错题题号"]
        rows = []
        for stu, abil in zip(students, abilities):
            scores = gen_quiz_scores(abil, n_single, n_multi)
            obj_total = sum(scores)
            row = [stu["id"], stu["name"]] + scores + \
                  [obj_total, "", obj_total,
                   wrong_obj_questions(scores, maxs, n_total)]
            rows.append(row)

        fix_perfect(rows, 2, n_total, max_total)
        # 重算总分和错题
        for row in rows:
            scores = row[2:2+n_total]
            row[2+n_total] = sum(scores)
            row[2+n_total+2] = row[2+n_total]
            row[2+n_total+3] = wrong_obj_questions(scores, maxs, n_total)

        write_csv(SCORE_DIR / f"quiz_{date}_{cls_name}.csv", header, rows)
        quiz_count += 1

    # 正式考试：固定19题
    for date in EXAM_DATES:
        random.seed(hash(date + cls_name) % 2**31)
        header = ["考号", "姓名"] + [f"Q{i+1}" for i in range(19)] + \
                 ["客观总分", "主观总分", "全卷总分", "客观错题题号"]
        rows = []
        for stu, abil in zip(students, abilities):
            scores = gen_exam_row(abil)
            obj_total = sum(scores[:14])
            sub_total = sum(scores[14:])
            row = [stu["id"], stu["name"]] + scores + \
                  [obj_total, sub_total, obj_total + sub_total,
                   wrong_obj_questions(scores, EXAM_MAX, 14)]
            rows.append(row)

        fix_perfect(rows, 2, 19, sum(EXAM_MAX))
        for row in rows:
            scores = row[2:21]
            row[21] = sum(scores[:14])
            row[22] = sum(scores[14:])
            row[23] = row[21] + row[22]
            row[24] = wrong_obj_questions(scores, EXAM_MAX, 14)

        write_csv(SCORE_DIR / f"exam_{date}_{cls_name}.csv", header, rows)
        exam_count += 1

    return quiz_count, exam_count


def main():
    total = 0
    for i, cls in enumerate(CLASSES):
        q, e = generate_for_class(cls, ability_seed=i*100)
        total += q + e
        print(f"{cls}: {q} 次测验 + {e} 次正式考试 = {q+e} 个文件")
    print(f"\n总计: {total} 个文件 → {SCORE_DIR}")


if __name__ == "__main__":
    main()
