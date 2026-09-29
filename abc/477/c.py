Q = int(input())
S = input()
T = input()

# S[i] からみた時に T が部分文字列と含まれる最小の r を管理する。
min_rights = [len(S) + 2] * (len(S) + 1)

# 末端から確認していって、
# S[i] から始まる部分文字列が T と一致 => min_rights[i] = i + len(T) - 1
# そうでない => min_rights[i] = min_rights[i + 1]

for i in range(len(S) - len(T), -1, -1):
    if S[i : i + len(T)] == T:
        min_rights[i] = i + len(T) - 1
    else:
        min_rights[i] = min_rights[i + 1]

for _ in range(Q):
    l, r = map(int, input().split())
    l, r = l - 1, r - 1
    if min_rights[l] <= r:
        print("Yes")
    else:
        print("No")
