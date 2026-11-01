"""dap-probe のテスト (debugpy が要る)。

実際に debugpy を起動し、小さなスクリプトをブレークポイントで止めて記録を確かめる。

実行: python3 tests/test_dap_probe.py   (リポジトリ root で。debugpy を import できる python で)
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "dap-probe"

TARGET = textwrap.dedent(
    """\
    def add(a, b):
        return a + b


    def call_multiline(x):
        y = add(
            x,
            2,
        )
        return y


    for i in range(2):
        call_multiline(i)

    total = 0
    for j in range(3):
        total += j
    """
)
# 行番号 (1 始まり)
LINE_MULTILINE_CALL = 6
LINE_LOOP_BODY = 18

RAISING = textwrap.dedent(
    """\
    def fail(value):
        raise ValueError(f"bad value: {value}")


    fail(42)
    """
)


def run_probe(tmp: Path, target_source: str, breakpoints: list[dict], *extra: str) -> dict:
    target = tmp / "target.py"
    target.write_text(target_source)
    for bp in breakpoints:
        bp["file"] = str(target)
    spec = tmp / "spec.json"
    spec.write_text(json.dumps({"breakpoints": breakpoints, "exceptions": ["uncaught"]}))
    out = tmp / "probe.json"
    subprocess.run(
        [sys.executable, str(SCRIPT), "--spec", str(spec), "--out", str(out), "--timeout", "60", *extra,
         "--", sys.executable, str(target)],
        check=True,
        capture_output=True,
        timeout=120,
    )
    return json.loads(out.read_text())


class RecordTest(unittest.TestCase):
    def test_multiline_call_recorded_once_per_call(self):
        with tempfile.TemporaryDirectory() as d:
            result = run_probe(Path(d), TARGET, [{"line": LINE_MULTILINE_CALL, "eval": ["x"]}])
        hits = [(h["line"], h["eval"]["x"]) for h in result["hits"]]
        # 2 回の呼び出しがそれぞれ 1 件ずつ。引数の評価後の line イベントの再発は数えない
        self.assertEqual(hits, [(LINE_MULTILINE_CALL, "0"), (LINE_MULTILINE_CALL, "1")])
        # Python 3.12 と 3.13 は、呼び出しごとに同じ行の停止をもう 1 回出す (2026-10-15 に確認)
        self.assertEqual(result["skipped_repeat_stops"], 2)
        self.assertEqual(result["errors"], [])

    def test_loop_body_recorded_every_iteration(self):
        with tempfile.TemporaryDirectory() as d:
            result = run_probe(Path(d), TARGET, [{"line": LINE_LOOP_BODY, "eval": ["j"], "max_hits": 5}])
        # 同じフレームの同じ行でも、ループで戻った停止は別の実行として記録する
        self.assertEqual([h["eval"]["j"] for h in result["hits"]], ["0", "1", "2"])
        self.assertEqual(result["skipped_repeat_stops"], 0)

    def test_max_hits_limits_records(self):
        with tempfile.TemporaryDirectory() as d:
            result = run_probe(Path(d), TARGET, [{"line": LINE_LOOP_BODY, "eval": ["j"], "max_hits": 1}])
        self.assertEqual([h["eval"]["j"] for h in result["hits"]], ["0"])

    def test_locals_and_failed_eval(self):
        with tempfile.TemporaryDirectory() as d:
            result = run_probe(
                Path(d), TARGET, [{"line": LINE_MULTILINE_CALL, "eval": ["undefined_name"], "max_hits": 1}]
            )
        hit = result["hits"][0]
        self.assertEqual(hit["locals"]["x"], "0")
        self.assertTrue(hit["eval"]["undefined_name"].startswith("ERROR"))

    def test_uncaught_exception_and_trigger(self):
        with tempfile.TemporaryDirectory() as d:
            result = run_probe(Path(d), RAISING, [], "--trigger", "echo triggered")
        self.assertEqual(len(result["exceptions"]), 1)
        self.assertIn("bad value: 42", result["exceptions"][0]["exception"]["description"])
        self.assertEqual(result["trigger"]["returncode"], 0)
        self.assertIn("triggered", result["trigger"]["output"])


if __name__ == "__main__":
    sys.exit(unittest.main(verbosity=2))
