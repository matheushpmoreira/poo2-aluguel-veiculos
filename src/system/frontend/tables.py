from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from typing import Callable, Generic, Iterable, Sequence, TypeVar
from tkinter import ttk


T = TypeVar("T")
RowFactory = Callable[[T], Sequence[object]]


@dataclass(frozen=True)
class Column:
    key: str
    title: str
    width: int = 100


class DataTable(Generic[T]):
    def __init__(self, parent: tk.Widget, columns: Iterable[Column], row_factory: RowFactory[T]) -> None:
        self.columns = tuple(columns)
        self.row_factory = row_factory
        self.items: dict[str, T] = {}
        self.tree = ttk.Treeview(parent, columns=tuple(column.key for column in self.columns), show="headings")
        for column in self.columns:
            self.tree.heading(column.key, text=column.title)
            self.tree.column(column.key, width=column.width)

    def pack(self, **kwargs: object) -> None:
        self.tree.pack(**kwargs)

    def bind(self, sequence: str, callback: Callable[[tk.Event], object]) -> None:
        self.tree.bind(sequence, callback)

    def clear(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.items.clear()

    def set_items(self, items: Iterable[T]) -> None:
        self.clear()
        for item in items:
            item_id = self.tree.insert("", "end", values=tuple(self.row_factory(item)))
            self.items[item_id] = item

    def selected_item(self) -> T | None:
        selected = self.tree.selection()
        if not selected:
            return None
        return self.items.get(selected[0])
