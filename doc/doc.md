<style>
table th:nth-of-type(1) {
    width:160px;
}
</style>

# PGdist - PostgreSQL projects control system



| Configuration files | Descriptions |
| --- | --- |
| [develop config file](develop/config.md) | contains info about PGCONN to testing database |
| [distribution config file](distribution/config.md) | contains info about connection to database and paths to passwords and installation scripts |
| [project config file](project_files/config.md) | contains info about project |
| [project version file](project_files/version.md) | contains info and scripts of project version |
| [project update file](project_files/update.md) | contains info and scripts of update from one version to another |



| Develop commands | Description |
| --- | --- |
| [--options](develop/cmd/options.md) | options used with dev. commands |
| [init](develop/cmd/init.md) | initiates PGdist project |
| [create-schema](develop/cmd/create-schema.md) | creates default directory structure |
| [status](develop/cmd/status.md) | shows status of project |
| [add](develop/cmd/add.md) | adds files to project |
| [rm](develop/cmd/rm.md) | removes files from project |
| [test-load](develop/cmd/test-load.md) | loads project to test database |
| [create-version](develop/cmd/create-version.md) | creates version from project |
| [create-update](develop/cmd/create-update.md) | creates update from project |
| [part-update-add](develop/cmd/part-update-add.md) | adds update part |
| [part-update-rm](develop/cmd/part-update-rm.md) | removes update part |
| [test-update](develop/cmd/test-update.md) | loads update to test database |
| [diff-db](develop/cmd/diff-db.md) | shows diffrence between project and database |
| [diff-db-file](develop/cmd/diff-db-file.md) | shows diffrence between database and file |
| [diff-file-db](develop/cmd/diff-file-db.md) | shows diffrence between file and database |
| [role-list](develop/cmd/role-list.md) | shows roles defined in project |
| [role-add](develop/cmd/role-add.md) | adds role to project |
| [role-change](develop/cmd/role-change.md) | changes role in project |
| [role-rm](develop/cmd/role-rm.md) | removes role from project |
| [require-add](develop/cmd/require-add.md) | adds require to another project |
| [require-rm](develop/cmd/require-rm.md) | removes require to another project |
| [dbparam-set](develop/cmd/dbparam-set.md) | sets parameters for creating database |
| [dbparam-get](develop/cmd/dbparam-get.md) | shows parameters for creating database |
| [data-add](develop/cmd/data-add.md) | adds data for comparing |
| [data-rm](develop/cmd/data-rm.md) | removes data from comparing |
| [data-list](develop/cmd/data-list.md) | shows data for comparing |



| Distribution commands | Description |
| --- | --- |
| [--options](distribution/cmd/options.md) | options used with dist. commands |
| [list](distribution/cmd/list.md) | shows available and installed projects |
| [install](distribution/cmd/install.md) | installs project to database |
| [check-update](distribution/cmd/check-update.md) | shows available updates |
| [update](distribution/cmd/update.md) | updates project in database |
| [clean](distribution/cmd/clean.md) | clears PGdist history of project in database |
| [set-version](distribution/cmd/set-version.md) | sets version of project in PGdist history |
| [get-version](distribution/cmd/get-version.md) | shows version of project from PGdist history |
| [pgdist-update](distribution/cmd/pgdist-update.md) | updates PGdist |
| [log](distribution/cmd/log.md) | shows history of PGdist actions |



## Authors

* Marian Krucina LinuxBox.cz

* Tadeáš Popov https://github.com/TadeasPopov

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE (Version 2) - see the COPYING file for details
