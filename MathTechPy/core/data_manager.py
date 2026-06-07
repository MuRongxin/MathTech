"""数据管理器 - 支持任意数量班级的动态数据管理

优化点：
1. 班级数据用列表存储，不再硬编码 students_1/students_2
2. 从 config.xml 自动识别所有班级配置
3. O(1) name->student 映射
4. 所有路径使用 Path，跨平台安全
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Optional
import re
from .models import StudentData, ClassInfo, KnowledgeTopic, Question, ExamMeta

# 非题目列的常见字段名（这些列不会被识别为题目）
KNOWN_META_COLUMNS = {
    "考号", "姓名", "学号", "班级", "班别", "座号", "序号",
    "客观总分", "主观总分", "全卷总分", "总分", "总成绩",
    "客观错题题号", "主观错题题号", "错题题号",
    "客观分", "主观分", "卷面分", "原始分", "标准分",
    "排名", "班排", "级排", "校排",
    "客观题得分", "主观题得分", "选择题得分", "非选择题得分",
    "student_id", "student_name", "class", "total_score", "score",
    "objective_score", "subjective_score", "full_score",
}


class DataManager:
    """数据管理器单例"""
    _instance: Optional["DataManager"] = None

    def __new__(cls) -> "DataManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.data_dir = Path(__file__).parent.parent / "data"
        self.config_path = self.data_dir / "config.xml"

        # 班级数据列表：
        # students[class_idx][mode] -> List[StudentData]
        # mode 0=客观分, 1=满分卷
        self.students: List[List[List[StudentData]]] = []
        self.class_names: List[str] = []

        self.current_class: int = 0  # 当前选中班级的索引

        # 考试日期列表（从 Excel 表头读取）
        self.dates: List[str] = []

        # 逐题分目录（_load_all 先收集，_init_knowledge 之后加载）
        self._question_score_dir: Optional[Path] = None

        # 知识点池：一级分类 → [二级知识点列表]
        self.knowledge_pool: Dict[str, List[str]] = {}
        # 分类显示顺序
        self.category_order: List[str] = []
        # 考试元数据：date_str → ExamMeta
        self.exam_meta: Dict[str, ExamMeta] = {}

        self._needs_init = False
        try:
            self._load_all()
        except (FileNotFoundError, ValueError, ET.ParseError) as e:
            print(f"[INFO] 配置缺失，需要初始化: {e}")
            self._needs_init = True
            self._init_knowledge()
            self._initialized = True
            return

        self._init_knowledge()
        self._load_question_scores()
        self._validate()
        self._initialized = True

    @property
    def class_count(self) -> int:
        return len(self.students)

    # ------------------------------------------------------------------
    # 加载
    # ------------------------------------------------------------------
    def _load_all(self) -> None:
        """加载学生名册，分数由 _load_question_scores 统一导入"""
        config = ET.parse(self.config_path).getroot()
        xml_elems = [e for e in config.findall("classMembers") if e.text]

        if not xml_elems:
            raise ValueError("config.xml 中未配置任何班级数据")

        xml_files = [self.data_dir / e.text.strip() for e in xml_elems]

        # 解析班级名称
        self.class_names = []
        for e in xml_elems:
            fname = e.text.strip()
            m = re.search(r'[A-Za-z]*(\d+)', fname)
            if m:
                self.class_names.append(f"A{m.group(1).zfill(2)}")
            else:
                self.class_names.append(fname)

        # 逐题分目录（固定路径）
        self._question_score_dir = self.data_dir / "question_scores"

        # 加载每个班级的学生名册（分数初始为空，由 _load_question_scores 填充）
        self.students = []
        for xml_path in xml_files:
            base = self._load_xml(xml_path)
            obj_students = [StudentData(s.id, s.name, s.call_count) for s in base]
            full_students = [StudentData(s.id, s.name, s.call_count) for s in base]
            sub_students = [StudentData(s.id, s.name, s.call_count) for s in base]
            self.students.append([obj_students, full_students, sub_students])

    def _load_question_scores(self) -> None:
        """扫描 question_scores/ 目录，加载逐题分并更新总分"""
        if not self._question_score_dir or not self._question_score_dir.exists():
            return

        mtimes = {}
        # 按班级分组所有学生 {class_idx: {name: (obj_stu, full_stu, sub_stu)}}
        class_maps = []
        for ci in range(self.class_count):
            obj_map = {s.name: s for s in self.students[ci][0]}
            full_map = {s.name: s for s in self.students[ci][1]}
            sub_map = {s.name: s for s in self.students[ci][2]}
            class_maps.append((obj_map, full_map, sub_map))

        # 已知班级后缀
        class_suffixes = [cn.replace("A", "") for cn in self.class_names]

        imported_dates: set[str] = set()

        for fpath in sorted(self._question_score_dir.glob("*")):
            if fpath.suffix.lower() not in (".csv", ".xlsx"):
                continue
            # 解析文件名: quiz_2025_09_01_A01.csv 或 exam_2025_09_07_A01.xlsx
            stem = fpath.stem
            parts = stem.split("_")
            if len(parts) < 5:
                continue
            etype = parts[0]          # quiz or exam
            date_str = f"{parts[1]}/{parts[2]}/{parts[3]}"  # 2025/09/01
            class_suffix = parts[4].replace("A", "")         # 01, 02, 03

            # 匹配班级索引
            try:
                class_idx = class_suffixes.index(class_suffix)
            except ValueError:
                print(f"[WARN] 逐题分文件班级 {parts[4]} 不在配置中: {fpath.name}")
                continue

            print(f"[INFO] 加载逐题分: {fpath.name} → 日期={date_str}, 班级=A{class_suffix}, 类型={etype}")

            try:
                if fpath.suffix.lower() == ".csv":
                    q_rows, obj_total_col, sub_total_col, full_total_col = \
                        self._parse_question_csv(fpath)
                else:
                    q_rows, obj_total_col, sub_total_col, full_total_col = \
                        self._parse_question_xlsx(fpath)
            except Exception as e:
                print(f"[WARN] 无法解析 {fpath.name}: {e}")
                continue

            obj_map, full_map, sub_map = class_maps[class_idx]

            # 为每个学生分配逐题分并更新总分
            matched = 0
            for name, row_data in q_rows.items():
                q_scores = row_data["questions"]
                stu_obj = obj_map.get(name)
                stu_full = full_map.get(name)
                stu_sub = sub_map.get(name)

                if stu_obj:
                    stu_obj.question_scores[date_str] = q_scores
                if stu_full:
                    stu_full.question_scores[date_str] = q_scores
                if stu_sub:
                    stu_sub.question_scores[date_str] = q_scores

                if not stu_obj and not stu_full:
                    continue
                matched += 1

                # 客观总分
                if obj_total_col and row_data["obj_total"] is not None:
                    new_score_str = f"{row_data['obj_total']:.2f}"
                    if stu_obj:
                        self._upsert_score(stu_obj.scores, date_str, new_score_str)
                # 主观总分
                if sub_total_col and row_data["sub_total"] is not None:
                    new_score_str = f"{row_data['sub_total']:.2f}"
                    if stu_sub:
                        self._upsert_score(stu_sub.scores_sub, date_str, new_score_str)
                # 全卷总分
                if full_total_col and row_data["full_total"] is not None:
                    new_score_str = f"{row_data['full_total']:.2f}"
                    if stu_full:
                        self._upsert_score(stu_full.scores_full, date_str, new_score_str)

                # 兜底：缺总分列时从逐题分自动加总
                has_obj = obj_total_col and row_data["obj_total"] is not None
                has_full = full_total_col and row_data["full_total"] is not None
                has_sub = sub_total_col and row_data["sub_total"] is not None
                q_sum = sum(q_scores.values())
                if not has_obj or not has_full or not has_sub:
                    # 尝试从 exam_meta 分题型
                    meta = self.exam_meta.get(date_str)
                    obj_qids = set()
                    if meta and meta.questions:
                        for q in meta.questions:
                            if q.qtype in ("choice", "multi_select"):
                                obj_qids.add(q.id)
                    if obj_qids:
                        obj_sum = sum(q_scores.get(qid, 0.0) for qid in obj_qids)
                        sub_sum = sum(q_scores.get(qid, 0.0) for qid in q_scores if qid not in obj_qids)
                    else:
                        obj_sum = q_sum
                        sub_sum = 0.0
                    if not has_obj and obj_sum > 0 and stu_obj:
                        self._upsert_score(stu_obj.scores, date_str, f"{obj_sum:.2f}")
                    if not has_full and q_sum > 0 and stu_full:
                        self._upsert_score(stu_full.scores_full, date_str, f"{q_sum:.2f}")
                    if not has_sub and stu_sub:
                        if has_full and has_obj:
                            sub_val = max(0.0, (row_data["full_total"] or 0) - (row_data["obj_total"] or 0))
                        else:
                            sub_val = sub_sum
                        if sub_val > 0:
                            self._upsert_score(stu_sub.scores_sub, date_str, f"{sub_val:.2f}")

            print(f"[INFO]   匹配 {matched}/{len(q_rows)} 名学生")

            # 将新日期加入 dates 列表
            if date_str not in self.dates:
                self.dates.append(date_str)
                self.dates.sort()
            imported_dates.add(date_str)

            # 自动检测题目结构
            if date_str not in self.exam_meta or not self.exam_meta[date_str].questions:
                all_qscores = [r["questions"] for r in q_rows.values() if r["questions"]]
                if all_qscores:
                    questions = self._detect_questions(all_qscores, etype)
                    if questions:
                        meta = self.get_exam_meta(date_str)
                        meta.questions = questions
                        print(f"[INFO]   自动检测 {len(questions)} 道题")

        if imported_dates:
            self._save_exam_meta()

    def _upsert_score(self, score_list: List[List[str]], date: str, score_str: str):
        """在成绩列表中更新或插入某日期的成绩"""
        for i, (d, _) in enumerate(score_list):
            if d == date:
                score_list[i][1] = score_str
                return
        score_list.append([date, score_str])
        score_list.sort(key=lambda x: x[0])

    def _parse_question_csv(self, path: Path) -> tuple:
        """解析逐题分 CSV

        返回: (q_rows, has_obj_total, has_sub_total, has_full_total)
          q_rows = {student_name: {"questions": {qid: score}, "obj_total": float|None, ...}}
        """
        import csv
        with open(path, "r", encoding="utf-8-sig") as f:
            all_rows = list(csv.reader(f))

        # 跳过标题行，找真正的列头行，记录行号
        headers = []
        header_row_idx = 0
        for ri, row in enumerate(all_rows[:5]):
            candidates = [h.strip() for h in row if h and h.strip()]
            valid = sum(1 for h in candidates
                       if h in KNOWN_META_COLUMNS or any(ch.isdigit() for ch in h))
            if valid >= 2:
                headers = [h.strip() for h in row]
                header_row_idx = ri
                break
        if not headers:
            return {}, False, False, False

        # 识别列：不在元数据字典中 + 列名含数字 → 题目列
        obj_total_idx = sub_total_idx = full_total_idx = None
        q_cols = []
        for i, h in enumerate(headers):
            if h in KNOWN_META_COLUMNS:
                if h in ("客观总分", "objective_score"):
                    obj_total_idx = i
                elif h in ("主观总分", "subjective_score"):
                    sub_total_idx = i
                elif h in ("全卷总分", "总分", "总成绩", "full_score", "total_score", "score"):
                    full_total_idx = i
            elif any(ch.isdigit() for ch in h):
                q_cols.append((i, h))

        q_rows = {}
        for row in all_rows[header_row_idx + 1:]:
                if not row or len(row) < 2:
                    continue
                name = row[1].strip() if len(row) > 1 else ""
                if not name:
                    continue

                q_scores = {}
                for idx, qid in q_cols:
                    if idx < len(row) and row[idx]:
                        try:
                            q_scores[qid] = float(row[idx])
                        except ValueError:
                            q_scores[qid] = 0.0

                obj_total = None
                sub_total = None
                full_total = None
                if obj_total_idx is not None and obj_total_idx < len(row) and row[obj_total_idx]:
                    try:
                        obj_total = float(row[obj_total_idx])
                    except ValueError:
                        pass
                if sub_total_idx is not None and sub_total_idx < len(row) and row[sub_total_idx]:
                    try:
                        sub_total = float(row[sub_total_idx])
                    except ValueError:
                        pass
                if full_total_idx is not None and full_total_idx < len(row) and row[full_total_idx]:
                    try:
                        full_total = float(row[full_total_idx])
                    except ValueError:
                        pass

                q_rows[name] = {
                    "questions": q_scores,
                    "obj_total": obj_total,
                    "sub_total": sub_total,
                    "full_total": full_total,
                }

        # 检查主观分列是否有数据（采样多行，避免第一行恰巧为空）
        sample_rows = list(q_rows.values())[:5]
        has_sub = any(r.get("sub_total") is not None for r in sample_rows)
        has_full = any(r.get("full_total") is not None for r in sample_rows)
        return q_rows, obj_total_idx is not None, sub_total_idx is not None and has_sub, full_total_idx is not None and has_full

    def _parse_question_xlsx(self, path: Path) -> tuple:
        """解析逐题分 Excel（与 CSV 同格式：考号,姓名,Q1...Qn,客观总分,主观总分,全卷总分,客观错题题号）"""
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            wb.close()
            return {}, False, False, False

        # 跳过标题行，找真正的列头行
        header = []
        header_row_idx = 0
        for ri, row in enumerate(rows[:5]):
            candidates = [str(h).strip() for h in row if h is not None and str(h).strip()]
            valid = sum(1 for h in candidates
                       if h in KNOWN_META_COLUMNS or any(ch.isdigit() for ch in h))
            if valid >= 2:
                header = [str(h).strip() if h else "" for h in row]
                header_row_idx = ri
                break
        if not header:
            wb.close()
            return {}, False, False, False

        # 识别列：不在元数据字典中 + 列名含数字 → 题目列
        obj_total_idx = sub_total_idx = full_total_idx = None
        q_cols = []
        for i, h in enumerate(header):
            if h in KNOWN_META_COLUMNS:
                if h in ("客观总分", "objective_score"):
                    obj_total_idx = i
                elif h in ("主观总分", "subjective_score"):
                    sub_total_idx = i
                elif h in ("全卷总分", "总分", "总成绩", "full_score", "total_score", "score"):
                    full_total_idx = i
            elif any(ch.isdigit() for ch in h):
                q_cols.append((i, h))

        q_rows = {}
        for row in rows[header_row_idx + 1:]:
            if not row or len(row) < 2:
                continue
            name = str(row[1]).strip() if len(row) > 1 else ""
            if not name:
                continue

            q_scores = {}
            for idx, qid in q_cols:
                val = row[idx] if idx < len(row) else None
                if val is not None:
                    try:
                        q_scores[qid] = float(val)
                    except (ValueError, TypeError):
                        q_scores[qid] = 0.0

            def _get(idx):
                if idx is not None and idx < len(row) and row[idx] is not None:
                    try:
                        return float(row[idx])
                    except (ValueError, TypeError):
                        pass
                return None

            q_rows[name] = {
                "questions": q_scores,
                "obj_total": _get(obj_total_idx),
                "sub_total": _get(sub_total_idx),
                "full_total": _get(full_total_idx),
            }

        wb.close()

        sample_rows = list(q_rows.values())[:5]
        has_sub = any(r.get("sub_total") is not None for r in sample_rows)
        has_full = any(r.get("full_total") is not None for r in sample_rows)
        return q_rows, obj_total_idx is not None, sub_total_idx is not None and has_sub, full_total_idx is not None and has_full

    def _detect_questions(self, all_qscores: List[dict], etype: str = "quiz") -> List:
        """从全班逐题分推断题目结构（结合考试类型和得分分布）"""
        from .models import Question as QModel
        # 按题号收集所有学生的得分
        qid_scores: dict[str, list[float]] = {}
        for qs in all_qscores:
            for qid, score in qs.items():
                qid_scores.setdefault(qid, []).append(score)

        questions = []
        for qid in sorted(qid_scores.keys(),
                          key=lambda x: (not x[1:].isdigit(), int(x[1:]) if x[1:].isdigit() else 0)):
            scores = qid_scores[qid]
            max_seen = max(scores) if scores else 5.0
            unique_vals = set(scores)
            max_score = max(1.0, round(max_seen)) if max_seen > 0 else 5.0

            # 提取题号数字
            qnum = int(qid[1:]) if qid[1:].isdigit() else 0

            # 按考试类型 + 题号推断题型
            if etype == "exam":
                # 正式考试精确结构: Q1-8单选(5') Q9-11多选(6') Q12-14填空(5') Q15-19解答(13-17')
                if 1 <= qnum <= 8:
                    qtype = "choice"
                    max_score = 5
                elif 9 <= qnum <= 11:
                    qtype = "multi_select"
                    max_score = 6
                elif 12 <= qnum <= 14:
                    qtype = "fill"
                    max_score = 5
                elif qnum == 15:
                    qtype = "answer"; max_score = 13
                elif qnum in (16, 17):
                    qtype = "answer"; max_score = 15
                elif qnum in (18, 19):
                    qtype = "answer"; max_score = 17
                else:
                    qtype = "fill" if max_score <= 10 else "answer"
            elif max_score == 6 and any(v not in (0.0, 6.0) for v in unique_vals):
                qtype = "multi_select"   # quiz 中多选：max=6 且存在中间分
            elif etype == "quiz":
                qtype = "choice"          # 测验默认选择题
            elif max_score > 10:
                qtype = "answer"
            else:
                qtype = "fill"

            questions.append(QModel(id=qid, qtype=qtype, max_score=max_score))
        return questions

    def _load_xml(self, path: Path) -> List[StudentData]:
        """读取班级 XML"""
        tree = ET.parse(path)
        students: List[StudentData] = []
        for elem in tree.findall("student"):
            sid = int(elem.get("id", 0))
            name = elem.findtext("name", "").strip()
            call = int(elem.findtext("callCount", "0"))
            students.append(StudentData(id=sid, name=name, call_count=call))
        return students

    def _validate(self) -> None:
        """数据完整性校验"""
        for ci, class_data in enumerate(self.students):
            for mi, mode_name in [(0, "客观分"), (1, "全卷分"), (2, "主观分")]:
                students = class_data[mi]
                attr = ["scores", "scores_full", "scores_sub"][mi]
                no_score = [s.name for s in students if not getattr(s, attr)]
                if no_score:
                    print(f"[WARN] 班级{ci}({self.class_names[ci]})-{mode_name}: {len(no_score)} 名学生无成绩")

    # ------------------------------------------------------------------
    # 查询接口
    # ------------------------------------------------------------------
    @property
    def current_students(self) -> List[StudentData]:
        """获取当前班级的学生列表"""
        if not self.students:
            return []
        return self.students[self.current_class][0]

    def get_zscores(self, class_idx: int, full_score: bool = False) -> list[list]:
        """获取指定班级的标准分数据

        Z = (原始分 - μ) / σ，缺考排除出统计。
        返回: [[name, [z1, z2, ...]], ...], 缺考为 None
        """
        import statistics
        students = self.students[class_idx][1 if full_score else 0]
        if not students or not self.dates:
            return []

        n_exams = len(self.dates)
        result = []

        # 收集原始分：用 date→score 字典，缺考记 None
        for s in students:
            arr = s.scores_full if full_score else s.scores
            score_by_date = {d: float(v) for d, v in arr} if arr else {}
            raw_list = []
            for dt in self.dates:
                if dt in score_by_date:
                    raw_list.append(score_by_date[dt])
                else:
                    raw_list.append(None)
            result.append([s.name, raw_list])

        # 对每次考试计算 Z
        for exam_i in range(n_exams):
            valid = [(ri, r[1][exam_i]) for ri, r in enumerate(result)
                     if r[1][exam_i] is not None]
            if len(valid) < 2:
                for r in result:
                    r[1][exam_i] = 0.0 if r[1][exam_i] is not None else None
                continue
            raw_vals = [v for _, v in valid]
            mean = statistics.mean(raw_vals)
            std = statistics.stdev(raw_vals)
            if std == 0:
                for r in result:
                    r[1][exam_i] = 0.0 if r[1][exam_i] is not None else None
            else:
                for ri, v in valid:
                    result[ri][1][exam_i] = round((v - mean) / std, 2)

        return result

    def is_quiz(self, date: str) -> bool:
        """纯客观题(仅有choice/multi_select) = quiz"""
        meta = self.exam_meta.get(date)
        if not meta or not meta.questions:
            return True
        return not any(q.qtype in ("fill", "answer") for q in meta.questions)

    # ------------------------------------------------------------------
    # 更新
    # ------------------------------------------------------------------
    def update_call_count(self, class_idx: int, student_id: int) -> int:
        """更新学生的 callCount，并写回 XML"""
        if class_idx < 0 or class_idx >= len(self.students):
            raise ValueError(f"班级索引越界: {class_idx}")

        # 更新该班级所有模式下的同一学生
        new_count = 0
        for mode_students in self.students[class_idx]:
            for s in mode_students:
                if s.id == student_id:
                    s.call_count += 1
                    new_count = s.call_count
                    break

        # 写回 XML
        xml_elems = list(ET.parse(self.config_path).getroot().findall("classMembers"))
        if class_idx < len(xml_elems) and xml_elems[class_idx].text:
            xml_path = self.data_dir / xml_elems[class_idx].text.strip()
            self._save_xml(xml_path, self.students[class_idx][0])

        return new_count

    def _save_xml(self, path: Path, students: List[StudentData]) -> None:
        """将学生数据写回 XML，保持可读格式"""
        root = ET.Element("root")
        for s in students:
            stu_elem = ET.SubElement(root, "student", {"id": str(s.id)})
            ET.SubElement(stu_elem, "name").text = s.name
            ET.SubElement(stu_elem, "callCount").text = str(s.call_count)

        self._indent_xml(root)
        tree = ET.ElementTree(root)
        tree.write(path, encoding="utf-8", xml_declaration=True)

    def _indent_xml(self, elem, level=0):
        """为 XML 元素添加缩进"""
        indent_str = "\n" + "  " * level
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent_str + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent_str
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = "\n" + "  " * level
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent_str

    # ------------------------------------------------------------------
    # 知识点池
    # ------------------------------------------------------------------
    DEFAULT_POOL: Dict[str, List[str]] = {
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
        "不等式": ["不等式性质", "一元二次不等式", "含绝对值不等式", "均值不等式", "线性规划"],
        "集合与逻辑": ["集合运算", "充分必要条件", "全称量词", "存在量词"],
    }

    def _init_knowledge(self) -> None:
        """初始化知识点池和考试元数据"""
        pool_path = self.data_dir / "knowledge_pool.xml"
        meta_path = self.data_dir / "exam_meta.xml"

        if pool_path.exists():
            self._load_knowledge_pool(pool_path)
        else:
            self.knowledge_pool = dict(self.DEFAULT_POOL)
            self.category_order = list(self.DEFAULT_POOL.keys())
            self._save_knowledge_pool(pool_path)

        if meta_path.exists():
            self._load_exam_meta(meta_path)
        else:
            self.exam_meta = {}

    def _load_knowledge_pool(self, path: Path) -> None:
        tree = ET.parse(path)
        self.knowledge_pool = {}
        self.category_order = []
        for cat in tree.findall("category"):
            name = cat.get("name", "")
            topics = [t.text.strip() for t in cat.findall("topic") if t.text]
            if name:
                self.knowledge_pool[name] = topics
                self.category_order.append(name)

    def _save_knowledge_pool(self, path: Path) -> None:
        root = ET.Element("pool")
        order = self.category_order if self.category_order else list(self.knowledge_pool.keys())
        for cat_name in order:
            if cat_name not in self.knowledge_pool:
                continue
            cat = ET.SubElement(root, "category", {"name": cat_name})
            for t in self.knowledge_pool[cat_name]:
                ET.SubElement(cat, "topic").text = t
        self._indent_xml(root)
        ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)

    def _load_exam_meta(self, path: Path) -> None:
        tree = ET.parse(path)
        self.exam_meta = {}
        for exam in tree.findall("exam"):
            dt = exam.get("date", "")
            if not dt:
                continue

            questions = []
            qnode = exam.find("questions")
            if qnode is not None:
                for q in qnode.findall("question"):
                    qid = q.get("id", "")
                    qtype = q.get("type", "choice")
                    max_score = float(q.get("max", "5.0"))
                    topics = []
                    for t in q.findall("topic"):
                        cat = t.get("category", "")
                        name = (t.text or "").strip()
                        weight = float(t.get("weight", "1.0"))
                        if cat and name:
                            topics.append(KnowledgeTopic(category=cat, name=name, weight=weight))
                    if qid:
                        questions.append(Question(id=qid, qtype=qtype, max_score=max_score, topics=topics))
            self.exam_meta[dt] = ExamMeta(date=dt, questions=questions)

    def _save_exam_meta(self) -> None:
        path = self.data_dir / "exam_meta.xml"
        root = ET.Element("exams")
        for dt, meta in self.exam_meta.items():
            exam = ET.SubElement(root, "exam", {"date": dt})

            # 只写 questions 节点
            if meta.questions:
                qnode = ET.SubElement(exam, "questions")
                for q in meta.questions:
                    qelem = ET.SubElement(qnode, "question",
                                          {"id": q.id, "type": q.qtype, "max": str(q.max_score)})
                    for kt in q.topics:
                        attrs = {"category": kt.category}
                        if kt.weight != 1.0:
                            attrs["weight"] = f"{kt.weight:.2f}"
                        ET.SubElement(qelem, "topic", attrs).text = kt.name
        self._indent_xml(root)
        ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)

    def get_exam_meta(self, date: str) -> ExamMeta:
        """获取某次考试的知识点元数据，不存在则返回空"""
        if date not in self.exam_meta:
            self.exam_meta[date] = ExamMeta(date=date)
        return self.exam_meta[date]

    def get_exam_questions(self, date: str) -> List[Question]:
        """获取某次考试的题目列表"""
        meta = self.get_exam_meta(date)
        return meta.questions

    def update_exam_questions(self, date: str, questions: List[Question]) -> None:
        """更新某次考试的题目列表并保存，保留已有的主客观知识点"""
        meta = self.get_exam_meta(date)
        meta.questions = questions
        self._save_exam_meta()

    def move_category(self, category: str, target_idx: int) -> None:
        """将分类移动到指定位置（拖拽用）"""
        if category not in self.category_order:
            return
        src_idx = self.category_order.index(category)
        if src_idx == target_idx:
            return
        if src_idx < target_idx:
            target_idx -= 1  # 移除自身后索引前移
        self.category_order.remove(category)
        self.category_order.insert(target_idx, category)
        self._save_knowledge_pool(self.data_dir / "knowledge_pool.xml")

    def add_knowledge(self, category: str, name: str) -> None:
        """添加新知识点到池并保存"""
        if category not in self.knowledge_pool:
            self.knowledge_pool[category] = []
            self.category_order.append(category)
        if name not in self.knowledge_pool[category]:
            self.knowledge_pool[category].append(name)
        self._save_knowledge_pool(self.data_dir / "knowledge_pool.xml")

    def rename_category(self, old: str, new: str) -> None:
        """重命名一级分类"""
        if old == new or old not in self.knowledge_pool:
            return
        self.knowledge_pool[new] = self.knowledge_pool.pop(old)
        if old in self.category_order:
            idx = self.category_order.index(old)
            self.category_order[idx] = new
        self._save_knowledge_pool(self.data_dir / "knowledge_pool.xml")

    def delete_category(self, category: str) -> None:
        """删除一级分类及其所有二级知识点"""
        if category not in self.knowledge_pool:
            return
        del self.knowledge_pool[category]
        if category in self.category_order:
            self.category_order.remove(category)
        self._save_knowledge_pool(self.data_dir / "knowledge_pool.xml")

    def rename_topic(self, category: str, old: str, new: str) -> None:
        """重命名二级知识点"""
        if category not in self.knowledge_pool or old == new:
            return
        topics = self.knowledge_pool[category]
        if old in topics:
            idx = topics.index(old)
            topics[idx] = new
        self._save_knowledge_pool(self.data_dir / "knowledge_pool.xml")

    def delete_topic(self, category: str, name: str) -> None:
        """删除二级知识点"""
        if category not in self.knowledge_pool:
            return
        topics = self.knowledge_pool[category]
        if name in topics:
            topics.remove(name)
        self._save_knowledge_pool(self.data_dir / "knowledge_pool.xml")
