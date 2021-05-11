Release History
===============
1.5.1 (2021-05-11)
-----------------
- Bugfix for nodes.iter_builds

1.5 (2021-04-29)
-----------------
- Add methods to get parameters and causes for `Build` and `QueueItem`
- Add methods to manage jcasc
- Add help functions

1.4 (2021-03-31)
-----------------
- Support to retrieve test report for build
- Support to validate Jenkinsfile

1.3 (2021-02-28)
-----------------
- Add capability to get/save artifacts for `WorkflowRun`.
- Make `Jenkins` and `Folder` is subscribed and can be iterated with depth.
- Refactor some code.

1.2 (2021-01-31)
----------------
- Support to enable, disable, scan, get_scan_log for `WorkflowMultiBranchProject`
- Call `Jenkins.get_job` for getting parent of `Job`
- Support process input step for `WorkflowRun`,  see `WorkflowRun.get_pending_input()`
- Support user management

1.1 (2020-12-31)
-----------------
- Rewrite documentation and add more examples
- `Jenkins.build_job()` and `Project.build()` accept key word argments instead of dict
- Support to access attribute with None type value in json
- Fix typo in `Folder.__iter__()`

1.0 (2020-11-15)
------------------
- First release

