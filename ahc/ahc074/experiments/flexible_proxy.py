import heapq, json, random
from pathlib import Path
import sys
TOOLS = Path(sys.argv[1])
ALL=(1<<64)-1

def run(seed,t):
 data=(TOOLS / 'in' / f'{seed:04}.txt').read_text().split()
 codes=[sum((c=='1')<<j for j,c in enumerate(s)) for s in data[4:260]]
 flip=sum((sum(x>>j&1 for x in codes)<128)<<j for j in range(64));codes=[x^flip for x in codes]
 hm=(1<<14)-1; cm=ALL^hm
 # Representative: majority on two-sided columns, AND on one-sided columns.
 flex=((1<<t)-1)<<14;one=cm^flex
 clusters={i:([x],x,x,[(x>>j)&1 for j in range(14,14+t)],0) for i,x in enumerate(codes)}
 def merged(a,b):
  xs,ba,oa,ca,sa=clusters[a];ys,bb,ob,cb,sb=clusters[b]
  same=ALL^((ba^bb)|(ba^oa)|(bb^ob))
  if not same&hm:return None
  nn=len(xs)+len(ys);counts=[x+y for x,y in zip(ca,cb)]
  base=(ba&bb)&one
  for z,n in enumerate(counts):
   if n*2>=nn:base|=1<<(14+z)
  score=sum(((x^base)&cm).bit_count() for x in xs+ys)
  return score-sa-sb,(xs+ys,ba&bb,oa|ob,counts,score)
 heap=[]
 for a in clusters:
  for b in range(a):
   q=merged(a,b)
   if q:heap.append((q[0],a,b))
 heapq.heapify(heap);nxt=256
 while len(clusters)>142-t:
  _,a,b=heapq.heappop(heap)
  if a not in clusters or b not in clusters:continue
  q=merged(a,b)
  if q is None:continue
  obj=q[1];del clusters[a];del clusters[b];clusters[nxt]=obj
  for j in list(clusters):
   if j!=nxt:
    v=merged(nxt,j)
    if v:heapq.heappush(heap,(v[0],nxt,j))
  nxt+=1
 bases=[]
 for xs,ba,oa,counts,score in clusters.values():
  base=ba&one
  for z,n in enumerate(counts):
   if n*2>=len(xs):base|=1<<(14+z)
  bases.append(base)
 counts=[];cost=[];near2=[];near4=[];near6=[]
 for x in codes:
  compatible=[b for b in bases if not(b&one&~x)]
  ds=[((x^b)&cm).bit_count() for b in compatible];best=min(ds);counts.append(len(compatible));cost.append(best);near2.append(sum(d<=best+2 for d in ds));near4.append(sum(d<=best+4 for d in ds));near6.append(sum(d<=best+6 for d in ds))
 return {'seed':seed,'t':t,'pages':len(bases),'compatible':sum(counts)/256,'min_compatible':min(counts),'correction':sum(cost)/256,'zero_retrieval_proxy':8.5+sum(cost)/256,'near2':sum(near2)/256,'near4':sum(near4)/256,'near6':sum(near6)/256,'max_cluster':max(len(z[0]) for z in clusters.values())}
rows=[]
for seed in range(4):
 for t in [32,50]:
  q=run(seed,t);rows.append(q);print(json.dumps(q),flush=True)
