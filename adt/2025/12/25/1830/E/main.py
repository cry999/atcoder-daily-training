from collections import defaultdict


S = input()
T = input()

hist = defaultdict(int)
s_atmarks = S.count('@')
t_atmarks = T.count('@')

for s in S:
    if s == '@':
        continue
    hist[s] += 1
for t in T:
    if t == '@':
        continue
    hist[t] -= 1

for k in hist:
    if k == '@':
        continue
    if hist[k] == 0:
        continue
    if k in 'atcoder':
        if hist[k] > 0:
            if hist[k] <= t_atmarks:
                t_atmarks -= hist[k]
                hist[k] = 0
            else:
                # print('<T atmark is not enough>')
                print('No')
                exit()
        else:
            if -hist[k] <= s_atmarks:
                s_atmarks += hist[k]
                hist[k] = 0
            else:
                # print('<S atmark is not enough>')
                print('No')
                exit()
    else:
        # atcoder 以外の文字が異なる場合は変換不可能なので 'No'
        # print(f'<not atcoder char>, {k=}, {hist[k]=}')
        print('No')
        exit()

if all(v == 0 for v in hist.values()):
    print('Yes')
else:
    print('No')
