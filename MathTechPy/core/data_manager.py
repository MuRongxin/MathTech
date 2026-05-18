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
import openpyxl

from .models import StudentData, ClassInfo


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
        self.use_full_score: bool = True  # 默认整卷分

        # 考试日期列表（从 Excel 表头读取）
        self.dates: List[str] = []

        self._load_all()
        self._initialized = True

    @property
    def class_count(self) -> int:
        return len(self.students)

    # ------------------------------------------------------------------
    # 加载
    # ------------------------------------------------------------------
    def _load_all(self) -> None:
        """加载所有数据"""
        config = ET.parse(self.config_path).getroot()
        xml_elems = [e for e in config.findall("classMembers") if e.text]
        xlsx_elems = [e for e in config.findall("classScore") if e.text]

        xml_files = [self.data_dir / e.text.strip() for e in xml_elems]
        xlsx_files = [self.data_dir / e.text.strip() for e in xlsx_elems]

        if len(xml_files) != len(xlsx_files):
            raise ValueError(
                f"config.xml 配置异常: classMembers={len(xml_files)}, "
                f"classScore={len(xlsx_files)}，数量必须相同"
            )

        if not xml_files:
            raise ValueError("config.xml 中未配置任何班级数据")

        # 解析班级名称
        self.class_names = []
        for e in xml_elems:
            fname = e.text.strip()
            m = re.search(r'[A-Za-z]*(\d+)', fname)
            if m:
                self.class_names.append(f"A{m.group(1).zfill(2)}")
            else:
                self.class_names.append(fname)

        # 加载每个班级的数据
        self.students = []
        for xml_path, xlsx_path in zip(xml_files, xlsx_files):
            class_data = self._load_class(xml_path, xlsx_path)
            self.students.append(class_data)

        self._validate()

    def _load_class(self, xml_path: Path, xlsx_path: Path) -> List[List[StudentData]]:
        """加载一个班级的数据
        
        返回: [客观分学生列表, 满分卷学生列表]
        """
        base_students = self._load_xml(xml_path)

        obj_students = [StudentData(s.id, s.name, s.call_count) for s in base_students]
        full_students = [StudentData(s.id, s.name, s.call_count) for s in base_students]

        dates = self._load_scores(xlsx_path, obj_students, full_students)
        if not self.dates:
            self.dates = dates

        return [obj_students, full_students]

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

    def _load_scores(self, path: Path, obj_students: List[StudentData],
                     full_students: List[StudentData]) -> List[str]:
        """读取 Excel 成绩"""
        wb = openpyxl.load_workbook(path, data_only=True)
        ws40 = wb["40"]
        dates = self._parse_sheet(ws40, obj_students, attr="scores")
        ws100 = wb["100"]
        self._parse_sheet(ws100, full_students, attr="scores_full")
        wb.close()
        return dates

    def _parse_sheet(self, ws, students: List[StudentData], attr: str) -> List[str]:
        """解析一个 sheet"""
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return []

        header = rows[0]
        dates = [str(h) for h in header[1:] if h is not None]

        name_map: Dict[str, StudentData] = {}
        for s in students:
            if s.name in name_map:
                print(f"[WARN] 重复姓名: {s.name} (id={s.id})")
            name_map[s.name] = s

        data_rows = rows[1:]
        matched = 0
        unmatched_names = []

        for row in data_rows:
            if not row or row[0] is None:
                continue
            name = str(row[0]).strip()
            stu = name_map.get(name)
            if stu is None:
                unmatched_names.append(name)
                continue

            score_list: List[List[str]] = []
            for i, date in enumerate(dates, start=1):
                val = row[i] if i < len(row) else None
                if val is None:
                    score_list.append([date, "0"])
                else:
                    try:
                        score_list.append([date, f"{float(val):.2f}"])
                    except (ValueError, TypeError):
                        score_list.append([date, "0"])

            setattr(stu, attr, score_list)
            matched += 1

        if unmatched_names:
            print(f"[WARN] {attr}: Excel 中 {len(unmatched_names)} 个学生未匹配")
        print(f"[INFO] {attr}: 成功匹配 {matched}/{len(students)} 名学生")

        return dates

    def _validate(self) -> None:
        """数据完整性校验"""
        for ci, class_data in enumerate(self.students):
            for mi, mode_name in [(0, "客观分"), (1, "满分卷")]:
                students = class_data[mi]
                no_score = [s.name for s in students if not s.scores and not s.scores_full]
                if no_score:
                    print(f"[WARN] 班级{ci}({self.class_names[ci]})-{mode_name}: {len(no_score)} 名学生无成绩")

    # ------------------------------------------------------------------
    # 查询接口
    # ------------------------------------------------------------------
    @property
    def current_students(self) -> List[StudentData]:
        """获取当前班级+当前模式的学生列表"""
        if not self.students:
            return []
        mode = 1 if self.use_full_score else 0
        return self.students[self.current_class][mode]

    def get_class_info(self, class_idx: int, full_score: bool = False) -> ClassInfo:
        """获取班级统计信息"""
        if class_idx < 0 or class_idx >= len(self.students):
            return ClassInfo(name="未知", count=0, avg_call=0.0, avg_score=0.0, avg_score_full=0.0)

        mode = 1 if full_score else 0
        students = self.students[class_idx][mode]
        count = len(students)
        if count == 0:
            return ClassInfo(name=self.class_names[class_idx], count=0,
                           avg_call=0.0, avg_score=0.0, avg_score_full=0.0)

        avg_call = sum(s.call_count for s in students) / count
        avg_score = sum(s.avg_score for s in students) / count
        avg_score_full = sum(s.avg_score_full for s in students) / count

        return ClassInfo(
            name=self.class_names[class_idx],
            count=count,
            avg_call=round(avg_call, 2),
            avg_score=round(avg_score, 2),
            avg_score_full=round(avg_score_full, 2)
        )

    def get_zscores(self, class_idx: int, full_score: bool = False) -> list[list]:
        """获取指定班级的标准分数据
        
        直接对原始分计算 Z = (原始分 - μ) / σ
        不受满分值影响，Z 分数对线性缩放不变。
        
        返回: 每个学生每次考试的标准分列表
              [[name, [z1, z2, ...]], ...]
        """
        import statistics
        mode = 1 if full_score else 0
        students = self.students[class_idx][mode]
        if not students or not self.dates:
            return []

        n_exams = len(self.dates)
        result = []

        # 收集原始分
        for s in students:
            arr = s.scores if s.scores else s.scores_full
            raw_list = []
            for i in range(n_exams):
                if i < len(arr):
                    try:
                        raw_list.append(float(arr[i][1]))
                    except:
                        raw_list.append(0.0)
                else:
                    raw_list.append(0.0)
            result.append([s.name, raw_list])

        # 对每次考试计算标准分 Z = (原始分 - μ) / σ
        for exam_i in range(n_exams):
            raw = [r[1][exam_i] for r in result]
            mean = statistics.mean(raw)
            std = statistics.stdev(raw) if len(raw) > 1 else 0
            for r in result:
                if std > 0:
                    r[1][exam_i] = round((r[1][exam_i] - mean) / std, 2)
                else:
                    r[1][exam_i] = 0.0

        return result

    def get_overview_data(self) -> dict:
        """获取概览页需要的所有数据"""
        def calc_averages(students: List[StudentData], full_marks: int) -> List[float]:
            if not students or not self.dates:
                return []
            avgs = []
            for i in range(len(self.dates)):
                vals = []
                for s in students:
                    arr = s.scores if s.scores else s.scores_full
                    if i < len(arr):
                        try:
                            vals.append(float(arr[i][1]) / full_marks)
                        except (ValueError, IndexError):
                            pass
                avgs.append(round(sum(vals) / len(vals), 2) if vals else 0.0)
            return avgs

        result = {
            "dates": self.dates,
            "classes": [],
        }

        for ci in range(self.class_count):
            info = self.get_class_info(ci)
            result["classes"].append({
                "name": info.name,
                "count": info.count,
                "avg_call": info.avg_call,
                "averages": calc_averages(self.students[ci][0], 40),
                "averages_full": calc_averages(self.students[ci][1], 100),
            })

        return result

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
