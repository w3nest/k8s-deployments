from pathlib import Path

from services.cqlsh_commands import CqlshCommands
from services.reporting.reporting import Report


class TaskBackupCassandra:
    RELATIVE_PATH = "cql"

    def __init__(self, report: Report,
                 path_work_dir: Path,
                 cqlsh_commands: CqlshCommands,
                 keyspaces: [str],
                 tables: [str]):
        self._report = report.get_sub_report("BackupCassandra", default_status_level="NOTIFY",
                                             init_status="ComponentInitialized")
        self._path_work_dir = path_work_dir
        self._cqlsh_commands = cqlsh_commands
        self._keyspaces = keyspaces
        self._tables = tables

    def run(self):
        self._report.set_status("Running")
        cqlsh_commands = self._cqlsh_commands
        path_task_work_dir, _ = self.task_path_dir_and_archive_item()
        self._report.debug(f"keyspaces={self._keyspaces}")
        path_cql_ddl_dir = (path_task_work_dir / "schema")
        path_cql_ddl_dir.mkdir(parents=True)

        for keyspace in self._keyspaces:
            keyspace_report = self._report.get_sub_report(f"backup_ddl_{keyspace}", default_status_level="NOTIFY")
            path_file = path_cql_ddl_dir / f"{keyspace}.cql"
            cqlsh_commands.backup_ddl(keyspace, path_file)
            keyspace_report.set_status("Done")

        path_cql_data_dir = (path_task_work_dir / "data")
        path_cql_data_dir.mkdir(parents=True)

        for table in self._tables:
            table_report = self._report.get_sub_report(f"backup_table_{table}", default_status_level="NOTIFY")
            path_file = path_cql_data_dir / f"{table}.csv"
            cqlsh_commands.backup_table(table, path_file)
            table_report.set_status("Done")

        self._report.set_status("Done")

    def task_path_dir_and_archive_item(self):
        result = self._path_work_dir / TaskBackupCassandra.RELATIVE_PATH
        if not result.exists():
            result.mkdir(parents=True)

        if not result.is_dir():
            raise RuntimeError(f"path '{result}' is not a directory")

        return result, TaskBackupCassandra.RELATIVE_PATH
