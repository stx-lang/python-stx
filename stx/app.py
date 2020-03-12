import os
import threading
import time

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from stx import logger
from stx.compiling.compiler import compile_document
from stx.document import Document
from stx.outputs import registry, OutputFile, OutputAction
from stx.utils.files import resolve_sibling
from stx.utils.debug import see


def read_version() -> str:
    version_file = resolve_sibling(__file__, '../version.txt')

    with open(version_file, 'r') as f:
        return f.read().strip()


version = read_version()  # TODO parse version
name = 'STX'
title = f'{name} {version}'


def process_file(input_file: str) -> Document:
    logger.info(f'Processing file {see(input_file)}...')

    document = compile_document(input_file)

    if len(document.actions) == 0:
        logger.warning('No actions were registered.')
    else:
        for action in document.actions:
            action.run()

    return document


def watch_file(input_file: str):
    ignored_files = set()

    def refresh():
        document = process_file(input_file)

        ignored_files.clear()

        for action in document.actions:
            if (isinstance(action, OutputAction)
                    and isinstance(action.target, OutputFile)):
                ignored_files.add(
                    os.path.abspath(action.target.file_path)
                )

    class Handler(FileSystemEventHandler):

        def __init__(self):
            self.lock = threading.Lock()

        def on_any_event(self, event: FileSystemEvent):
            if event.is_directory:
                return

            with self.lock:
                src_file = os.path.abspath(event.src_path)

                if src_file not in ignored_files:
                    logger.info(f'Detected change on: {src_file}')

                    refresh()

    refresh()

    root_dir = os.path.dirname(input_file)

    logger.info(f'Watching directory {see(root_dir)} for changes...')

    observer = Observer()
    observer.schedule(Handler(), root_dir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Stopping watch...')
        observer.stop()
    observer.join()


def main(input_file: str, watch_mode=False):
    input_file = os.path.abspath(input_file)

    if watch_mode:
        watch_file(input_file)
    else:
        process_file(input_file)
