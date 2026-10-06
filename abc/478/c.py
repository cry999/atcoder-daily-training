N, K = map(int, input().split())
(*A,) = map(int, input().split())
B = sorted(A)


i = 0
count_up = False
while i < N:
    if not count_up and A[i] != B[i]:
        # 初めて A[i] != B[i] となったところから K 個は入れ替わってても良い
        count_up = True
        i += K

    if count_up and A[i] != B[i]:
        print("No")
        exit()

    i += 1
print("Yes")
