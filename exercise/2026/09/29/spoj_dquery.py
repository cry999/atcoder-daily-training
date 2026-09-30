import math
import sys

input = sys.stdin.readline


N = int(input())
(*a,) = map(int, input().split())

Q = int(input())
queries = [tuple(map(int, input().split())) for _ in range(Q)]

B = max(1, int(N / math.sqrt(Q)))


def sort_key(i: int):
    l, r = queries[i]
    block = (l - 1) // B
    return (block, r if block % 2 == 0 else -r)


order = sorted(range(Q), key=sort_key)

# cnt[i] := i の個数
cnt = [0] * (max(a) + 1)
# kinds := 現在の区間に含まれる異なる値の種類数
kinds = 0


def add(i: int):
    """a[i] を区間に追加する"""
    global kinds

    assert i < N

    # print(f"[DEBUG] add({i}): {a[i]}")
    cnt[a[i]] += 1
    if cnt[a[i]] == 1:
        kinds += 1


def remove(i: int):
    """a[i] を区間から削除する"""
    global kinds

    assert i < N
    assert cnt[a[i]] > 0

    # print(f"[DEBUG] rem({i}): {a[i]}")
    cnt[a[i]] -= 1
    if cnt[a[i]] == 0:
        kinds -= 1


ans = [0] * Q
cl, cr = 0, 0  # 現在の区間 [cl, cr)

for q in order:
    l, r = queries[q]
    l -= 1
    # print(f"[DEBUG] {q=} ({cl}, {cr}) -> ({l}, {r})")

    # 先に区間を広げる
    while l < cl:
        cl -= 1
        add(cl)
        # print(f"[DEBUG]   ({cl}, {cr})")

    while cr < r:
        add(cr)
        cr += 1
        # print(f"[DEBUG]   ({cl}, {cr})")

    # 次に区間を狭める
    while cl < l:
        remove(cl)
        cl += 1
        # print(f"[DEBUG]   ({cl}, {cr})")

    while r < cr:
        cr -= 1
        remove(cr)
        # print(f"[DEBUG]   ({cl}, {cr})")

    ans[q] = kinds

print("\n".join(map(str, ans)))
