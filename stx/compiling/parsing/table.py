from abc import ABC

from stx.components import Table, TableRow
from stx.compiling.marks import table_cell_mark
from stx.compiling.parsing.abstract import AbstractParser


class TableParser(AbstractParser, ABC):

    def parse_table_row(
            self,
            indentation: int,
            header: bool):
        table = self.composer.get_last_component()

        if not isinstance(table, Table):
            table = Table([])

            self.composer.add(table)

        row = TableRow([], header)

        table.rows.append(row)

        self.parse_table_cell(indentation)

    def parse_table_cell(
            self,
            indentation: int):
        table = self.composer.get_last_component()

        if not isinstance(table, Table):
            table = Table([])

            self.composer.add(table)

        row = table.get_last_row()

        if row is None:
            row = TableRow([], False)

            table.rows.append(row)

        self.stop_mark = table_cell_mark

        cell = self.capture_component(indentation, True)

        self.stop_mark = None

        row.cells.append(cell)
