N = int(input())

XY = [tuple(map(int, input().split())) for _ in range(N)]
S = input()

min_rs = {}
max_ls = {}

for (x, y), s in zip(XY, S):
    if s == 'R':
        if min_rs.get(y):
            min_rs[y] = min(min_rs[y], x)
        else:
            min_rs[y] = x
    elif s == 'L':
        if max_ls.get(y):
            max_ls[y] = max(max_ls[y], x)
        else:
            max_ls[y] = x

# print(min_rs)
# print(max_ls)

for y in min_rs.keys():
    if not max_ls.get(y):
        continue
    if min_rs[y] < max_ls[y]:
        print('Yes')
        exit()

print('No')
