# Worklog

Ever wanted to record every minute and every jira issue of your working time? And you tried to find the perfect tool but all of them are too complex for such a simple need?

Worklog is a tool for easily recording how much you spend on tasks and on breaks. You can also enter notes so that you have the recorded memory of the stuff you did.

A daily workflow is as follows:

- You start the work day by simply calling the `wl.py`. It generates a file for the day and records the date.
- You start working on an issue, e.g. JIRA-1111. When you stop working for that issue, either that you switch to another issue or you took a break, you simply type `wl w JIRA-1111`. This command creates a record with timestamp. Since we always record the timestamp, we always know how much we spent on any tasks.
- Lets say you took a break, and came back to work. You simply type `wl b` and it generates the break record.
- And the day goes on like this, you took breaks and worked for long hours et cetera, and created a day's worth of record. You want to see the todays records, you simply type `wl s`
- You can generate reports too! You simply type `wl c` for the current day or `wl c -p 2` for the 2nd previous day. You can even generate the reports for a specific jira issue or breaks! You simply type either `wl c -i JIRA-1111` or `wl c -b`.

This tool is intentionally kept simple, because anyone can wrap their heads around it very easily and bend it to their will. If you have any pull requests or feature requests, send them away!
