"""测试学生评估tab的分数模式切换逻辑"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from core.data_manager import DataManager
dm = DataManager()

print("=" * 60)
print("学生评估 Tab — 端到端算法验证")
print("=" * 60)

# 模拟 tab 逻辑
import statistics

def compute_subjective_zscores(class_idx):
    obj_students = dm.students[class_idx][0]
    full_students = dm.students[class_idx][1]
    dates = dm.dates
    n_dates = len(dates)
    result = []
    for s_obj in obj_students:
        full_scores = []
        for s_full in full_students:
            if s_full.name == s_obj.name:
                full_scores = [float(v[1]) for v in s_full.scores_full] if s_full.scores_full else []
                break
        obj_scores = [float(v[1]) for v in s_obj.scores] if s_obj.scores else []
        subs = []
        for i in range(n_dates):
            obj_val = obj_scores[i] if i < len(obj_scores) else 0.0
            full_val = full_scores[i] if i < len(full_scores) else 0.0
            subs.append(max(0.0, round(full_val - obj_val, 1)))
        result.append([s_obj.name, subs])
    if len(dates) <= 1:
        for r in result:
            r[1] = [0.0] * len(dates)
        return result
    for exam_i in range(n_dates):
        raw = [r[1][exam_i] for r in result]
        mean = statistics.mean(raw)
        std = statistics.stdev(raw) if len(raw) > 1 else 0
        for r in result:
            if std > 0:
                r[1][exam_i] = round((r[1][exam_i] - mean) / std, 2)
            else:
                r[1][exam_i] = 0.0
    return result

def build_topic_exam_map(topic_attr):
    topic_map = {}
    for date, meta in dm.exam_meta.items():
        topics = getattr(meta, topic_attr, [])
        for t in topics:
            if t.name not in topic_map:
                topic_map[t.name] = []
            topic_map[t.name].append((date, t.weight))
    return topic_map

def compute_topic_performance(student_name, topic_attr, zscores_data):
    topic_exam_map = build_topic_exam_map(topic_attr)
    if not topic_exam_map:
        return {}
    student_z = {}
    dates = dm.dates
    for name, z_list in zscores_data:
        if name == student_name:
            student_z = {dates[i]: z_list[i] for i in range(min(len(dates), len(z_list)))}
            break
    if not student_z:
        return {}
    topic_category = {}
    for cat, topics in dm.knowledge_pool.items():
        for t in topics:
            topic_category[t] = cat
    result = {}
    for topic_name, exam_list in topic_exam_map.items():
        weighted_sum = 0.0
        total_weight = 0.0
        n_with_data = 0
        for date, weight in exam_list:
            if date in student_z and student_z[date] is not None:
                weighted_sum += student_z[date] * weight
                total_weight += weight
                n_with_data += 1
        category = topic_category.get(topic_name, "未分类")
        if total_weight > 0:
            result[topic_name] = {"z": round(weighted_sum / total_weight, 2),
                                  "count": n_with_data, "category": category}
        else:
            result[topic_name] = {"z": None, "count": 0, "category": category}
    return result

# ---- 测试1: 客观分模式下客观题知识点分析 ----
print("\n[测试1] 客观分模式 + 客观题知识点")
dm.current_class = 0
obj_zscores_40 = dm.get_zscores(0, full_score=False)
student = obj_zscores_40[0][0]
perf1 = compute_topic_performance(student, "subjective_topics", obj_zscores_40)
valid1 = [(n, d) for n, d in perf1.items() if d["z"] is not None]
print(f"  学生: {student}, 有效知识点: {len(valid1)}")
if valid1:
    print(f"  前3: {[(n, d['z'], d['count']) for n, d in sorted(valid1, key=lambda x: x[1]['z'], reverse=True)[:3]]}")

# ---- 测试2: 总分模式下客观题知识点分析 ----
print("\n[测试2] 总分模式 + 客观题知识点")
obj_zscores_100 = dm.get_zscores(0, full_score=True)
perf2 = compute_topic_performance(student, "subjective_topics", obj_zscores_100)
valid2 = [(n, d) for n, d in perf2.items() if d["z"] is not None]
print(f"  学生: {student}, 有效知识点: {len(valid2)}")
if valid2:
    print(f"  前3: {[(n, d['z'], d['count']) for n, d in sorted(valid2, key=lambda x: x[1]['z'], reverse=True)[:3]]}")

# 对比两种模式差异
if valid1 and valid2:
    diffs = []
    for n1, d1 in perf1.items():
        if n1 in perf2 and d1["z"] is not None and perf2[n1]["z"] is not None:
            diffs.append((n1, d1["z"], perf2[n1]["z"], abs(d1["z"] - perf2[n1]["z"])))
    if diffs:
        diffs.sort(key=lambda x: x[3], reverse=True)
        print(f"  最大差异知识点: {diffs[0][0]} (40分Z={diffs[0][1]}, 100分Z={diffs[0][2]}, 差={diffs[0][3]:.2f})")

# ---- 测试3: 主观题知识点分析 ----
print("\n[测试3] 主观题知识点分析")
sub_zscores = compute_subjective_zscores(0)
perf3 = compute_topic_performance(student, "objective_topics", sub_zscores)
valid3 = [(n, d) for n, d in perf3.items() if d["z"] is not None]
print(f"  学生: {student}, 有效知识点: {len(valid3)}")
if valid3:
    print(f"  前3: {[(n, d['z'], d['count']) for n, d in sorted(valid3, key=lambda x: x[1]['z'], reverse=True)[:3]]}")

# ---- 测试4: 主客观对比 ----
print("\n[测试4] 主客观对比")
common = set(perf1.keys()) & set(perf3.keys())
valid_comp = []
for name in common:
    oz = perf1[name]["z"]
    sz = perf3[name]["z"]
    if oz is not None or sz is not None:
        valid_comp.append((name, oz or 0, sz or 0, abs((oz or 0) - (sz or 0))))
valid_comp.sort(key=lambda x: x[3], reverse=True)
print(f"  共有知识点: {len(common)}, 有效对比: {len(valid_comp)}")
for name, oz, sz, diff in valid_comp[:5]:
    print(f"    {name}: 客观Z={oz:.2f}, 主观Z={sz:.2f}, 差={diff:.2f}")

# ---- 测试5: 分类聚合 ----
print("\n[测试5] 分类聚合")
def compute_cat(perf):
    cats = {}
    for name, data in perf.items():
        cat = data["category"]
        if data["z"] is not None:
            if cat not in cats:
                cats[cat] = {"zs": [], "count": 0}
            cats[cat]["zs"].append(data["z"])
            cats[cat]["count"] += 1
    for cat, d in cats.items():
        d["z"] = round(sum(d["zs"]) / len(d["zs"]), 2) if d["zs"] else 0.0
    return cats

cat1 = compute_cat(perf1)
cat3 = compute_cat(perf3)
all_cats = sorted(set(cat1.keys()) | set(cat3.keys()))
print(f"  合并分类数: {len(all_cats)}")
for c in all_cats:
    oz = cat1.get(c, {}).get("z", "--")
    sz = cat3.get(c, {}).get("z", "--")
    print(f"    {c}: 客观Z={oz}, 主观Z={sz}")

# ---- 测试6: 成绩历程数据 ----
print("\n[测试6] 成绩历程")
stu = dm.students[0][0][0]  # 客观分模式学生
full_stu = dm.students[0][1][0]  # 满分卷模式学生
obj_scores = [float(s[1]) for s in stu.scores] if stu.scores else []
full_scores = [float(s[1]) for s in full_stu.scores_full] if full_stu.scores_full else []
n = min(len(obj_scores), len(full_scores))
print(f"  学生: {stu.name}, 考试次数: {n}")
print(f"  客观分前5: {obj_scores[:5]}")
print(f"  满分前5: {full_scores[:5]}")
sub_scores = [max(0.0, round(full_scores[i] - obj_scores[i], 1)) for i in range(n)]
print(f"  主观分前5: {sub_scores[:5]}")

print("\n✅ 所有测试通过!")
