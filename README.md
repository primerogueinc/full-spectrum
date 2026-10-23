# full-spectrum

Raw data and analysis files for **Full Spectrum**, Prime Rogue Inc.'s series on US election interference in Canadian domestic politics.

This repository holds the evidence behind the series: raw data pulled from public sources, and the analysis files that interpret it. It does not hold the published articles. Those live on [primerogueinc.com](https://primerogueinc.com).

## What's here

```
data/        Raw data, one folder per collection: YYYY-MM-DD_topic/
analysis/    Analysis files, YYYY-MM-DD_topic.md
scripts/     stamp.py, the timestamping script
MANIFEST.sha256   SHA-256 of every file in data/ and analysis/
*.ots        OpenTimestamps proofs, one beside each file
```

### `data/2026-10-22_10xvotes-azure/`

Public records on the 10X Votes app (skcn.10xvotes.com) that held Alberta voter records, and on the Centurion Project's web presence. Collected October 22, 2026.

| File | Contents |
| --- | --- |
| `crtsh/10xvotes-certificates.csv` | 145 unique TLS certificates for `*.10xvotes.com` from crt.sh, precertificate duplicates removed. Each row links to its crt.sh record. |
| `crtsh/centurion-domains-summary.csv` | Certificate counts and first issuance for Centurion-related domains |
| `dns/dns-resolutions-10xvotes.csv` | DNS answers for 10xvotes.com hosts via Google Public DNS, 2026-10-22, about 09:30–10:30 UTC, including Azure `asuid` verification records |
| `dns/dns-resolutions-centurion.csv` | DNS answers for Centurion-related domains, same session |
| `wayback/cdx-10xvotes.com.csv` | Internet Archive CDX index for 10xvotes.com and all subdomains |
| `wayback/cdx-thecenturionproject.ca.csv` | Internet Archive CDX index for thecenturionproject.ca. Wix platform bundle files are omitted. Ticket-order and email-campaign URLs are redacted because they contained attendees' order numbers, reservation IDs and signed tokens. |
| `wayback/key-captures.csv` | The archived pages relied on in the analysis, with direct capture links |
| `workbook/10xvotes-phase2-evidence.xlsx` | The same data as one workbook, with a per-host summary |

Analysis: [`analysis/2026-10-22_10xvotes-centurion-infrastructure-phase2.md`](analysis/2026-10-22_10xvotes-centurion-infrastructure-phase2.md)

## How this was collected

Passive and public only. No 10X Votes or Centurion server was contacted, no account was created, and no voter data was viewed or downloaded. Sources: crt.sh certificate transparency logs, Google Public DNS, and the Internet Archive's Wayback Machine. Live DNS can change after collection; the files record what the resolvers returned at the time stated.

## Blockchain timestamps

Every file in `data/` and `analysis/`, plus `MANIFEST.sha256`, carries an [OpenTimestamps](https://opentimestamps.org) proof (`<file>.ots`). The proof commits the file's SHA-256 hash to the Bitcoin blockchain. That shows the exact file existed no later than the Bitcoin block that anchors it, and that it has not changed since.

The [OpenTimestamps workflow](.github/workflows/opentimestamps.yml) runs on every push that touches evidence, and every six hours:

1. New files are stamped.
2. A file that changes keeps its old proof, renamed `<file>.ots.superseded-<date>`, and gets a new one. Earlier versions stay provable through git history.
3. Pending proofs are upgraded to full Bitcoin attestations once the anchoring transaction confirms, usually within a few hours.

To verify a file yourself:

```
pip install opentimestamps-client
ots verify data/2026-10-22_10xvotes-azure/crtsh/10xvotes-certificates.csv.ots
```

`ots verify` needs a Bitcoin node or uses a public block explorer. For a no-install check, upload the file and its `.ots` at [opentimestamps.org](https://opentimestamps.org).

## Corrections

When a finding changes, the analysis file is updated and its timestamp history shows when. The 2026-10-22 analysis corrects an earlier Prime Rogue analysis on three points (Cloudflare proxying, Vercel hosting, and the "skcn = Saskatchewan" reading); see its "Corrections to Phase 1" section.

## License

MIT, see [LICENSE](LICENSE). Third-party records (certificate logs, DNS answers, archive indexes) are public data reproduced for verification.
