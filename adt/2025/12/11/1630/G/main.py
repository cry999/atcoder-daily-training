A, B, C, D = map(int, input().split())

primes = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
    31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
    127, 131, 137, 139, 149, 151, 157, 163, 167, 173,
    179, 181, 191, 193, 197, 199,
]

for takahashi in range(A, B+1):
    for p in primes:
        if C <= p-takahashi <= D:
            # 青木くんが勝つ方法がある
            break
        continue
    else:
        # この数字を出せば高橋くんが勝つ
        print('Takahashi')
        break
else:
    # 高橋くんが勝てる数字が見つからない
    print('Aoki')
