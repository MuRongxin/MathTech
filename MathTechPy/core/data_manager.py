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
import math
import os
import pickle
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

        # 各班级名册 XML 的实际路径（_load_all 时缓存，避免每次解析 config.xml）
        self._class_xml_paths: List[Path] = []

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
        # 非初始化类加载错误（供 UI 显示），None 表示加载正常
        self._load_error: Optional[str] = None
        try:
            self._load_all()
        except FileNotFoundError as e:
            # 仅 config.xml 缺失才视为首次启动；班级 XML 缺失属于数据错误
            if e.filename and Path(e.filename) == self.config_path:
                print(f"[INFO] 配置缺失，需要初始化: {e}")
                self._needs_init = True
            else:
                self._load_error = f"数据文件缺失: {e}"
                print(f"[ERROR] {self._load_error}")
            self._init_knowledge()
            self._initialized = True
            return
        except (ET.ParseError, ValueError) as e:
            # 配置损坏/格式错误不是"需要初始化"，记录后交由 UI 提示
            self._load_error = f"{type(e).__name__}: {e}"
            print(f"[ERROR] 数据加载失败（非初始化问题）: {self._load_error}")
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
    # 公开生命周期接口（供 main_window 等调用，替代直接访问私有成员）
    # ------------------------------------------------------------------
    def reload(self) -> None:
        """重新加载全部数据（名册 + 逐题分 + 校验）"""
        self._load_all()
        self._load_question_scores()
        self._validate()

    def mark_initialized(self) -> None:
        """标记初始化完成（初始化向导结束后调用）"""
        self._initialized = True
        self._needs_init = False

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
        # 缓存各班级名册路径，供 update_call_counts / class_xml_path 使用
        self._class_xml_paths = xml_files

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
        """扫描 question_scores/ 目录，加载逐题分并更新总分

        解析结果按文件 mtime 缓存到 data/.question_scores_cache.pkl，
        启动时仅对新增/修改过的文件重新解析。
        """
        if not self._question_score_dir or not self._question_score_dir.exists():
            return

        # 按班级分组所有学生 {class_idx: {name: (obj_stu, full_stu, sub_stu)}}
        class_maps = []
        for ci in range(self.class_count):
            names = [s.name for s in self.students[ci][0]]
            dups = sorted({n for n in names if names.count(n) > 1})
            if dups:
                print(f"[WARN] 班级 {self.class_names[ci]} 存在重名学生 {dups}，"
                      f"逐题分将同时匹配所有同名者")
            obj_map = {s.name: s for s in self.students[ci][0]}
            full_map = {s.name: s for s in self.students[ci][1]}
            sub_map = {s.name: s for s in self.students[ci][2]}
            class_maps.append((obj_map, full_map, sub_map))

        # 已知班级后缀
        class_suffixes = [cn.replace("A", "") for cn in self.class_names]

        # 逐题分解析缓存：{文件路径: (mtime, 解析结果)}
        cache_path = self.data_dir / ".question_scores_cache.pkl"
        cache = self._load_qs_cache(cache_path)
        new_cache = {}

        imported_dates: set[str] = set()
        unknown_class: Dict[str, int] = {}   # 未配置班级后缀 → 文件数
        seen_dates: Dict[tuple, str] = {}    # (class_idx, date) → etype
        meta_snapshot = self._exam_meta_snapshot()
        fname_re = re.compile(r'^(quiz|exam)_(\d{4})_(\d{2})_(\d{2})_(.+)$')

        for fpath in sorted(self._question_score_dir.glob("*")):
            if fpath.suffix.lower() not in (".csv", ".xlsx"):
                continue
            # 解析文件名: quiz_2025_09_01_A01.csv 或 exam_2025_09_07_A01.xlsx
            m = fname_re.match(fpath.stem)
            if not m:
                print(f"[WARN] 逐题分文件名格式不符"
                      f"（应为 quiz|exam_YYYY_MM_DD_班级），已跳过: {fpath.name}")
                continue
            etype = m.group(1)                                    # quiz or exam
            date_str = f"{m.group(2)}/{m.group(3)}/{m.group(4)}"  # 2025/09/01
            class_suffix = m.group(5).replace("A", "")            # 01, 02, 03

            # 匹配班级索引
            try:
                class_idx = class_suffixes.index(class_suffix)
            except ValueError:
                unknown_class[m.group(5)] = unknown_class.get(m.group(5), 0) + 1
                continue

            # 同一班级同一日期同时存在 quiz_ 与 exam_ 文件时后者覆盖前者
            date_key = (class_idx, date_str)
            if date_key in seen_dates and seen_dates[date_key] != etype:
                print(f"[WARN] 班级 {self.class_names[class_idx]} {date_str} 同时存在 "
                      f"{seen_dates[date_key]} 与 {etype} 文件，后者成绩将覆盖前者")
            seen_dates[date_key] = etype

            # mtime 未变 → 直接用缓存的解析结果，否则重新解析
            try:
                mtime = fpath.stat().st_mtime
            except OSError as e:
                print(f"[WARN] 无法读取 {fpath.name}: {e}")
                continue
            cached = cache.get(str(fpath))
            if (cached and isinstance(cached, (tuple, list)) and len(cached) == 2
                    and cached[0] == mtime):
                q_rows, obj_total_col, sub_total_col, full_total_col = cached[1]
            else:
                print(f"[INFO] 解析逐题分: {fpath.name} → 日期={date_str}, "
                      f"班级={m.group(5)}, 类型={etype}")
                try:
                    if fpath.suffix.lower() == ".csv":
                        result = self._parse_question_csv(fpath)
                    else:
                        result = self._parse_question_xlsx(fpath)
                except Exception as e:
                    print(f"[WARN] 无法解析 {fpath.name}: {e}")
                    continue
                q_rows, obj_total_col, sub_total_col, full_total_col = result
            new_cache[str(fpath)] = (mtime,
                                     (q_rows, obj_total_col, sub_total_col, full_total_col))

            obj_map, full_map, sub_map = class_maps[class_idx]

            # 为每个学生分配逐题分并更新总分
            matched = 0
            for name, row_data in q_rows.items():
                q_scores = row_data["questions"]
                stu_obj = obj_map.get(name)
                stu_full = full_map.get(name)
                stu_sub = sub_map.get(name)

                # 三个模式副本有意共享同一 q_scores dict：
                # UI 对逐题分只读，共享可避免三倍内存开销
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

                # 兜底：缺总分列时从逐题分自动加总。
                # 该行存在逐题数据即视为参考，即使总和为 0 也记录（区分"无数据"与"0 分"）
                has_obj = obj_total_col and row_data["obj_total"] is not None
                has_full = full_total_col and row_data["full_total"] is not None
                has_sub = sub_total_col and row_data["sub_total"] is not None
                q_sum = sum(q_scores.values())
                if (not has_obj or not has_full or not has_sub) and q_scores:
                    # 尝试从 exam_meta 分题型
                    meta = self.exam_meta.get(date_str)
                    obj_qids = set()
                    if meta and meta.questions:
                        for q in meta.questions:
                            if q.qtype in ("choice", "multi_select"):
                                obj_qids.add(q.id)
                    if obj_qids:
                        obj_sum = sum(q_scores.get(qid, 0.0) for qid in obj_qids)
                        sub_sum = sum(q_scores.get(qid, 0.0) for qid in q_scores
                                      if qid not in obj_qids)
                    else:
                        obj_sum = q_sum
                        sub_sum = 0.0
                    if not has_obj and stu_obj:
                        self._upsert_score(stu_obj.scores, date_str, f"{obj_sum:.2f}")
                    if not has_full and stu_full:
                        self._upsert_score(stu_full.scores_full, date_str, f"{q_sum:.2f}")
                    if not has_sub and stu_sub:
                        if has_full and has_obj:
                            sub_val = max(0.0, (row_data["full_total"] or 0)
                                          - (row_data["obj_total"] or 0))
                        else:
                            sub_val = sub_sum
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

        if unknown_class:
            summary = ", ".join(f"{k}({v}个)" for k, v in sorted(unknown_class.items()))
            print(f"[WARN] {sum(unknown_class.values())} 个逐题分文件属于未配置班级，"
                  f"已跳过: {summary}")

        # 仅在 exam_meta 内容实际变化时写回
        if imported_dates and self._exam_meta_snapshot() != meta_snapshot:
            self._save_exam_meta()

        self._save_qs_cache(cache_path, new_cache)

    @staticmethod
    def _load_qs_cache(cache_path: Path) -> dict:
        """读取逐题分解析缓存，损坏或不存在时返回空"""
        try:
            with open(cache_path, "rb") as f:
                data = pickle.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
        return {}

    @staticmethod
    def _save_qs_cache(cache_path: Path, cache: dict) -> None:
        """原子写回逐题分解析缓存，失败仅告警（下次启动重解析）"""
        try:
            tmp = cache_path.with_suffix(cache_path.suffix + ".tmp")
            with open(tmp, "wb") as f:
                pickle.dump(cache, f)
            os.replace(tmp, cache_path)
        except Exception as e:
            print(f"[WARN] 逐题分缓存写入失败: {e}")

    def _exam_meta_snapshot(self) -> list:
        """考试元数据的轻量指纹，用于判断内容是否实际变化"""
        return [
            (dt, [(q.id, q.qtype, q.max_score,
                   [(t.category, t.name, t.weight) for t in q.topics])
                  for q in meta.questions])
            for dt, meta in sorted(self.exam_meta.items())
        ]

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

        返回: (q_rows, obj_col_exists, sub_col_has_data, full_col_has_data)
          q_rows = {student_name: {"questions": {qid: score}, "obj_total": float|None, ...}}
          后三项表示对应总分列是否存在且至少一行有数据
        """
        import csv
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                all_rows = list(csv.reader(f))
        except UnicodeDecodeError:
            print(f"[WARN] {path.name}: UTF-8 解码失败，改用 GBK 编码重试")
            with open(path, "r", encoding="gbk") as f:
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

        # 姓名列按表头查找，找不到时回退为第 2 列
        name_idx = next((i for i, h in enumerate(headers)
                         if h in ("姓名", "student_name")), 1)

        q_rows = {}
        bad_cells = 0
        for row in all_rows[header_row_idx + 1:]:
            if not row or len(row) < 2:
                continue
            name = row[name_idx].strip() if len(row) > name_idx else ""
            if not name:
                continue

            q_scores = {}
            for idx, qid in q_cols:
                if idx < len(row) and row[idx]:
                    try:
                        q_scores[qid] = float(row[idx])
                    except ValueError:
                        q_scores[qid] = 0.0
                        bad_cells += 1

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

            if name in q_rows:
                print(f"[WARN] {path.name}: 重名学生行 \"{name}\"，后者覆盖前者")
            q_rows[name] = {
                "questions": q_scores,
                "obj_total": obj_total,
                "sub_total": sub_total,
                "full_total": full_total,
            }

        if bad_cells:
            print(f"[WARN] {path.name}: {bad_cells} 个单元格无法解析为数字，已记 0")

        # 检查主观/全卷总分列是否有数据（全量扫描所有行）
        has_sub = any(r.get("sub_total") is not None for r in q_rows.values())
        has_full = any(r.get("full_total") is not None for r in q_rows.values())
        return q_rows, obj_total_idx is not None, sub_total_idx is not None and has_sub, full_total_idx is not None and has_full

    def _parse_question_xlsx(self, path: Path) -> tuple:
        """解析逐题分 Excel（与 CSV 同格式：考号,姓名,Q1...Qn,客观总分,主观总分,全卷总分,客观错题题号）

        返回语义同 _parse_question_csv。
        """
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True)
        try:
            ws = wb.active
            rows = list(ws.iter_rows(values_only=True))
            if not rows:
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

            # 姓名列按表头查找，找不到时回退为第 2 列
            name_idx = next((i for i, h in enumerate(header)
                             if h in ("姓名", "student_name")), 1)

            q_rows = {}
            for row in rows[header_row_idx + 1:]:
                if not row or len(row) < 2:
                    continue
                name = str(row[name_idx]).strip() if len(row) > name_idx else ""
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

                if name in q_rows:
                    print(f"[WARN] {path.name}: 重名学生行 \"{name}\"，后者覆盖前者")
                q_rows[name] = {
                    "questions": q_scores,
                    "obj_total": _get(obj_total_idx),
                    "sub_total": _get(sub_total_idx),
                    "full_total": _get(full_total_idx),
                }

            # 检查主观/全卷总分列是否有数据（全量扫描所有行）
            has_sub = any(r.get("sub_total") is not None for r in q_rows.values())
            has_full = any(r.get("full_total") is not None for r in q_rows.values())
            return q_rows, obj_total_idx is not None, sub_total_idx is not None and has_sub, full_total_idx is not None and has_full
        finally:
            wb.close()

    # 新高考 19 题固定结构: Q1-8单选(5') Q9-11多选(6') Q12-14填空(5') Q15-19解答(13-17')
    _EXAM19_STRUCTURE: Dict[int, tuple] = {
        **{i: ("choice", 5.0) for i in range(1, 9)},
        **{i: ("multi_select", 6.0) for i in range(9, 12)},
        **{i: ("fill", 5.0) for i in range(12, 15)},
        15: ("answer", 13.0), 16: ("answer", 15.0), 17: ("answer", 15.0),
        18: ("answer", 17.0), 19: ("answer", 17.0),
    }

    def _detect_questions(self, all_qscores: List[dict], etype: str = "quiz") -> List:
        """从全班逐题分推断题目结构（结合考试类型和得分分布）

        exam 仅在观测题数恰为 19 且各题 max_seen 与固定结构吻合时才套用
        新高考结构；其余情况一律按观测数据推断，并提示人工核对。
        """
        from .models import Question as QModel
        # 按题号收集所有学生的得分
        qid_scores: Dict[str, List[float]] = {}
        for qs in all_qscores:
            for qid, score in qs.items():
                qid_scores.setdefault(qid, []).append(score)

        def _qnum(qid: str) -> int:
            m = re.search(r"\d+", qid)
            return int(m.group(0)) if m else 0

        # 判断观测数据是否吻合 19 题固定结构：
        # 题号恰为 1-19，且各题观测最高分落在 [假设满分/2, 假设满分] 区间
        use_fixed = (
            etype == "exam"
            and len(qid_scores) == 19
            and sorted(_qnum(q) for q in qid_scores) == list(range(1, 20))
            and all(
                self._EXAM19_STRUCTURE[_qnum(qid)][1] / 2
                <= max(scores)
                <= self._EXAM19_STRUCTURE[_qnum(qid)][1]
                for qid, scores in qid_scores.items() if scores
            )
        )

        questions = []
        for qid in sorted(qid_scores.keys(), key=lambda x: (_qnum(x), x)):
            scores = qid_scores[qid]
            max_seen = max(scores) if scores else 5.0
            unique_vals = set(scores)

            if use_fixed:
                qtype, max_score = self._EXAM19_STRUCTURE[_qnum(qid)]
            else:
                # 按观测数据推断：满分取不小于观测最大值的整数（ceil 避免
                # round 低估，如观测 7.2 被归为 7）；无人满分时仍可能低估
                max_score = float(max(1, math.ceil(max_seen))) if max_seen > 0 else 5.0
                # 是否存在 0 与满分之外的中间分 → 判定多选
                has_mid = any(v not in (0.0, max_seen) for v in unique_vals)
                if max_score == 6 and has_mid:
                    qtype = "multi_select"
                elif etype == "quiz":
                    qtype = "choice"          # 测验默认选择题
                elif max_score > 10:
                    qtype = "answer"
                else:
                    qtype = "fill"

            questions.append(QModel(id=qid, qtype=qtype, max_score=max_score))

        if not use_fixed:
            print(f"[WARN] {etype} 题目结构按观测数据推断（共 {len(questions)} 题），"
                  f"满分/题型可能不准确（无人满分时会低估），请到数据维护页核对")
        return questions

    def _load_xml(self, path: Path) -> List[StudentData]:
        """读取班级 XML（单个学生脏数据跳过并告警，不中止整班加载）"""
        tree = ET.parse(path)
        students: List[StudentData] = []
        for elem in tree.findall("student"):
            try:
                sid = int(elem.get("id", 0))
                call = int(elem.findtext("callCount", "0"))
            except ValueError:
                print(f"[WARN] {path.name}: 跳过脏数据学生 "
                      f"(id={elem.get('id')!r}, callCount={elem.findtext('callCount')!r})")
                continue
            name = elem.findtext("name", "").strip()
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
    def update_call_counts(self, class_idx: int, student_ids: List[int]) -> None:
        """批量更新学生的 callCount：内存更新后一次性原子写回该班 XML"""
        if class_idx < 0 or class_idx >= len(self.students):
            raise ValueError(f"班级索引越界: {class_idx}")

        ids = set(student_ids)
        # 更新该班级所有模式下的同一批学生
        for mode_students in self.students[class_idx]:
            for s in mode_students:
                if s.id in ids:
                    s.call_count += 1

        # 一次性写回 XML（路径来自 _load_all 时的缓存，不再重复解析 config）
        if class_idx < len(self._class_xml_paths):
            self._save_xml(self._class_xml_paths[class_idx], self.students[class_idx][0])

    def update_call_count(self, class_idx: int, student_id: int) -> int:
        """更新单个学生的 callCount（兼容接口，委托批量方法）"""
        self.update_call_counts(class_idx, [student_id])
        for s in self.students[class_idx][0]:
            if s.id == student_id:
                return s.call_count
        return 0

    def class_xml_path(self, class_idx: int) -> Path:
        """返回该班名册 XML 的实际路径（来自 config.xml 缓存）"""
        if class_idx < 0 or class_idx >= len(self._class_xml_paths):
            raise ValueError(f"班级索引越界: {class_idx}")
        return self._class_xml_paths[class_idx]

    @staticmethod
    def _atomic_write(tree: ET.ElementTree, path: Path) -> None:
        """原子写 XML：先写临时文件再 os.replace，避免写入中断损坏数据"""
        tmp = path.with_suffix(path.suffix + ".tmp")
        tree.write(tmp, encoding="utf-8", xml_declaration=True)
        os.replace(tmp, path)

    def _save_xml(self, path: Path, students: List[StudentData]) -> None:
        """将学生数据写回 XML，保持可读格式"""
        root = ET.Element("root")
        for s in students:
            stu_elem = ET.SubElement(root, "student", {"id": str(s.id)})
            ET.SubElement(stu_elem, "name").text = s.name
            ET.SubElement(stu_elem, "callCount").text = str(s.call_count)

        self._indent_xml(root)
        tree = ET.ElementTree(root)
        self._atomic_write(tree, path)

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
        self._atomic_write(ET.ElementTree(root), path)

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
        self._atomic_write(ET.ElementTree(root), path)

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
        """更新某次考试的题目列表并保存（整体替换，调用方需自带知识点）"""
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
