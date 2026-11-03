import itertools,random
rng=random.Random(74)
checks=0
for size in range(2,13):
 for bits in itertools.product([0,1],repeat=size-1):
  color=[bits[0],1-bits[0]]+list(bits[1:])
  for rank in range(size):
   for rep in range(2):
    v=list(range(size));weight=[rng.randint(1,4) for _ in v]
    if rank==0:
     desired=v[:1];assert color[v[0]]!=color[v[1]];checks+=1;continue
    page=v[rank];prefix=v[:rank+1]
    partner=max((x for x in prefix if color[x]!=color[page]),key=lambda x:weight[x])
    desired=[page,partner]+sorted((x for x in prefix if x not in [page,partner]),key=lambda x:-weight[x])
    placed={page};original=v[:]
    for item in original[:rank]:
     assert v[0]==item
     ix=desired.index(item);anchor=next(x for x in reversed(desired[:ix]) if x in placed)
     d=v.index(anchor);v.remove(item);v.insert(d,item);placed.add(item)
    assert v==desired+original[rank+1:]
    assert color[v[0]]!=color[v[1]]
    # A single head-to-after-second move always flips while retaining the invariant.
    head=v.pop(0);v.insert(1,head)
    assert color[v[0]]!=color[v[1]]
    checks+=1
print('head-two abstract checks:',checks)
