S = input()
m = {}
for c in S:
    m[c] = m.get(c, 0) + 1

for c in m.keys():
    if m[c] == 1:
        print(c)
