N, M = map(int, input().split())
S = input()
T = input()

Q = int(input())
for _ in range(Q):
    w = input()

    is_takahashi = True
    is_aoki = True
    for c in w:
        if c not in S:
            is_takahashi = False
        if c not in T:
            is_aoki = False
    if is_takahashi and is_aoki:
        print("Unknown")
    elif is_takahashi:
        print("Takahashi")
    elif is_aoki:
        print("Aoki")
    else:
        print("Unknown")
