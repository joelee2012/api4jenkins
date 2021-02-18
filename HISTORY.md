Release History
===============
1.3 (2021-02-28)
-----------------
- Support save artifacts as zip or only one file.
- Support pythonic way to iterate jenkins and folder with depth.

1.2 (2021-01-31)
----------------
- Support to enable, disable, scan, get_scan_log for `WorkflowMultiBranchProject`
- Call `Jenkins.get_job` for getting parent of `Job`
- Support process input step for WorkflowRun,  see `WorkflowRun.get_pending_input()`
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

