# Testing

Tests tests can be found in the ```test/``` directory. We distinguish between unit tests and system tests.

## Unit tests

A true unit test is a unit test in the classical sense. They are normally a method inside one of the the *_test.py classes. For further information see the [documentation of the python unit testing framework](https://docs.python.org/3/library/unittest.html).

## System test

This project contains a [mechanism for easy system wide unit testing](/test/system_test.py). The Idea of this is to enable users, without writing code, to submit meaningful bug reports. System tests can be found in the ```test/*_tests/``` directory. And they have the following structure:
```shell
system_tests
├── args    # Command line arguments
├── skip    # (optional) If present skip this test
├── stderr  # (optional) Expected stderr
├── stdin   # Stdin data
└── stdout  # Expected stdout
```

If the skipfile is not present each directory is assembled to a test which implements the following logic:
```shell
$ { cat stdin | pdml2flow $(cat args) 2>&3 | diff - stdout; } 3>&1 1>&2 | diff - stderr
```

Note that diff comparing stdout respects that object attributes might occur in a different order. Keep the following things in mind when writing a system unit test:

* The test should be minimal. This means your test should contain the least amount of information in order to do what you want.
* Anonymize personal data
* One test should only cover one aspect
