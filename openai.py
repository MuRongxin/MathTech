import pandas as pd
import datetime

class Course:
    def __init__(self, name, teacher, class_name, day, period, num_periods):
        self.name = name
        self.teacher = teacher
        self.class_name = class_name
        self.day = day
        self.period = period
        self.num_periods = num_periods

class Schedule:
    def __init__(self, start_date, end_date, interval=1):
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.courses = []
        self.schedule = None

    def read_course_data(self, file_name):
        """
        从特定格式的txt文件中读取课程数据
        """
        with open(file_name, 'r') as f:
            for line in f:
                course_data = line.strip().split(',')
                name, teacher, class_name, day_period, day_periods, night_periods = course_data
                day, period = day_period.split(' ')
                period = int(period)
                day_periods = int(day_periods)
                night_periods = int(night_periods)
                num_periods = day_periods + night_periods
                course = Course(name, teacher, class_name, day, period, num_periods)
                self.courses.append(course)

    def generate_schedule(self):
        """
        根据课程数据生成完整的课程表
        """
        dates = pd.date_range(start=self.start_date, end=self.end_date, freq='D')
        self.schedule = pd.DataFrame(index=self.days, columns=range(1, 14))
        for course in self.courses:
            days = dates[dates.day_name() == course.day]
            periods = [course.period + i for i in range(course.num_periods)]
            periods = [p for p in periods if p <= 13] # 排除课程结束时间超过13节课的情况
            for day in days:
                self.schedule.loc[day.day_name(), periods] = course.name + '\n' + course.teacher


# kry="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"