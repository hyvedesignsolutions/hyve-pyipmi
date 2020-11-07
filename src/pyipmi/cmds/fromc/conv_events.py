#!/usr/bin/env python3

infile = 'generic_events.c'
outfile = 'generic_events.py'

fin = open(infile, 'r')
fout = open(outfile, 'w')

fout.write('GENERIC_EVENT_TYPES = (\n')
fout.write('    (\n')
fout.write('        # 0x00 - Nothing\n')
fout.write('    ),\n')

list_all = []
list_one = []
type_pre = '0x01'
comment_pre = ''
comment = ''

while True:
    line = fin.readline()
    if not line:    break       # end of file
    line = line.strip()
    if not line:    continue    # empty line

    if line[:2] == '/*':        # comments
        comment_pre = comment
        comment = line[2:-2]
        continue

    list_line = line.split(',')
    if len(list_line) < 4: continue
    type_line = list_line[0][2:]
    event = list_line[3][2:-3]
    if type_pre != type_line:
        list_one.insert(0, '# ' + type_pre + ' - ' + comment_pre.strip())
        list_all.append(list_one)
        list_one = []
        type_pre = type_line
    list_one.append(event)

for i in list_all:
    fout.write(' ' * 4 + '(\n')
    for j in i:
        if j[0] == '#':
            fout.write(' ' * 8 + j.strip() + '\n')
        else:
            fout.write(' ' * 8 + '\'' + j.strip() + '\',\n')
    fout.write(' ' * 4 + '),\n')

fout.write(')\n\n')

fin.close()
fout.close()
