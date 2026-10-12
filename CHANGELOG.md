# Changelog

All notable changes to marine-haris.

## [0.3.0] — 2026-08-05

### Added — snapshot payload pruning

- `prune_payload()` in `data_aggregator.py`: strips every `meta` block (static schema — description/units/formula) and every per-source `values` map from Signal K snapshots, keeping `value`/`timestamp`/`$source`/`pgn` per path.
- Sinilind N2K docs drop from ~30–160 KB to ~12 KB (~10×); ends the ES 1000-field-limit explosion (see watchtower `guides/references/es-field-limit-fix.md`). Per-frame detail remains archived in the raw CAN capture (`haris-canraw`), so nothing is lost.
- New tests: `TestPrunePayload` (meta/values stripped, value objects kept verbatim, lists walked).

## [0.2.0] — 2026-08-04

### Changed — Aggregator synced with production

- **Replaced the legacy in-process `VesselState` aggregator** (`src/data_collection/data_aggregator.py`) with the **Signal K polling collector** — the exact file deployed to vessel edge nodes (haris-arthur / haris-sinilind) via watchtower.
  - Polls the local Signal K API every N seconds (default 10), writes JSONL snapshots for Filebeat.
  - **Freshness filter** (`HARIS_MAX_SIGNAL_AGE`, default 30s): values older than the threshold are blanked (`value: null`) — stale data is *absent*, never wrong, in Elasticsearch.
  - Source-agnostic: simulator input (bench) and real NMEA 2000/CAN both feed Signal K; the collector treats them identically.
- **`src/system/harisd.service`** updated to the production unit contract: runs `data_aggregator.py` with `HARIS_VESSEL_ID`, `HARIS_SIGNALK_API_URL`, `HARIS_SNAPSHOT_INTERVAL`, `HARIS_LOG_PATH`, `HARIS_MAX_SIGNAL_AGE`, `HARIS_SOC_*` env vars (defaults shown; watchtower role renders per-node values).
- **Tests:** added `tests/test_aggregator.py` (5 tests) covering the freshness filter and event shape.
- The NMEA parsers (`nmea2000_parser.py`, `nmea0183_parser.py`, `signal_k_ingestor.py`) remain in the repo as reference — the deployed pipeline parses via Signal K.

## [0.1.0] — 2026-07

- Initial edge collector: NMEA 2000/0183 parsers + VesselState aggregator (legacy, superseded by 0.2.0).
