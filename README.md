# Backup

Being a programmer, I hate to create backups in a drag-and-drop way. Frequently switching Macs and between Fedora and Xubuntu made creating backups and recovery a pain, especially when i wanted only very specific files/directories to be backed up. `Backup` is a programmatic way to create and recover backups from location A to location B and back. Locations can be host volumes or external volumes and can be completely controlled by the config `backupOptions.json` file.

## Usage
Run help:
```
$: python backupCreator.py --help
```

### Creating a backup
Run as `sudo` for most cases, and pass `--create` or `-c`:
```bash
$: sudo python backupCreator.py --create
# or
$: sudo python backupCreator.py -c
```

### Recovering from the same backup device
Run as `sudo` for most cases, and pass `--recover` or `-r`:
```bash
$: sudo python backupCreator.py --recover
# or
$: sudo python backupCreator.py -r
```

## Minimum compatibility
- Python 2.6+

:shipit:
