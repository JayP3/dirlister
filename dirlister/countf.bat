@echo off
for /F %%R in (count_these.txt) do python countf.py %%R --logfile napfileserver.idx
