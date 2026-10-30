from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import date
from pathlib import Path

SOURCE_URL = "https://adrenoleukodystrophy.info/mutations-and-variants-in-abcd1"


def fetch_registry_snapshot(destination: str | Path, timeout: int = 30) -> dict:
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "ABCD1-research-pipeline/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read()
        final_url = response.geturl()
        status = response.status
        content_type = response.headers.get_content_type()
    destination.write_bytes(raw)
    checksum = hashlib.sha256(raw).hexdigest()
    metadata = {
        "source_url": SOURCE_URL,
        "final_url": final_url,
        "http_status": status,
        "content_type": content_type,
        "snapshot_date": date.today().isoformat(),
        "sha256": checksum,
        "raw_path": str(destination),
        "variant_records_verified": False,
        "note": "HTML metadata snapshot only; registry variant rows must not be inferred without verified structured export.",
    }
    destination.with_suffix(destination.suffix + ".json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return metadata
