#!/usr/bin/env python
## TODO: Is the data format good enough? Should we replace it or is it enough ?
import os
import re
import argparse
from datetime import datetime as dt
from datetime import timedelta
from datetime import time

class WorkLog():
    """
    Example worklog:
        #WL#WORKID:JIRA-000001#START:09.30#END:09.39#WL
        Daily meeting
    """
    _TIME_FORMAT = "%H.%M"
    ##                ^#WL#WORKID:        JIRA-000000   #START:                09       .                   10      #END:              09       .                 30      #WL(newline)         did work(until not including newline + #WL)
    WORKLOG_REGEX = r"^#WL#WORKID:(?P<id>[A-Za-z0-9_-]+)#START:(?P<start_hour>[0-9]{2})\.(?P<start_minutes>[0-9]{2})#END:(?P<end_hour>[0-9]{2})\.(?P<end_minutes>[0-9]{2})#WL(\n)?(?P<comment>[\s\S]*?)(?=\n?^#WL|\Z)"
    def __init__(self,
            workid="NO_ID",
            start=dt.now().time(),
            end=dt.now().time(),
            comment: str | None = None
            ):
        self.start_time = start
        self.end_time = end
        self.workid = workid
        self.comment = comment
    def __str__(self) -> str:
        start = self.start_time.strftime(self._TIME_FORMAT)
        end = self.end_time.strftime(self._TIME_FORMAT)
        if self.comment is not None and self.comment != "":
            return f"#WL#WORKID:{self.workid}#START:{start}#END:{end}#WL" + "\n" + self.comment + "\n"
        else:
            return f"#WL#WORKID:{self.workid}#START:{start}#END:{end}#WL" + "\n"

    def pretty(self) -> str:
        wl = ""
        wl += "#WL# "
        id = self.workid
        if id == "NO_ID":
            id = "Break"
        wl += id + "\t"
        wl += f"{self.start_time.strftime(WorkLog._TIME_FORMAT)} - {self.end_time.strftime(WorkLog._TIME_FORMAT)} "
        wl += f"= {self.duration().total_seconds() / 60} minutes"
        if self.comment is not None and self.comment != "":
            wl += "\n" + self.comment
        return wl

    def duration(self) -> timedelta:
        start = timedelta(hours=self.start_time.hour, minutes=self.start_time.minute)
        end = timedelta(hours=self.end_time.hour, minutes=self.end_time.minute)
        return end - start

class WorkPage():
    """
    Example workpage .worklog/2025.25/06.27:
        #WL#WORKID:BRP-000001#START:09.30#END:09.30#WL
        #WL#WORKID:BRP-000001#START:09.30#END:09.39#WL
        Daily meeting
        #WL#WORKID:BRP-000000#START:09.39#END:17.00#WL
        did work all day
    """
    def __init__(self, day=dt.now().date()):
        self.day = day
        self._PAGE_DIR = os.environ["HOME"] + "/.worklog/" + day.strftime("%Y.%W")
        self.page = self._PAGE_DIR + day.strftime('/%m.%d')
        self.worklogs: list[WorkLog] = [] 
        os.makedirs(self._PAGE_DIR, mode=0o755, exist_ok=True)
        if not os.path.exists(self.page) or os.path.getsize(self.page) <= 0:
            self.add_wl(WorkLog())
        else:
            # Parse the page.
            wl_regex = re.compile(WorkLog.WORKLOG_REGEX, re.MULTILINE)
            with open(self.page, 'r') as page:
                page_content = page.read()
                for match in wl_regex.finditer(page_content):
                    id = match.group("id")
                    start = time(int(match.group("start_hour")), int(match.group("start_minutes")))
                    end = time(int(match.group("end_hour")), int(match.group("end_minutes")))
                    comment = match.group("comment")
                    wl = WorkLog(id, start, end, comment)
                    self.worklogs.append(wl)

    def calc_duration_day(self) -> tuple[float, float, float]:
        """
            Returns: (total_time, work_time, break_time)
        """
        total_time = timedelta()
        work_time = timedelta()
        break_time = timedelta()
        for wl in self.worklogs:
            if wl.workid == "NO_ID":
                break_time += wl.duration()
            else:
                work_time += wl.duration()
            total_time += wl.duration()
        return (total_time.total_seconds() / 60, work_time.total_seconds() / 60, break_time.total_seconds() / 60)

    def calc_duration_issue(self, id=None) -> float:
        duration = timedelta()
        if id == "Break" or id == "break":
            id = "NO_ID"
        for wl in self.worklogs:
            if id == wl.workid:
                duration += wl.duration()
        return duration.total_seconds() / 60

    def add_break(self, comment: str):
        start = self.worklogs[-1].end_time
        wl = WorkLog(start=start,comment=comment)
        self.add_wl(wl)
        return

    def add_work(self, work_id: str, comment: str):
        start = self.worklogs[-1].end_time
        wl = WorkLog(start=start, workid=work_id, comment=comment)
        self.add_wl(wl)
        return

    def add_wl(self, worklog: WorkLog):
        self.worklogs.append(worklog)
        with open(self.page, 'a') as page:
            page.write(str(worklog))

    def edit(self):
        editor = os.environ['EDITOR']
        if editor is None or len(editor) <= 0:
            editor = "nvim"
        os.system(f"{editor} {self.page}")
        return

    def show(self, id: str|None =None):
        print(f"#WL# Date: {self.day.strftime('%x')}")
        if id == "break" or id == "Break":
            id = "NO_ID"
        for wl in self.worklogs:
            if id is None or id == wl.workid:
                print(wl.pretty())

