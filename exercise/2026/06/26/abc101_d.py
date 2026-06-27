K = int(input())


def snuke(n: int):
    s = 0
    while n > 0:
        s += n % 10
        n //= 10
    return s


ans = set()
d = 1
while len(ans) < K:
    n = 1
    while len(ans) < K:
        x = d * n + (d - 1)
        y = d * (n + 1) + (d - 1)

        if x * snuke(y) > snuke(x) * y:
            break

        ans.add(x)
        n += 1

    d *= 10

sorted_ans = sorted(ans)
for k in range(K):
    a = sorted_ans[k]
    if a > 10**15:
        print(10**15)
        break
    else:
        print(a)
