# Worklog

Ever wanted to record every minute and every jira issue of your working time? And you tried to find the perfect tool but all of them are too complex for such a simple need?

Worklog is a tool for easily recording how much you spend on tasks and on breaks. You can also enter notes so that you have the recorded memory of the stuff you did.

A daily workflow is as follows:

- You start the work day by simply calling the `wl.py`. It generates a file for the day and records the date.
- You start working on an issue, e.g. JIRA-1111. When you stop working for that issue, either that you switch to another issue or you took a break, you simply type `wl w JIRA-1111`. This command creates a record with timestamp. Since we always record the timestamp, we always know how much we spent on any tasks. You can also attach some comment using `-m <MESSAGE>` to the entry, which is very useful for documentating useful information.
- Lets say you took a break, and came back to work. You simply type `wl b` and it generates the break record.
- And the day goes on like this, you took breaks and worked for long hours et cetera, and created a day's worth of record. You want to see the todays records, you simply type `wl s`
- You can generate reports too! You simply type `wl c` for the current day or `wl c -p 2` for the 2nd previous day. You can even generate the reports for a specific jira issue or breaks! You simply type either `wl c -i JIRA-1111` or `wl c -b`.

This tool is intentionally kept simple, because anyone can wrap their heads around it very easily and bend it to their will. If you have any pull requests or feature requests, send them away!

For misc. stuff that does not have a specific jira issue id, for example responding to immediate support requests or daily meetings, you can define abbrevations or aliases in your shell. For example in fish, you would do:

```sh
abbr --set-cursor -a -- wlops "wl w JIRA-000000 -m '%'" # Misc stuff that does not have an assigned issue, like recurring operations, helping colleagues or pairing with others.
abbr --set-cursor -a -- wldaily "wl w JIRA-000001 -m 'Daily %'" # Recurring meetings etc.
```

This way, you are assigning id's to these part of your time and you can track it in this tool. It is very practical ;)

Example worklog:
```
#WL#WORKID:BRP-000001#START:09.30#END:09.30#WL
#WL#WORKID:BRP-000001#START:09.30#END:09.39#WL
Daily meeting
#WL#WORKID:BRP-000000#START:09.39#END:17.00#WL
did work all day
```
