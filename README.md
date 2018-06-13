# abb_bulk_migrator
Broadband Acquisitions Migrator

Takes a CSV from STDIN and prints results to STDOUT

Calls aBB API (URL in Script)

## Usage
For Mac / Linux users:
```bash
$ ./migrator.py < test.csv
```

For Windows + Powershell users:
```bash
$ Get-Content test.csv | python migrator.py
```