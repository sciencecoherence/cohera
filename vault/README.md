# Cohera Vault

Recovery snapshots are stored here.

## Automation
- Script: `/home/xavier/cohera-repo/scripts/vault_snapshot.sh`
- Cron installer: `/home/xavier/cohera-repo/scripts/install_vault_snapshot_cron.sh`
- Default schedule: daily at `03:17` local time

## Snapshot guarantees
Each snapshot folder contains:
- `manifest.json` (file list, sizes, mtimes)
- `checksums.txt` (sha256 for all files)

## Retention
To prevent repo bloat, only the newest **10** snapshot directories are kept.
Older `snapshot-*` / `bootstrap-*` directories are pruned automatically.
