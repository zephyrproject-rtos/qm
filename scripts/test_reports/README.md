
# TestRail Scripts

This set of scripts helps uploading test results from Junit format to Testrail.

Install all requirements using:

```
$ pip3 install --user -r requirements.txt
```

We suggest to create a python virtual environment for this.

Export the following variables in the shell where you intend to run the script:

- TESTRAIL\_USER
- TESTRAIL\_TOKEN

The script supports the following arguments:

```
optional arguments:
  -h, --help            show this help message and exit
  --runner {tcf,sanitycheck,maxwell,autopts}
                        Select runner to import from.
  -c CONFIG, --config CONFIG
                        Configuration name.
  -V COMMIT, --commit COMMIT
                        Version being tested (git desribe string)
  -p PROJECT, --project PROJECT
                        Project ID
  -s SUITE, --suite SUITE
                        Suite ID
  -n, --dry-run         Dry run
  -m MILESTONE, --milestone MILESTONE
                        Milestone ID
  -P PLAN, --plan PLAN  Test plan ID

  -b buginfo_file, --buginfo-file buginfo_file for sanitycheck & sanitycheckbatch runner
                     points to a file containing bug info for the error/failure cases.
                     When test cases results will be uploaded into the Test Rail, the bug IDs will be auto added for the error/failure cases.
                     The file format is following:

                     [platform1 name]
                      Case1 name= bug ID
                      Case2 name= bug ID
                     [platform2 name]
                      Case1 name= bug ID

Result files (input):
  You can either select a directory with multiple files or just point to one
  file depending on the source of the results. TCF results expect a
  directory with multiple files, where sanitycheck expect 1 file per
  configuration.

  -j RESULTS_DIR, --results-dir RESULTS_DIR
                        Directory with test result files
  -f RESULTS_FILE, --results-file RESULTS_FILE
                        File with test results format.
```


To upload all Junit results from a directory produced by Sanitycheck, use the following command:

```
$ python3 report.py --runner sanitycheckbatch -j <junit dir> -V <commit_id>    -p <project id> -s <test suite> -m <milestone> -P <plan number optionally>
```

Python script for Sanitycheck and for SanitycheckBatch has useful log information, for better view of it you can follow next step.
For example, if you want to upload all Junit results from a directory, and upload bug information from a file, then see log output, you can use next command. Create empty file log.txt before run that command.

```
$ python3 report.py --runner sanitycheckbatch -j junit4TestRail -V master-2019-10-16-3d4aef8f99    -p 5 -s 52 -m 9 -b buginfo.ini>> log.txt
```

To upload one single Junit file produced by Sanitycheck, use the following command:

```
$ python3 report.py --runner sanitycheck -f <junit file> -V v1.13.0-1386-g183e7445c6.2379 -p <project id> -s <test suite> -m <milestone> -c <config name> -P <plan number optionally>
```
If you will use -P plan number (Plan ID), you can upload new results to the already created page of the Test Run in the TestRail system.
To know plan number just open page with already created Test Run and check webpage address, for example you will have 'zephyrproject.testrail.io/index.php?/plans/view/0101'
Number 0101 it is you plan number and you can use it to upload result to that Test Run. Also you can find Plan ID in the log output.
