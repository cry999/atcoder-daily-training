S = input()

now = 'A'
for s in S:
    if s == now:
        continue
    if s > now:
        now = s
        continue
    print('No')
    exit()

print('Yes')
