import bisect

N, Q = map(int, input().split())
follows = {}


def is_following(a: int, b: int) -> bool:
    f = follows.get(a, [])
    i = bisect.bisect_left(f, b)
    return 0 <= i < len(f) and f[i] == b


def follow(a: int, b: int):
    if is_following(a, b):
        return
    f = follows.get(a, [])
    bisect.insort_left(f, b)
    follows[a] = f


def unfollow(a: int, b: int):
    if not is_following(a, b):
        return
    f = follows.get(a, [])
    i = bisect.bisect_left(f, b)
    follows[a] = f[:i] + f[i+1:]


for _ in range(Q):
    T, A, B = map(int, input().split())
    # print(follows)
    if T == 1:
        follow(A, B)
    elif T == 2:
        unfollow(A, B)
    else:  # T == 3
        if is_following(A, B) and is_following(B, A):
            print('Yes')
        else:
            print('No')
