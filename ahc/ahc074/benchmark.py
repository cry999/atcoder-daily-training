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
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--cases", type=int, default=100)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--baseline", action="store_true")
    parser.add_argument("--json", type=pathlib.Path)
    args = parser.parse_args()
    tools = args.tools.resolve()
    command = [str(tools / "target/release/tester"), args.python,
               str(args.solver.resolve())]
    if args.baseline:
        command.append("--baseline")

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
                "max_moves": maximum, "wall_seconds": elapsed}

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(run, range(args.cases)))
    summary = {"cases": len(results), "score_sum": sum(x["score"] for x in results),
               "score_mean": statistics.mean(x["score"] for x in results),
               "score_min": min(x["score"] for x in results),
               "score_max": max(x["score"] for x in results),
               "mistakes": 0, "max_moves": max(x["max_moves"] for x in results),
               "max_wall_seconds": max(x["wall_seconds"] for x in results)}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.json:
        args.json.write_text(json.dumps({"summary": summary, "cases": results},
                                        ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
