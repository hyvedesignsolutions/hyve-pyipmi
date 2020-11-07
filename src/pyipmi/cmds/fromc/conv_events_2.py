#!/usr/bin/env python3

infile = 'specific_events.c'
outfile = 'specific_events.py'

fin = open(infile, 'r')
fout = open(outfile, 'w')

fout.write('SPECIFIC_EVENT_TYPES = {\n')

list_all = []
list_one = []
type_pre = '0x05'
comment_pre = ''
comment = ''

while True:
    line = fin.readline()
    if not line:    break       # end of file
    line = line.strip()
    if not line:    continue    # empty line

    if line[:2] == '/*':        # comments
        comment_pre = comment
        comment = '# ' + line[2:-2]
        continue

    list_line = line.split(',')
    if len(list_line) < 4: continue
    type_line = list_line[0][2:]

    end = list_line[4].strip()
    if end:
        event = list_line[3][2:] + ', ' + end[:-3]
    else: 
        event = list_line[3][2:-3]

    if type_pre != type_line:
        list_one = [type_pre, comment_pre] + list_one
        list_all.append(list_one)
        list_one = []
        type_pre = type_line
    list_one.append(event)

for i in list_all:
    #fout.write(' ' * 4 + '(\n')
    for j in i:
        if j[0] == '#':
            fout.write(' ' * 8 + j.strip() + '\n')
        elif j[:2] == '0x':
            fout.write(' ' * 4 + j + ': (\n')
        else:
            fout.write(' ' * 8 + '\'' + j.strip() + '\',\n')
    fout.write(' ' * 4 + '),\n')


fout.write('}\n\n')

fin.close()
fout.close()
