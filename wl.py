#!/usr/bin/env python
## TODO: add -i <WORKID> to s command
## TODO: integrate with kitty to open the issue in the browser easily (?)
## TODO: Is the data format good enough? Should we replace it or is it enough ?
## TODO: Simplify aliases? e.g. simplify assigning JIRA-000000 for misc stuff, JIRA-000000 for dailies etc.
import os
import re
import argparse
from datetime import datetime as dt
from datetime import timedelta
from datetime import time

class WorkLog():
    _TIME_FORMAT = "%H.%M"
    def __init__(self, 
            workid="NO_ID", 
            start=dt.now().time(), 
            end=dt.now().time(), 
            ):
        self.start_time = start
        self.end_time = end
        self.workid = workid
    def __str__(self) -> str:
        start = self.start_time.strftime(self._TIME_FORMAT)
        end = self.end_time.strftime(self._TIME_FORMAT)
        return  "#WL" + \
                f"#WORKID:{self.workid}" + \
                f"#START:{start}" + \
                f"#END:{end}" + \
                "#WL"
    def duration(self) -> timedelta:
        start = timedelta(hours=self.start_time.hour, minutes=self.start_time.minute)
        end = timedelta(hours=self.end_time.hour, minutes=self.end_time.minute)
        return end - start

    @staticmethod
    def from_str(header_data: str):
        start = re.search("#START:(.*?)#", header_data).group(1)
        end = re.search("#END:(.*?)#", header_data).group(1)
        workid = re.search("#WORKID:(.*?)#", header_data).group(1)
        start = dt.strptime(start, WorkLog._TIME_FORMAT)
        end = dt.strptime(end, WorkLog._TIME_FORMAT)
        return WorkLog(workid, start, end)

class WorkPage():
    def __init__(self, day=dt.now().date()):
        self.day = day
        self._PAGE_DIR = os.environ["HOME"] + "/.worklog/" + day.strftime("%Y.%W")
        self.page = self._PAGE_DIR + day.strftime('/%m.%d')
        os.makedirs(self._PAGE_DIR, mode=0o755, exist_ok=True)
        if not os.path.exists(self.page) or os.path.getsize(self.page) <= 0:
            self.write_header(WorkLog())

    def get_headers_str(self):
        headers = [str(wl) for wl in self.get_headers()]
        return headers

    def get_headers(self):
        rgx = re.compile("#WL(.*#)WL")
        headers = []
        with open(self.page, 'r') as page:
            for line in page.readlines():
                match = rgx.match(line)
                if match is not None:
                    headers.append(WorkLog.from_str(match.group(1)))
        return headers

    def calc_duration(self, id=None, calc_work=False, calc_break=False):
        total_time = timedelta() 
        for header  in self.get_headers():
            if id is not None:
                if (header.workid == id):
                    total_time += header.duration()
            else:
                if (calc_break and header.workid == "NO_ID") or \
                        (calc_work and header.workid != "NO_ID"):
                    total_time += header.duration()
        return total_time.total_seconds() / 60

    def write_header(self, wl):
        with open(self.page, 'a') as page:
            page.write(str(wl) + "\n")
        return

    def get_prev_end(self) -> time:
        """ Get the previous end time, e.g. to use as the start time """
        last_header = self.get_headers()[-1]
        return last_header.end_time 

    def add_break(self):
        start = self.get_prev_end()
        wl = WorkLog(start=start)
        self.write_header(wl)
        return
    
    def add_work(self, work_id):
        start = self.get_prev_end()
        wl = WorkLog(start=start, workid=work_id)
        self.write_header(wl)
        return

    def add_comment(self,comment):
        if comment is not None:
            with open(self.page, 'a') as page:
                for c in comment:
                    page.write(c + "\n")
        return
    
    def edit(self):
        editor = os.environ['EDITOR']
        if editor is None or len(editor) <= 0:
            editor = "nvim"
        os.system(f"{editor} {self.page}")
        return

    def show(self):
        with open(self.page, "r") as page:
            print(f"#WL# Date: {self.day.strftime('%x')}")
            for line in page:
                line = line.strip()
                if re.search("#WL.*#WL", line):
                    wl = WorkLog.from_str(line)
                    line_to_print = "#WL# "
                    if wl.workid == "NO_ID":
                        line_to_print = line_to_print + "Break\t"
                    else:
                        line_to_print = line_to_print + wl.workid + "\t"
                    line_to_print = line_to_print + f" {wl.start_time.strftime(WorkLog._TIME_FORMAT)} - {wl.end_time.strftime(WorkLog._TIME_FORMAT)} "
                    duration = wl.duration().total_seconds()
                    line_to_print = line_to_print + f"= {duration / 60} minutes"
                    print(line_to_print)
                else:
                    print(line)
        return

def main(args):
    wp = None
    if args.previous is not None or args.previous != 0:
        prev = float(args.previous)
        date = (dt.now() - timedelta(days=prev)).date()
        wp = WorkPage(date)
    else:
        wp = WorkPage()
    if args.command_name in ["break", "b"]:
        wp.add_break()
        wp.add_comment(args.message)
    elif args.command_name in ["work", "w"]:
        wp.add_work(args.id)
        wp.add_comment(args.message)
    elif args.command_name in ["calculate", "calc", "c"]:
        if args.id is not None and args.id != '':
            print(f"Total time for {args.id} is {wp.calc_duration(id=args.id)} minutes")
        else:
            if not args.breakoff and not args.total:
                args.work = True
            if args.breakoff or args.all:
                print(f"Total break time is {wp.calc_duration(calc_break=True)} minutes")
            if args.work or args.all:
                print(f"Total work  time is {wp.calc_duration(calc_work=True)} minutes")
            if args.total or args.all:
                print(f"Total spent time is {wp.calc_duration(calc_break=True, calc_work=True)} minutes")
    elif args.command_name in ["edit", "e"]:
        wp.edit()
    elif args.command_name in ["show", "s"]:
        wp.show()
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
    calculate_parser.add_argument("--id",    "-i", action="store",      metavar="ID", help="Calculate all types")
    edit_parser = sub_parsers.add_parser("edit", aliases=["e"])
    show_parser = sub_parsers.add_parser("show", aliases=["s"])

    args = parser.parse_args()
    main(args)

