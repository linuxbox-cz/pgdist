### Test

Requires:
* local PostgreSQL
* git
* PGdist
* access to test database default postgres@/pgdist (schema will be created by installing pgdist or running test)
* access to v3a lbadmin database

```
./test.sh -h
Optional parameters:
    -u --user     git user name
    -e --email    git user email
    -p --pgconn   pg connection (PGCONN) defautl postgres@/
    --no-clean    wont clean files and database after test
    -h --help     prints this help
```

Functionality:

./test.sh
* variables setup
* test_devel_1.sh 
	* tests commands from PGdist Devel section
	* if git user and email is set, test require-add
* test_devel_2.sh
	* tests commands from PGdist Devel section
	* changes files and adds new files
	* create-update
* test_server.sh
	* tests commands from PGdist Server section
