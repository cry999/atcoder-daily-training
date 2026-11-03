import json,random,statistics
from pathlib import Path
import sys
TOOLS = Path(sys.argv[1])
ALL=(1<<64)-1
rows=[]
for degree in [2,3,4,23]:
 for seed in range(8):
  rng=random.Random(7400+seed)
  patterns=set()
  while len(patterns)<127:
   d=rng.choice([2,3]) if degree==23 else degree
   patterns.add(sum(1<<j for j in rng.sample(range(64),d)))
  patterns=list(patterns)
  degrees=[1+sum(m>>j&1 for m in patterns) for j in range(64)]
  codes=[sum((v=='1')<<j for j,v in enumerate(s)) for s in (TOOLS / 'in' / f'{seed:04}.txt').read_text().split()[4:260]]
  covers=[];exposes=[]
  for target in codes:
   eligible=[m for m in patterns if m&target==m]
   best=32
   for restart in range(24):
    rem=target;count=0
    while rem:
     gs=[((m&rem).bit_count(),rng.random(),m) for m in eligible]
     if not gs:count+=rem.bit_count();break
     gain,_,m=max(gs)
     if gain<2:count+=rem.bit_count();break
     rem&=~m;count+=1
    best=min(best,count)
   covers.append(best);exposes.append(min(degrees[j] for j in range(64) if not target>>j&1))
  obj={'degree':degree,'seed':seed,'cover':statistics.mean(covers),'expose':statistics.mean(exposes),'proxy':statistics.mean(covers)+statistics.mean(exposes)+2,'mindegree':min(degrees),'maxdegree':max(degrees)}
  rows.append(obj);print(json.dumps(obj),flush=True)
