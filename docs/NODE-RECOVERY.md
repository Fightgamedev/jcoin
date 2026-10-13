# Back up and restore a local JCoin node

This procedure is for the local test prototype only. It backs up the validator
identity and its matching ledger together. The raw validator key is not
encrypted, and the ledger contains transparent transfer history. Treat a backup
as sensitive: keep it on encrypted storage that only you can access. Do not
commit it to Git, email it, or put it in shared/cloud storage without protecting
it with your own encryption.

## Create a backup

Replace `/path/to/jcoin` below with the directory containing your checkout.

1. Stop JCoin cleanly. In the terminal opened by `JCoin.desktop` or
   `run-jcoin.sh`, press **Ctrl+C** and wait for the process to exit.
2. From the repository directory, copy the complete `node-data` directory.
   Do not copy only `jcoin.sqlite3`: SQLite may have committed data in its WAL
   files while the node is running.

```sh
cd /path/to/jcoin
umask 077
mkdir -p "$HOME/.local/backups"
cp -a node-data "$HOME/.local/backups/jcoin-node-$(date +%Y%m%d-%H%M%S)"
```

The copy should contain `jcoin.sqlite3` and `master-validator.key`. Keep those
files together. The directory and key should remain owner-only (`0700` and
`0600` on POSIX systems). Store another copy only on encrypted storage; these
permissions do not encrypt the backup or protect it from software running as
your account.

## Restore a backup

1. Stop the node cleanly and keep the backup directory unchanged.
2. From the repository directory, move the current data directory aside. This
   preserves it if the chosen backup is wrong.
3. Copy the entire backed-up `node-data` directory into the repository. Do not
   combine a database from one backup with a validator key from another.
4. Start JCoin normally. Startup checks SQLite structure, block signatures,
   transaction rules, and issuance. If validation fails, stop the node and
   preserve both directories; do not edit or delete the failed data.

```sh
cd /path/to/jcoin
mv node-data "node-data-before-restore-$(date +%Y%m%d-%H%M%S)"
cp -a "$HOME/.local/backups/jcoin-node-YYYYMMDD-HHMMSS" node-data
```

Replace `jcoin-node-YYYYMMDD-HHMMSS` with the backup directory you selected.
After startup, check the dashboard's reported chain height and balances. A
restore returns the local test ledger and validator identity to the time of the
backup; transfers made after that point are not present in the restored copy.

This guide does not provide key encryption, automatic backups, recovery from a
lost key, database repair, or migration between different validator
identities. JCoin remains test-only and must not hold real funds.
