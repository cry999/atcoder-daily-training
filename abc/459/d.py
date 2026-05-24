from sortedcontainers import SortedList

T = int(input())

for _ in range(T):
    S = input()
    hist = {}
    for s in S:
        hist[s] = hist.get(s, 0) + 1

    N = len(S)

    for n in hist.values():
        if N + 1 >= 2 * n:
            continue
        print("No")
        break
    else:
        print("Yes")
        q = SortedList(map(lambda x: (x[1], x[0]), hist.items()))

        ans = [""] * N
        while q:
            n, c = q.pop()

            if ans and ans[-1] == c:
                n1, c1 = q.pop()
                q.add((n, c))
                ans.append(c1)
                if n1 - 1:
                    q.add((n1 - 1, c1))
            else:
                ans.append(c)
                if n - 1:
                    q.add((n - 1, c))
        print("".join(ans))
