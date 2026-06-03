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

# 分值结构
EXAM_MAX = [5]*8 + [6]*3 + [5]*3 + [13, 15, 15, 17, 17]  # Q1-Q19
QUIZ_MAX = [5]*8  # Q1-Q8


def load_students(cls_name: str) -> list[dict]:
    """返回 [{"id": "100001", "name": "张三"}, ...]"""
    tree = ET.parse(DATA_DIR / f"data_{cls_name}.xml")
    return [
        {"id": e.get("id", ""), "name": e.findtext("name", "").strip()}
        for e in tree.findall("student")
    ]


def gen_quiz_row(ability: float) -> list[int]:
    scores = []
    for _ in range(8):
        scores.append(5 if random.random() < ability else 0)
    return scores


def gen_exam_row(ability: float) -> list[int]:
    scores = []
    for _ in range(8):
        scores.append(5 if random.random() < ability else 0)
    for _ in range(3):
        r = random.random()
        if r < ability * 0.7:
            scores.append(6)
        elif r < ability * 0.9:
            scores.append(3)
        else:
            scores.append(0)
    for _ in range(3):
        scores.append(5 if random.random() < ability else 0)
    for mx in [13, 15, 15, 17, 17]:
        ratio = ability * random.uniform(0.5, 1.0)
        score = round(mx * ratio)
        score = min(score, mx - 1) if ability > 0.95 else score
        scores.append(max(0, min(score, mx)))
    return scores


def assign_abilities(n: int, seed_offset: int = 0) -> list[float]:
    random.seed(42 + seed_offset)
    return [random.uniform(0.2, 0.95) for _ in range(n)]


def write_csv(path: Path, header: list[str], rows: list[list]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def fix_perfect(rows: list[list], score_start: int, n_score_cols: int, max_total: int):
    """修复满分：扣掉最后一道解答题1分"""
    for row in rows:
        scores = row[score_start:score_start + n_score_cols]
        if sum(scores) >= max_total:
            for i in range(len(scores)-1, -1, -1):
                if scores[i] > 0:
                    row[score_start + i] -= 1
                    break


def wrong_obj_questions(scores: list[int], maxs: list[int], n_obj: int) -> str:
    """返回客观题错题题号，逗号分隔。n_obj = 客观题数量"""
    wrong = []
    for i in range(n_obj):
        if scores[i] == 0:
            wrong.append(f"Q{i+1}")
    return ",".join(wrong)


def generate_for_class(cls_name: str, ability_seed: int):
    students = load_students(cls_name)
    n = len(students)
    abilities = assign_abilities(n, ability_seed)
    quiz_count = 0
    exam_count = 0

    # 测验
    for date in QUIZ_DATES:
        random.seed(hash(date + cls_name) % 2**31)
        header = ["考号", "姓名", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8",
                  "客观总分", "主观总分", "全卷总分", "客观错题题号"]
        rows = []
        for stu, abil in zip(students, abilities):
            scores = gen_quiz_row(abil)
            obj_total = sum(scores)
            row = [stu["id"], stu["name"]] + scores + [obj_total, "", obj_total,
                   wrong_obj_questions(scores, QUIZ_MAX, 8)]
            rows.append(row)
        fix_perfect(rows, 2, 8, sum(QUIZ_MAX))
        # 重新计算修复后的总分
        for row in rows:
            scores = row[2:10]
            row[10] = sum(scores)
            row[12] = row[10]
            row[13] = wrong_obj_questions(scores, QUIZ_MAX, 8)
        write_csv(SCORE_DIR / f"quiz_{date}_{cls_name}.csv", header, rows)
        quiz_count += 1

    # 正式考试
    for date in EXAM_DATES:
        random.seed(hash(date + cls_name) % 2**31)
        header = ["考号", "姓名"] + [f"Q{i+1}" for i in range(19)] + \
                 ["客观总分", "主观总分", "全卷总分", "客观错题题号"]
        rows = []
        for stu, abil in zip(students, abilities):
            scores = gen_exam_row(abil)
            obj_total = sum(scores[:14])
            sub_total = sum(scores[14:])
            row = [stu["id"], stu["name"]] + scores + [obj_total, sub_total,
                   obj_total + sub_total,
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
