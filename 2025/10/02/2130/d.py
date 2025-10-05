N = int(input())
S = list(input() for _ in range(N))

m = {}
for s in S:
    if not (s[0] in 'HDCS'):
        print('No')
        # print('s[0]')
        break
    if not (s[1] in 'A23456789TJQK'):
        print('No')
        # print('s[1]')
        break
    if m.get(s[0], {}).get(s[1], 0):
        print('No')
        # print('dup')
        break
    if not m.get(s[0], None):
        m[s[0]] = {}
    m[s[0]][s[1]] = m.get(s[1], 0) + 1
else:
    print('Yes')
