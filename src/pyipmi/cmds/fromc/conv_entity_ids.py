#!/usr/bin/env python3

infile = 'entity_ids.c'
outfile = 'entity_ids.py'

fin = open(infile, 'r')
fout = open(outfile, 'w')

fout.write('ENTITY_ID_CODES = (\n')
while True:
    line = fin.readline()
    if not line:    break       # end of file
    line = line.strip()
    if not line:    continue    # empty line

    list_line = line.split(',')
    if len(list_line) < 2: continue
    list_line = [x.strip() for x in list_line]
    if list_line[0][2:] == '0x00': continue

    fout.write(' ' * 4 + '\'' + list_line[1][1:-3] + '\',\n')

fout.write(')\n\n')

fin.close()
fout.close()

