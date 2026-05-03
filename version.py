import re
from datetime import date
from pprint import pprint

with open('lang/english.lng', 'r') as file:
    data = file.read()

found = False
for line in data.split('\n'):
    m = re.search("^(STR_GRF_DESC[ \t]*:.*)Ver.([0-9]+) .*$", line)

    if m:
        found = True
        prefix = m[1]
        version = int(m[2])+1
        date = date.today().strftime("%Y.%m.%d.")
        newline = f"{prefix}Ver.{version} {date}"
        
        print(f"New version: Ver.{version}")
        
        data = data.replace(line, newline)
        break

if found:
    with open('lang/english.lng', "w") as text_file:
        text_file.write(data)
else:
    print("Cannot find the line in lang/english.lng containing STR_GRF_DESC")