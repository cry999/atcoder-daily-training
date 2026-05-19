T = int(input())


def peal(s: str):
    res = []
    for c in s:
        if c == ")":
            if len(res) >= 3 and res[-3] + res[-2] + res[-1] == "(xx":
                res.pop()
                res.pop()
                res.pop()
                res.append("x")
                res.append("x")
            else:
                res.append(c)
        else:
            res.append(c)
    return res


for _ in range(T):
    A = input()
    B = input()

    if peal(A) == peal(B):
        print("Yes")
    else:
        print("No")
