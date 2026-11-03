import sys,random

def main():
 read=sys.stdin.readline
 n,k,p,r=map(int,read().split());strings=[read().strip() for _ in range(p)]
 codes=[sum((c=='1')<<j for j,c in enumerate(s)) for s in strings]
 h=int(sys.argv[1]) if len(sys.argv)>1 else 16
 rng=random.Random(74)
 handles=list(range(h)); content=list(range(h,64));cm=sum(1<<j for j in content)
 c=k-len(content)
 # 各紙は商品ペアの共通の黒だけを印刷し、残りを単独の黒紙で補う。
 edges=[]
 hm=sum(1<<j for j in handles)
 for a in range(p):
  for b in range(a):
   if (~(codes[a]^codes[b])&hm):edges.append((((codes[a]^codes[b])&cm).bit_count(),a,b))
 edges.sort();used=set();clusters=[]
 for cost,a,b in edges:
  if a not in used and b not in used and len(used)//2<p-c:
   used.add(a);used.add(b);clusters.append([a,b])
 clusters += [[a] for a in range(p) if a not in used]
 # 2 組の相手交換と、単独商品との入れ替えで距離を下げる。
 def distance(a,b):return ((codes[a]^codes[b])&cm).bit_count() if (~(codes[a]^codes[b])&hm) else 999
 for _ in range(3):
  improved=False
  rng.shuffle(clusters)
  for i in range(c):
   if len(clusters[i])!=2:continue
   a,b=clusters[i]
   for j in range(i+1,c):
    other=clusters[j]
    if len(other)==1:
     d=other[0];old=distance(a,b);da,db=distance(a,d),distance(b,d)
     if min(da,db)<old:
      if da<=db:clusters[i],clusters[j]=[a,d],[b];b=d
      else:clusters[i],clusters[j]=[b,d],[a];a,b=b,d
      improved=True
    else:
     x,y=other;old=distance(a,b)+distance(x,y)
     da,db=distance(a,x)+distance(b,y),distance(a,y)+distance(b,x)
     if min(da,db)<old:
      if da<=db:clusters[i],clusters[j]=[a,x],[b,y];b=x
      else:clusters[i],clusters[j]=[a,y],[b,x];b=y
      improved=True
  if not improved:break
 assert len(clusters)==c
 # 同じ取っ手の黒白を交互に並べられるよう、同数ずつ割り当てる。
 sizes=[(c//(2*h))*2]*h
 for g in range((c-sum(sizes))//2):sizes[g]+=2
 assert sum(sizes)==c
 slots=[[[ ] for _ in range(2)] for g in range(h)]
 choices=[]
 for cl in clusters:
  candidates=[]
  for g,j in enumerate(handles):
   colors=[codes[a]>>j&1 for a in cl]
   if min(colors)==max(colors):candidates.append((g,colors[0]))
  choices.append(candidates)
 # 小さい二部マッチングで各色の定員を満たす。
 capacity={(g,col):sizes[g]//2 for g in range(h) for col in range(2)}
 assigned={}
 def put(i,seen):
  for gc in sorted(choices[i],key=lambda z:len(slots[z[0]][z[1]])/max(1,capacity[z])):
   if gc in seen:continue
   seen.add(gc);g,col=gc
   if len(slots[g][col])<capacity[gc]:slots[g][col].append(i);assigned[i]=gc;return True
   for old in slots[g][col][:]:
    if put(old,seen):slots[g][col].remove(old);slots[g][col].append(i);assigned[i]=gc;return True
  return False
 for i in sorted(range(c),key=lambda i:len(choices[i])):
  assert put(i,set()),(i,h,'assignment')
 pages=[];groups=[];member=[0]*p;pagecolor=[]
 for g in range(h):
  group=[]
  for i0,i1 in zip(slots[g][0],slots[g][1]):
   for i in (i0,i1):
    cl=clusters[i];base=codes[cl[0]]
    for a in cl[1:]:base &= codes[a]
    j=handles[g];opaque=cm|(1<<j)
    for a in cl:member[a]=len(content)+len(pages)
    group.append(len(content)+len(pages));pages.append((opaque,base&opaque));pagecolor.append(base>>j&1)
  groups.append(group)
 masks=[1<<j for j in content]+[x[0] for x in pages]
 blacks=[1<<j for j in content]+[x[1] for x in pages]
 # 単独の黒紙は全ページより上に保つ。
 order=list(range(k));loc=[0]*k
 for g,group in enumerate(groups):
  for item in group:loc[item]=g
 current=-1
 for opaque,black in zip(masks,blacks):print(''.join(str(black>>j&1) if opaque>>j&1 else '.' for j in range(n)))
 sys.stdout.flush()
 tops=[0]*h
 for turn in range(r):
  a=int(read())
  if a<0:return
  target=codes[a];page=member[a];g=loc[page];moves=[]
  def move(item,d):
   ix=order.index(item);order.pop(ix);order.insert(d,item);moves.append((item,d))
  def retire(group):
   item=groups[group][tops[group]];move(item,k-1);tops[group]=(tops[group]+1)%len(groups[group])
  if current>=0:retire(loc[current])
  while groups[g][tops[g]]!=page:retire(g)
  # 現在は各窓の単独黒紙が見えているので、必要なものを先に取り出す。
  patches=target&cm&~blacks[page]
  count=0
  for j in range(len(content)):
   if patches>>content[j]&1:move(j,0);count+=1
  move(page,count);current=page
  for group,j in enumerate(handles):
   if group!=g and (blacks[groups[group][tops[group]]]>>j&1)!=(target>>j&1):retire(group)
  print(str(len(moves))+''.join(f'\n{x} {d}' for x,d in moves),flush=True)

if __name__=='__main__':main()
