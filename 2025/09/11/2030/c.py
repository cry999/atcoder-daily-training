H, M = map(int, input().split())


def is_easy_to_misread(H: int, M: int) -> bool:
    A, B = H // 10, H % 10
    C, D = M // 10, M % 10

    return (A*10 + C) < 24 and (B*10+D) < 60


def next_time(H: int, M: int) -> tuple[int, int]:
    if M == 59:
        return (H + 1) % 24, 0
    return H, M + 1


while True:
    if is_easy_to_misread(H, M):
        print(H, M)
        exit()
    H, M = next_time(H, M)
