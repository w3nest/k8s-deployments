from enum import Enum
from pathlib import Path

from services.cqlsh_commands import CqlshCommands


class OnPathDirMissing(Enum):
    CREATE = "create"
    ERROR = "error"


class TaskCassandra:
    RELATIVE_PATH = "cql"
    RELATIVE_PATH_SCHEMA = "cql/schema"
    RELATIVE_PATH_DATA = "cql/data"

    def __init__(self,
                 path_work_dir: Path,
                 cqlsh_commands: CqlshCommands,
                 keyspaces: [str],
                 tables: [str]):
        self._path_work_dir = path_work_dir
        self._cqlsh_commands = cqlsh_commands
        self._keyspaces = keyspaces
        self._tables = tables

    def run(self):
        raise NotImplementedError("Abstract class")

    def _task_path_dir_and_archive_item(self, on_missing: OnPathDirMissing):
        return self.__path_dir_maybe_exists(TaskCassandra.RELATIVE_PATH,
                                            on_missing=on_missing), TaskCassandra.RELATIVE_PATH

    def _path_cql_ddl_dir(self, on_missing: OnPathDirMissing):
        return self.__path_dir_maybe_exists(TaskCassandra.RELATIVE_PATH_SCHEMA, on_missing=on_missing)

    def _path_cql_data_dir(self, on_missing: OnPathDirMissing):
        return self.__path_dir_maybe_exists(TaskCassandra.RELATIVE_PATH_DATA, on_missing=on_missing)

    def __path_dir_maybe_exists(self, relative_path: str, on_missing: OnPathDirMissing) -> Path:
        path = self._path_work_dir / relative_path
        if not path.exists():
            if on_missing == OnPathDirMissing.ERROR:
                raise RuntimeError(f"path {path} does not exist")
            elif on_missing == OnPathDirMissing.CREATE:
                path.mkdir(parents=True)

        if not path.is_dir():
            raise RuntimeError(f"path '{path}' is not a directory")

        return path
