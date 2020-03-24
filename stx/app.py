import os
import threading
import time
import click
import pkg_resources

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from stx import logger
from stx.compiling.compiler import compile_document
from stx.document import Document
from stx.outputs import OutputFile, OutputAction
from stx.utils.debug import see

app_name = 'stx'
app_version = pkg_resources.require(app_name)[0].version
app_title = f'{app_name} {app_version}'


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
        try:
            document = process_file(input_file)

            ignored_files.clear()

            for action in document.actions:
                if (isinstance(action, OutputAction)
                        and isinstance(action.target, OutputFile)):
                    ignored_files.add(
                        os.path.abspath(action.target.file_path)
                    )
        except Exception as e:
            print(e)

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


def main(input_file: str, watch_mode=False, version=False):
    if version:
        print(app_title)

    input_file = os.path.abspath(input_file)

    if watch_mode:
        watch_file(input_file)
    else:
        process_file(input_file)


@click.command(name='stx')
@click.argument('input_file')
@click.option(
    '-w', '--watch', help='Watches the document for changes.',
    is_flag=True, default=False)
@click.option(
    '-v', '--version', help='Shows the STX version.',
    is_flag=True, default=False)
def cli(input_file: str, watch: bool, version: bool):
    """Processes the STX document indicated by INPUT_FILE."""
    main(input_file, watch, version)
