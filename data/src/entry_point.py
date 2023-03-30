import sys


def main(task: str):
    if task == "backup":
        from tasks import get_task_backup_builder
        get_task_backup_builder()().run()
    elif task == "setup_backup":
        from tasks import get_task_setup_backup_builder
        get_task_setup_backup_builder()().run()
    else:
        raise RuntimeError(f"Unknown task {task}")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise RuntimeError("entry_point.py expect exactly one argument")
    arg = sys.argv[1]
    main(arg)
