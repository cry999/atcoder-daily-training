"""公式 tester で解答と単純解を比較する。配布ツールは別途展開・ビルドする。"""
import argparse
import concurrent.futures
import json
import pathlib
import re
import statistics
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tools", type=pathlib.Path)
    parser.add_argument("--solver", type=pathlib.Path,
                        default=pathlib.Path(__file__).resolve().parents[1] / "ahc074_a.py")
    parser.add_argument("--executable", type=pathlib.Path,
                        help="コンパイル済みの解答を直接実行する")
    parser.add_argument("--solver-arg", action="append", default=[],
                        help="解答に渡す引数（複数回指定可）")
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--cases", type=int, default=100)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--baseline", action="store_true")
    parser.add_argument("--previous", action="store_true",
                        help="初版の 4 窓方式と比較する")
    parser.add_argument("--json", type=pathlib.Path)
    args = parser.parse_args()
    tools = args.tools.resolve()
    command = [str(tools / "target/release/tester"), args.python,
               str(args.solver.resolve())]
    if args.executable:
        if args.baseline or args.previous:
            parser.error("--executable と --baseline/--previous は併用できません")
        command = [str(tools / "target/release/tester"),
                   str(args.executable.resolve())]
    if args.baseline or args.previous:
        command[2] = str(pathlib.Path(__file__).resolve().parent / "baseline.py")
    if args.baseline:
        command.append("--baseline")

    command.extend(args.solver_arg)

    def run(seed):
        started = time.perf_counter()
        with (tools / "in" / f"{seed:04}.txt").open() as f:
            n, k, p, r = map(int, f.readline().split())
            f.seek(0)
            result = subprocess.run(command, stdin=f, capture_output=True,
                                    text=True, timeout=10)
        elapsed = time.perf_counter() - started
        match = re.search(r"Score = (\d+)", result.stderr)
        if result.returncode or not match:
            raise RuntimeError(f"seed={seed}: {result.stderr}")
        score = int(match[1])
        lines = result.stdout.splitlines()
        fallback = k > 2 * n and all(
            s == "." * n for s in lines[2 * n:k])
        pos, moves, maximum = k, 0, 0
        for _ in range(r):
            count = int(lines[pos])
            assert 0 <= count <= 2 * k
            maximum = max(maximum, count)
            moves += count
            pos += count + 1
        assert pos == len(lines), (seed, "extra or missing output")
        # 公式採点は 2*K*誤注文数+操作数。等しければ誤注文はゼロ。
        assert score == moves, (seed, "mistakes or invalid output", result.stderr)
        return {"seed": seed, "score": score, "mistakes": 0,
                "max_moves": maximum, "wall_seconds": elapsed,
                "fallback_design": fallback}

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(run, range(args.cases)))
    summary = {"cases": len(results), "score_sum": sum(x["score"] for x in results),
               "score_mean": statistics.mean(x["score"] for x in results),
               "score_min": min(x["score"] for x in results),
               "score_max": max(x["score"] for x in results),
               "mistakes": 0, "max_moves": max(x["max_moves"] for x in results),
               "fallback_designs": sum(x["fallback_design"] for x in results),
               "max_wall_seconds": max(x["wall_seconds"] for x in results)}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.json:
        args.json.write_text(json.dumps({"summary": summary, "cases": results},
                                        ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
