using Microsoft.AspNetCore.Mvc;
using AuxiliaryTool.Web.Models;
using System.Linq;
using System;
using System.Collections.Generic;

namespace AuxiliaryTool.Web.Controllers
{
    [ApiController]
    [Route("api")]
    public class ApiController : ControllerBase
    {
        private readonly Random _random = new Random();
        private readonly List<StudentData> _randomHistory_1 = new List<StudentData>();
        private readonly List<StudentData> _randomHistory_2 = new List<StudentData>();

        [HttpGet("overview")]
        public IActionResult GetOverview()
        {
            var a1 = AuxiliaryMethods.Instance.studentDatas_1;
            var a2 = AuxiliaryMethods.Instance.studentDatas_2;

            double avg1 = 0, avg2 = 0;
            List<string> dates = new List<string>();

            if (a1.Count > 0 && a1[0].scoreArr.Count > 0)
            {
                var scores = a1.SelectMany(s => s.scoreArr.Select(a => double.Parse(a[1])));
                avg1 = scores.Average();
                dates = a1[0].scoreArr.Select(a => a[0]).ToList();
            }

            if (a2.Count > 0 && a2[0].scoreArr.Count > 0)
            {
                var scores = a2.SelectMany(s => s.scoreArr.Select(a => double.Parse(a[1])));
                avg2 = scores.Average();
            }

            // 计算每个日期的班级平均分（用于看板下方图表）
            List<double> averages1 = new List<double>();
            List<double> averages2 = new List<double>();
            if (a1.Count > 0 && dates.Count > 0)
            {
                for (int d = 0; d < dates.Count; d++)
                {
                    double sum1 = 0, sum2 = 0;
                    int c1 = 0, c2 = 0;
                    foreach (var s in a1)
                        if (d < s.scoreArr.Count && double.TryParse(s.scoreArr[d][1], out double v1)) { sum1 += v1; c1++; }
                    foreach (var s in a2)
                        if (d < s.scoreArr.Count && double.TryParse(s.scoreArr[d][1], out double v2)) { sum2 += v2; c2++; }
                    averages1.Add(c1 > 0 ? Math.Round(sum1 / c1, 2) : 0);
                    averages2.Add(c2 > 0 ? Math.Round(sum2 / c2, 2) : 0);
                }
            }

            return Ok(new
            {
                a01 = new { count = a1.Count, avg = Math.Round(avg1, 2) },
                a02 = new { count = a2.Count, avg = Math.Round(avg2, 2) },
                dates = dates,
                averages1 = averages1,
                averages2 = averages2
            });
        }

        [HttpGet("class/{id}")]
        public IActionResult GetClass(int id)
        {
            var list = id == 1
                ? AuxiliaryMethods.Instance.studentDatas_1
                : AuxiliaryMethods.Instance.studentDatas_2;

            return Ok(list.Select(s => new
            {
                id = s.ID,
                name = s.Name,
                callCount = s.CallCount,
                scoreCount = s.scoreArr.Count
            }));
        }

        [HttpPost("random/{classId}")]
        public IActionResult RandomStudent(int classId)
        {
            var list = classId == 1
                ? AuxiliaryMethods.Instance.studentDatas_1
                : AuxiliaryMethods.Instance.studentDatas_2;

            if (list.Count == 0) return BadRequest("No students");

            var history = classId == 1 ? _randomHistory_1 : _randomHistory_2;
            StudentData selected;

            if (history.Count >= list.Count) history.Clear();

            while (true)
            {
                int idx = _random.Next(list.Count);
                var stu = list[idx];
                if (!history.Contains(stu))
                {
                    selected = stu;
                    history.Add(stu);
                    break;
                }
            }

            // Update callCount in XML
            var xmlPath = classId == 1
                ? AuxiliaryMethods.Instance.classFilePath_1
                : AuxiliaryMethods.Instance.classFilePath_2;

            AuxiliaryMethods.Instance.UpdateXmlData(xmlPath, selected.ID, selected.CallCount + 1);
            selected.CallCount++;

            return Ok(new
            {
                id = selected.ID,
                name = selected.Name,
                callCount = selected.CallCount
            });
        }

        [HttpGet("scores/{classId}")]
        public IActionResult GetScores(int classId, [FromQuery] bool fullScore = false)
        {
            var list = fullScore
                ? (classId == 1 ? AuxiliaryMethods.Instance.studentDatas_1_2 : AuxiliaryMethods.Instance.studentDatas_2_2)
                : (classId == 1 ? AuxiliaryMethods.Instance.studentDatas_1 : AuxiliaryMethods.Instance.studentDatas_2);

            if (list.Count == 0 || list[0].scoreArr.Count == 0)
                return Ok(new { dates = new List<string>(), students = new List<object>() });

            var dates = list[0].scoreArr.Select(a => a[0]).ToList();

            var students = list.Select(s => new
            {
                name = s.Name,
                scores = s.scoreArr.Select(a => double.Parse(a[1])).ToList()
            });

            return Ok(new { dates, students });
        }

        [HttpGet("scores/{classId}/dates")]
        public IActionResult GetScoreDates(int classId)
        {
            var list = classId == 1
                ? AuxiliaryMethods.Instance.studentDatas_1
                : AuxiliaryMethods.Instance.studentDatas_2;

            if (list.Count == 0 || list[0].scoreArr.Count == 0)
                return Ok(new List<string>());

            return Ok(list[0].scoreArr.Select(a => a[0]).ToList());
        }
    }
}
