import os
import myabiparser

from blast import BlastPlasmid


print('hello world')
folder = 'seq'
dirs = os.listdir('seq')
sequences = []
for file in dirs:
    main, ext = os.path.splitext(file)
    if ext == '.ab1':
        print(file)
        a = myabiparser.open_trace2(os.path.join(folder,file))
        a.setTraces()
        sequences.append(a.sequence)

# print(len(sequences))

l = len(sequences)
for i in range(l):
    bm = BlastPlasmid(sequences[i])
    for j in range(i+1,l):    
        match = bm.blast6(sequences[j])
        print(i,j, len(sequences[i]), len(sequences[j]))
        print(match)