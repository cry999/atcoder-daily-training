S = "".join(input().split())
T = "".join(input().split())

# 偶数回の移動で到達可能
evens = set(["RGB", "BRG", "GBR"])

if S in evens and T in evens:
    print("Yes")
elif S not in evens and T not in evens:
    print("Yes")
else:
    print("No")
