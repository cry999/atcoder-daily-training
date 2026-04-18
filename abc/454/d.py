from sys import stdin

input = stdin.readline

T = int(input())

for _ in range(T):
    A = input()
    B = input()

    def clean_str(s: str) -> str:
        r = []
        for c in s:
            if c == ")":
                if len(r) >= 3 and r[-3] == "(" and r[-2] == r[-1] == "x":
                    r.pop()  # x
                    r.pop()  # x
                    r.pop()  # (

                    r.append("x")
                    r.append("x")
                else:
                    r.append(c)

            else:  # s[i] == 'x':
                r.append(c)
        return "".join(r)

    # print(f"{A=} -> a={clean_str(A)}")
    # print(f"{B=} -> b={clean_str(B)}")
    sa = clean_str(A)
    sb = clean_str(B)

    if sa == sb:
        print("Yes")
    else:
        print("No")
