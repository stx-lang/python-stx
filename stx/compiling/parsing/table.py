from abc import ABC

from stx.compiling.reading.location import Location
from stx.components import Table, TableRow
from stx.compiling.marks import table_cell_mark
from stx.compiling.parsing.abstract import AbstractParser


class TableParser(AbstractParser, ABC):

    def parse_table_row(
            self,
            location: Location,
            indentation: int,
            header: bool):
        table = self.composer.get_last_component()

        if not isinstance(table, Table):
            table = Table(location)

            self.composer.add(table)

        row = TableRow(location, header)

        table.rows.append(row)

        self.parse_table_cell(location, indentation)

    def parse_table_cell(
            self,
            location: Location,
            indentation: int):
        table = self.composer.get_last_component()

        if not isinstance(table, Table):
            table = Table(location)

            self.composer.add(table)

        row = table.get_last_row()

        if row is None:
            row = TableRow(location, False)

            table.rows.append(row)

        indentation0 = indentation

        while True:
            with self.using_stop_char(table_cell_mark):
                cell = self.capture_component(indentation, True)

                row.cells.append(cell)

                # TODO this is weird maybe None content should be supported
                if self.active():
                    # TODO ensure that is from the same content
                    self.get_content().skip_empty_line()

            if not self.active():
                break

            content = self.get_content()

            with content.checkout() as trx:
                # Consume indentation when it is the beginning of the line
                if content.column == 0:
                    if content.read_spaces(indentation0) < indentation0:
                        trx.cancel()
                        break

                if content.peek() == table_cell_mark:
                    content.move_next()
                    content.read_spaces()

                    indentation = content.column
                    trx.save()
                else:
                    break
