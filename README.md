# dap-probe 🔍💅

**English** | [日本語](README.ja.md)

This command drives debugpy over the Debug Adapter Protocol (DAP) and records the values at breakpoint hits as JSON 💖✨  
Instead of stopping manually in your editor, it records the stack, local variables, and the results of the expressions you asked for, then keeps going 🏃‍♀️💨

## 🛍️ Requirements

- Python 3
- `debugpy` installed in the target Python environment. If it isn't there, pass its location with `--debugpy-dir` 📁

## 📦 Install

```sh
install -m 755 dap-probe ~/.local/bin/dap-probe
```

## 🎀 Usage

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

After `--`, write the command you'd use to start the app without debugpy 🚀  
`--trigger` is a command that runs after the breakpoints are set, and `--wait-port` is the TCP port it waits to open before running that command ⏳  
The options and recording caveats are written at the top of `dap-probe` 📝

## 🧪 Tests

```sh
pip install debugpy
python3 tests/test_dap_probe.py
```

## 📜 License

MIT 💖
