from collections import defaultdict

N = int(input())

g = {}
check = defaultdict(bool)

for _ in range(N):
    prev_name, next_name = input().split()
    g[prev_name] = next_name
    check[prev_name] = False

for name in g.keys():
    s = name
    while not check[name] and name in g:
        check[name] = True
        name = g[name]

        if s == name:
            print("No")
            break
    else:
        continue
    break
else:
    print("Yes")
