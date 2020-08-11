# PGdist - PostgreSQL projects control system

## Description
Let me introduce our project PGdist, used for PostgreSQL projects management from development to production.
URL: https://github.com/linuxbox-cz/pgdist

PGdist can:
- manage source files, collaborating with Git
- test project installation in PostgreSQL
- help to create update scripts and test it for mistakes
- display project‘s diff and existing database structure
- watch for proper role creation in database
- allow dependency settings
- compare data in tables
- make installations and updates on production server (inc. roles, dependencies)
- allow to split install and update scripts to parts, intended to be or not to be done in particular transaction
- show diffs in structured and colored mode

PGdist requires:
- PostgreSQL
- Git

The main motivation was standardization of many projects in PostgreSQL.  
PGdist will help us to create new version and its rpm package.  
On the other hand, it will install or update the project from rpm on production server.  
PGdist also can compare very old installation (and possible hand-made changes) and help us to prepare update script to standard version.  
PGdist also requires a little bit of **DIY - do it yourself**.  

**Develop part** - It is for usage on local computer. It cooperates with git.  

**Distribution part** - It is for usage on production server.

[**Tutorial**](doc/tutorial.md)

## Authors

* Marian Krucina LinuxBox.cz

* Tadeáš Popov https://github.com/TadeasPopov

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE (Version 2) - see the COPYING file for details
