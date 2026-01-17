N, Q = map(int, input().split())
S = list(input())


def is_abc(i: int) -> bool:
    return 0 <= i and i + 2 < N and S[i] == "A" and S[i + 1] == "B" and S[i + 2] == "C"


count_abc = sum(is_abc(i) for i in range(N))

for _ in range(Q):
    x, c = input().split()
    i = int(x) - 1

    if is_abc(i - 2) or is_abc(i - 1) or is_abc(i):
        count_abc -= 1

    S[i] = c

    if is_abc(i - 2) or is_abc(i - 1) or is_abc(i):
        count_abc += 1

    print(count_abc)
