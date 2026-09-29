"""
Jal Taranga — Production Cloud Runner
Ensures port resolution, immediate unbuffered logs, and clean server binding.
"""
import os
import sys
from pathlib import Path

# Force unbuffered standard output for instant cloud logging
os.environ["PYTHONUNBUFFERED"] = "1"

# Add backend directory to sys.path so 'app' package is always resolvable
root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import uvicorn

if __name__ == "__main__":
    raw_port = os.environ.get("PORT", "8000")
    try:
        port = int(raw_port)
    except ValueError:
        port = 8000

    host = "0.0.0.0"
    print("==================================================", flush=True)
    print("  Jal Taranga Geospatial Platform (All-India Core)", flush=True)
    print(f"  Binding to {host}:{port}", flush=True)
    print("==================================================", flush=True)

    uvicorn.run(
        "backend.app.main:app",
        host=host,
        port=port,
        log_level="info",
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
