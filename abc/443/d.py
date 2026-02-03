from collections import deque

T = int(input())

for _ in range(T):
    N = int(input())
    (*R,) = map(int, input().split())

    ans = 0
    to_be_continued = True
    while to_be_continued:
        to_be_continued = False
        for i in range(N - 1, -1, -1):
            if i - 1 >= 0 and abs(R[i - 1] - R[i]) > 1:
                # print(f"check: {i=}, {R[i]=} and {R[i-1]=}")
                to_be_continued = True

                ans += abs(R[i - 1] - R[i]) - 1
                if R[i - 1] > R[i]:
                    R[i - 1] = R[i] + 1
                else:
                    R[i] = R[i - 1] + 1

        for i in range(N):
            if i + 1 < N and abs(R[i + 1] - R[i]) > 1:
                # print(f"check: {i=}, {R[i]=} and {R[i+1]=}")
                to_be_continued = True

                ans += abs(R[i + 1] - R[i]) - 1
                if R[i + 1] > R[i]:
                    R[i + 1] = R[i] + 1
                else:
                    R[i] = R[i + 1] + 1
    # print(*R)
    print(ans)
