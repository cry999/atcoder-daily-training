N, Q = map(int, input().split())
*A, = map(lambda x: int(x)-1, input().split())

person = [[0]*30 for _ in range(N)]
for i in range(N):
    person[i][0] = A[i]

for d in range(1, 30):
    for i in range(N):
        j = person[i][d-1]
        person[i][d] = person[j][d-1]


def compute_person(i: int, t: int) -> int:
    d = 0
    while t:
        if t & 1:
            i = person[i][d]
        d += 1
        t >>= 1
    return i


buckets = [[0]*30 for _ in range(N)]
for i in range(N):
    buckets[i][0] = i+1

for d in range(1, 30):
    for i in range(N):
        j = person[i][d-1]
        buckets[i][d] = buckets[i][d-1]+buckets[j][d-1]


def compute_buckets(i: int, t: int) -> int:
    d = 0
    ans = 0
    while t:
        if t & 1:
            ans += buckets[i][d]
            i = person[i][d]
        t >>= 1
        d += 1
    return ans


for _ in range(Q):
    T, B = map(int, input().split())

    print(compute_buckets(B-1, T))
