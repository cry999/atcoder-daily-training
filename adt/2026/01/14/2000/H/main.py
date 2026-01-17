N = int(input())

# まずは i から決める
lo, hi = 0, N
while hi - lo > 1:
    mi = (lo + hi) // 2
    print(f"? {lo+1} {mi} 1 {N}")
    T = int(input())
    if T == mi - lo:
        lo = mi
    else:
        hi = mi

i = hi

lo, hi = 0, N
while hi - lo > 1:
    mi = (lo + hi) // 2
    print(f"? 1 {N} {lo+1} {mi}")
    T = int(input())
    if T == mi - lo:
        lo = mi
    else:
        hi = mi

j = hi

print(f"! {i} {j}")