def main(args):
    wp = None
    if args.previous is not None or args.previous != 0:
        prev = float(args.previous)
        date = (dt.now() - timedelta(days=prev)).date()
        wp = WorkPage(date)
    else:
        wp = WorkPage()
    if args.command_name in ["break", "b"]:
        wp.add_break("\n".join(args.message))
    elif args.command_name in ["work", "w"]:
        wp.add_work(args.id, "\n".join(args.message))
    elif args.command_name in ["calculate", "calc", "c"]:
        if args.id is not None and args.id != '':
            issue_dur = wp.calc_duration_issue(id=args.id)
            print(f"Total time for {args.id} is {issue_dur} minutes")
        else:
            total_dur, work_dur, break_dur = wp.calc_duration_day()
            if not args.breakoff and not args.total:
                args.work = True
            if args.breakoff or args.all:
                print(f"Total break time is {break_dur} minutes")
            if args.work or args.all:
                print(f"Total work  time is {work_dur} minutes")
            if args.total or args.all:
                print(f"Total spent time is {total_dur} minutes")
    elif args.command_name in ["edit", "e"]:
        wp.edit()
    elif args.command_name in ["show", "s"]:
        wp.show(args.id)
    else:
        print("Arguments not understood")
        return 1
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record and calculate worklogs locally", allow_abbrev=True)
    parser.add_argument("--previous", "-p", action="store", metavar="DAY", default=0, help="Show a previous day")
    sub_parsers = parser.add_subparsers(dest="command_name")

    break_parser = sub_parsers.add_parser("break", aliases=["b"])
    break_parser.add_argument("--message", "-m", action="append", metavar="MESSAGE", help="You can use '-m MESSAGE' more than once", default=[])
    work_parser = sub_parsers.add_parser("work", aliases=["w"])
    work_parser.add_argument("id", action="store", metavar="ID")
    work_parser.add_argument("--message", "-m", action="append", metavar="MESSAGE", help="You can use '-m MESSAGE' more than once", default=[])
    calculate_parser = sub_parsers.add_parser("calculate", aliases=["calc", "c"])
    calculate_parser.add_argument("--break", "-b", action="store_true", default=False, dest="breakoff")
    calculate_parser.add_argument("--total", "-t", action="store_true", default=False)
    calculate_parser.add_argument("--work",  "-w", action="store_true", default=False, help="Default type if none given")
    calculate_parser.add_argument("--all",   "-a", action="store_true", default=False, help="Calculate all types")
    calculate_parser.add_argument("--id",    "-i", action="store",      metavar="ID", help="Calculate the given id")
    edit_parser = sub_parsers.add_parser("edit", aliases=["e"])
    show_parser = sub_parsers.add_parser("show", aliases=["s"])
    show_parser.add_argument("--id", "-i", action="store", metavar="ID", help="Show only the given id")

    args = parser.parse_args()
    main(args)

