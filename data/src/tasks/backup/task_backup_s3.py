from pathlib import Path

from services.mc_commands import McCommands
from services.reporting import Report


class TaskBackupS3:
    RELATIVE_PATH = "minio"

    def __init__(self, report: Report, path_work_dir: Path, mc_commands: McCommands, buckets: [str]):
        self._path_work_dir = path_work_dir
        self._report = report.get_sub_report("BackupS3", default_status_level="NOTIFY",
                                             init_status="ComponentInitialized")
        self._mc_commands = mc_commands
        self._buckets = buckets

    def run(self):
        mc_commands = self._mc_commands
        self._report.debug(f"buckets={self._buckets}")

        for bucket in self._buckets:
            bucket_report = self._report.get_sub_report(f"backup_minio_{bucket}", default_status_level="NOTIFY")
            mc_commands.set_reporter(bucket_report)
            mc_commands.backup_bucket(bucket)
            bucket_report.set_status("Done")

        mc_commands.set_reporter(self._report)
        mc_commands.stop_local()

    def task_path_dir_and_archive_item(self):
        result = self._path_work_dir / TaskBackupS3.RELATIVE_PATH
        if not result.exists():
            result.mkdir(parents=True)

        if not result.is_dir():
            raise RuntimeError(f"path '{result}' is not a directory")

        return result, TaskBackupS3.RELATIVE_PATH
