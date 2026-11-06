# dap-probe 🔍💅

[English](README.md) | **日本語**

debugpy を Debug Adapter Protocol (DAP) で操作して、ブレークポイントで止まったときの値を JSON に記録しちゃうコマンドだよ💖✨  
エディタで手で止める代わりに、スタック、ローカル変数、指定した式の評価結果を記録して、そのまま続行してくれるよ🏃‍♀️💨

## 🛍️ 必要なもの

- Python 3
- 対象の Python 環境に入った `debugpy`。入ってないときは `--debugpy-dir` で場所を教えてね📁

## 📦 導入

```sh
install -m 755 dap-probe ~/.local/bin/dap-probe
```

## 🎀 使い方

```sh
cat > spec.json <<'JSON'
{"breakpoints": [{"file": "/abs/path/app.py", "line": 120, "condition": "x > 1",
                  "eval": ["len(rows)"], "max_hits": 3}],
 "exceptions": ["uncaught"]}
JSON

dap-probe --spec spec.json --out probe.json \
  --wait-port 127.0.0.1:8000 --trigger 'curl -s http://127.0.0.1:8000/health' \
  -- .venv/bin/python -m uvicorn main:app --port 8000
```

`--` の後ろには、debugpy を使わないときの起動コマンドを書いてね🚀  
`--trigger` はブレークポイントを設定したあとに実行するコマンドで、`--wait-port` はそのコマンドの前に開くのを待つ TCP ポートだよ⏳  
オプションと記録の注意点は `dap-probe` の冒頭に書いてあるよ📝

## 🧪 テスト

```sh
pip install debugpy
python3 tests/test_dap_probe.py
```

## 📜 ライセンス

MIT 💖
