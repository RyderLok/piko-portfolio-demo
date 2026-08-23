Piko — Catch a sound. Make a world.

Portfolio demo of an interactive sound-to-brush toy: collect a field recording, turn it into a visual brush, and draw on a shared plate.

This public clone runs in DEMO_MODE by default. It does not need API keys, a database, ESP32 hardware, or production servers.

> This is a portfolio demo repository. It contains selected code and mock data only. Production services, API credentials, original design assets, and private data are not included.

## Highlights

- Hardware-inspired Collect → New Sounds → Transform → Draw flow (Piko visual language)
- Local acoustic features drive brush size, density, and motion
- Semantic category in demo is a **local simulation** (not Qwen)
- Sample library + plate drawing work without a recorder

## What is simulated

| Capability | Demo (`DEMO_MODE=true`) | Production (private) |
| --- | --- | --- |
| Sound category (Qwen / SiliconFlow) | Local 5-class heuristic | Server-side API with env key |
| Cloud sound store (Supabase) | Local `python-service/sounds/` | Service role on the server only |
| ESP32 field recorder | Bundled synthetic clips + optional laptop mic | INMP441 + USB/Wi-Fi bridge |
| High-res design sources | Not in this repo | Private |

The UI still runs the real brush / canvas pipeline on mock or mic audio.

## Requirements

- Python 3.11+
- A current desktop browser (Chrome / Edge / Safari)

ESP32, Node serial bridge, iPad app, and cloud accounts are **optional** and not required for the portfolio walkthrough.

## Start (demo)

```bash
cd piko-portfolio-demo
./start-demo.sh
```

Then open http://127.0.0.1:8000

Manual equivalent:

```bash
cd python-service
python3 -m venv .venv-demo
source .venv-demo/bin/activate   # Windows: .venv-demo\Scripts\activate
pip install -r requirements.txt
export DEMO_MODE=true            # Windows: set DEMO_MODE=true
python -m uvicorn app:app --host 127.0.0.1 --port 8001
```

In another terminal:

```bash
cd web-demo
python3 -m http.server 8000
```

Health check: http://127.0.0.1:8001/health should include `"demoMode": true`.

## Screenshots / live demo

Run the commands above and walk Collect → Input → Transform → Draw in the browser. Optional live URL, PDF, and video links can be added here when published separately (this repo does not host production backends or GitHub Pages).

## Walkthrough

1. Collect — tap **Input**. Transfer animation uses bundled demo clips (no recorder).
2. New Sounds — pick 1–5 samples, Next.
3. Transform — wait for the local analysis (simulated category + real acoustics).
4. Draw — paint with the generated brush.

Optional: if a record UI is available, the laptop mic is used instead of ESP32. That is labeled as a demo substitute.

## Production is not in this repository

Do not put real keys in the browser or in git.

- Copy `python-service/.env.example` → `.env` only on a private machine
- Set `DEMO_MODE=false` only when SiliconFlow / Supabase env vars are present
- Frontend never receives `SILICONFLOW_API_KEY` or Supabase `service_role`

## Links (add yours before publishing)

- Live demo: _TBD_
- Portfolio PDF: _TBD_
- Video walkthrough: _TBD_

## License

Code and design assets in this demo are for portfolio display. See `LICENSE`.
See `SECURITY.md` to report issues privately.
