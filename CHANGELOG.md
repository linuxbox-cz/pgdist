## [1.2401.0.0] - 2024-01-24

### Fix
Fix: add parametr --force to install failed installations and updates

## [1.2312.0.0] - 2023-12-06

### Fix
repeat install/update failed part


## [1.2311.0.1] - 2023-11-15

### Fix
open files with utf-8 encoding


## [1.2311.0.0] - 2023-11-09

### Added
to pgdist data-add add option: exclude column
add "IF EXISTS" to generated command "DROP FUNCTION"
add command update-status

## [1.0.1] - 2022-11-23

### Fix
decode psql output, when sql fails
remove param bufsize from call subprocess.Popen - Python 3.9 yells RuntimeWarning

## [1.0.0] - 2023-11-18

### Change
python2 revrite to python3

### Added
argument JSON-output for list, check-update
added defaults to get whole command "ALTER TABLE"

### Fix
add loading new required projects to old project
default in alter function, test-update - check table data, alter enum


## [0.6.8] - 2020-02-13

### Fix
Log create new role/database when new database is created.

## [0.6.7] - 2019-12-31

### Added
add universal sql type
add type operators
