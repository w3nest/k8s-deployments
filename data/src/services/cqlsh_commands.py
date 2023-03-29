import datetime
import subprocess
from pathlib import Path

from services.reporting.reporting import Report


class CqlInstance:

    def __init__(self, host: str):
        self._host = host

    def get_host(self):
        return self._host


class CqlshCommands:

    def __init__(self, report: Report, cqlsh: str, instance: CqlInstance):
        self._report = report.get_sub_report("CqlshCommands", init_status="InitializingComponent")
        self._cqlsh = cqlsh.split(" ")
        self._instance = instance
        self._report.debug(f"using instance {instance.get_host()}")

    def backup_ddl(self, keyspace: str, path_file: Path):
        report = self._report.get_sub_report(f"backup_ddl_{keyspace}", init_status="in function")
        report.debug(f"will store ddl in {path_file}")
        code, out, err = self.run_command(report, f"DESCRIBE {keyspace};")
        if code == 0:
            path_file.write_text(out)
            report.set_status("Done")
        else:
            raise RuntimeError(f"Failure: {err}")

    def backup_table(self, table: str, path_file: Path):
        report = self._report.get_sub_report(f"backup_table_{table}", init_status="in function")
        report.debug(f"will store table data in {path_file}")
        total = self.count_table(report, table)

        count = 0

        last_message_timestamp = datetime.datetime.now().timestamp()
        out = ""

        def on_line(line: str):
            now = datetime.datetime.now().timestamp()
            nonlocal last_message_timestamp
            nonlocal count
            nonlocal out
            count = count + 1
            out = f"{out}{line}"
            if (now - last_message_timestamp) > 1:
                last_message_timestamp = now
                report.debug(f"Copied {count} / {total} lines ")

        self.run_command_with_handler(report, f"COPY {table} TO STDOUT;", on_line=on_line)
        if count != total:
            raise RuntimeError(f"Wrong count of rows : expected {total}, got {count}")
        path_file.write_text(out)
        report.set_status("Done")

    def count_table(self, report: Report, table: str) -> int:
        report = report.get_sub_report("_count_table", init_status="in function")
        report.debug(f"table={table}")
        code, out, err = self.run_command(report, f"SELECT count(*) FROM {table}")
        if code == 0:
            lines = out.splitlines()
            report.debug(f"lines={lines}")
            count_str = lines[3].strip()
            return int(count_str)
        else:
            raise RuntimeError(f"Failure: {err}")

    def run_command(self, report: Report, cql: str):
        report = report.get_sub_report("_run_command", init_status="in function")
        report.debug(f"cql='{cql}'")
        result = subprocess.run([*self._cqlsh, self._instance.get_host(), "-e", cql],
                                capture_output=True, text=True)
        report.debug(f"return_code={result.returncode}")
        report.debug(f"out={result.stdout}")
        report.debug(f"err={result.stderr}")
        return result.returncode, result.stdout, result.stderr,

    def run_command_with_handler(self, report: Report, cql: str, on_line):
        report = report.get_sub_report("_run_command_with_handler", init_status="in function")
        report.debug(f"cql={cql}")
        with subprocess.Popen([*self._cqlsh, self._instance.get_host(), "-e", cql],
                              stdout=subprocess.PIPE) as popen:
            for line in popen.stdout:
                on_line(line.decode('utf8'))

        report.set_status("exit function")
