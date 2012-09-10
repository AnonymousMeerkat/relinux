import subprocess
import re
import sys

temp = subprocess.Popen(["python", "./test.py"], stdout=subprocess.PIPE, universal_newlines=True)
patt = re.compile("^ *\[=*[|/-\\]* *\] *[0-9]*/[0-9]* *([0-9]*)% *$")
while temp.poll() is None:
    output = temp.stdout.readline()
    match = patt.match(output)
    if match != None:
        sys.stdout.write("\r" + match.group(0))
sys.stdout.write("\n")