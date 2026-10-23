#!/usr/bin/env python3
"""Timestamp every evidence file in this repo with OpenTimestamps (Bitcoin).

For each file under data/ and analysis/ (and MANIFEST.sha256):
  * no .ots proof yet            -> `ots stamp` it (proof saved as <file>.ots)
  * proof exists, file unchanged -> leave it
  * proof exists, file changed   -> keep the old proof as <file>.ots.superseded-<UTC date>,
                                    then stamp the new version
Then run `ots upgrade` on every proof so pending calendar attestations become
full Bitcoin block attestations once the anchoring transaction confirms (a few hours).

Run by .github/workflows/opentimestamps.yml; can also be run locally.
"""
import datetime
import hashlib
import pathlib
import subprocess
import sys

from opentimestamps.core.serialize import StreamDeserializationContext
from opentimestamps.core.timestamp import DetachedTimestampFile

ROOT = pathlib.Path(__file__).resolve().parent.parent
EVIDENCE_DIRS = ["data", "analysis"]
SKIP_SUFFIXES = (".ots",)


def evidence_files():
    files = []
    for d in EVIDENCE_DIRS:
        for p in sorted((ROOT / d).rglob("*")):
            if p.is_file() and not p.name.endswith(SKIP_SUFFIXES) and ".ots.superseded-" not in p.name:
                files.append(p)
    return files


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def write_manifest(files):
    lines = [f"{sha256(p)}  {p.relative_to(ROOT).as_posix()}" for p in files]
    (ROOT / "MANIFEST.sha256").write_text("\n".join(lines) + "\n")


def proof_digest(ots_path):
    with open(ots_path, "rb") as f:
        dtf = DetachedTimestampFile.deserialize(StreamDeserializationContext(f))
    return dtf.file_digest.hex()


def main():
    files = evidence_files()
    write_manifest(files)
    targets = files + [ROOT / "MANIFEST.sha256"]
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    to_stamp = []
    for p in targets:
        proof = p.with_name(p.name + ".ots")
        if not proof.exists():
            to_stamp.append(p)
        elif proof_digest(proof) != sha256(p):
            proof.rename(p.with_name(f"{p.name}.ots.superseded-{today}"))
            to_stamp.append(p)

    if to_stamp:
        print("Stamping:", *[p.relative_to(ROOT).as_posix() for p in to_stamp], sep="\n  ")
        subprocess.run(["ots", "stamp", *map(str, to_stamp)], check=True)

    proofs = sorted(ROOT.glob("**/*.ots"))
    for proof in proofs:
        # Exit status is non-zero while the attestation is still pending; that is expected.
        r = subprocess.run(["ots", "upgrade", str(proof)], capture_output=True, text=True)
        status = "complete" if r.returncode == 0 else "pending"
        print(f"{status:8} {proof.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
