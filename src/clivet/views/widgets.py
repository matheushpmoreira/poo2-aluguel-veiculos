import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, ttk
from typing import Callable, Generic, Iterable, Sequence, TypeVar

try:
    from tkcalendar import DateEntry as CalendarDateEntry
except ImportError:
    CalendarDateEntry = None


T = TypeVar("T")
RowFactory = Callable[[T], Sequence[object]]


class DateEntry(ttk.Entry if CalendarDateEntry is None else CalendarDateEntry):
    def __init__(self, master=None, textvariable: tk.StringVar | None = None, **kwargs):
        if CalendarDateEntry is None:
            super().__init__(master, textvariable=textvariable, **kwargs)
            return
        kwargs.setdefault("date_pattern", "yyyy-mm-dd")
        super().__init__(master, textvariable=textvariable, **kwargs)


@dataclass(frozen=True)
class Choice(Generic[T]):
    value: T
    label: str


class ChoiceBox(Generic[T]):
    def __init__(self, parent: tk.Widget, choices: Iterable[Choice[T]], width: int | None = None) -> None:
        self.variable = tk.StringVar()
        self.widget = ttk.Combobox(parent, textvariable=self.variable, state="readonly", width=width)
        self.choices: tuple[Choice[T], ...] = ()
        self.set_choices(choices)

    def grid(self, **kwargs: object) -> None:
        self.widget.grid(**kwargs)

    def pack(self, **kwargs: object) -> None:
        self.widget.pack(**kwargs)

    def bind(self, sequence: str, callback: Callable[[tk.Event], object]) -> None:
        self.widget.bind(sequence, callback)

    def set_choices(self, choices: Iterable[Choice[T]]) -> None:
        current_value = self.selected_value(default=None)
        self.choices = tuple(choices)
        self.widget["values"] = tuple(choice.label for choice in self.choices)
        if current_value is not None and self.select_value(current_value):
            return
        self.select_first()

    def selected_value(self, default: T | None = None) -> T | None:
        index = self.widget.current()
        if 0 <= index < len(self.choices):
            return self.choices[index].value
        return default

    def require_value(self) -> T:
        value = self.selected_value()
        if value is None:
            raise ValueError("Nenhuma opção foi selecionada.")
        return value

    def select_first(self) -> None:
        if self.choices:
            self.widget.current(0)
        else:
            self.variable.set("")

    def select_value(self, value: T) -> bool:
        for index, choice in enumerate(self.choices):
            if choice.value == value:
                self.widget.current(index)
                return True
        return False


@dataclass(frozen=True)
class Column:
    key: str
    title: str
    width: int = 100


class DataTable(Generic[T]):
    def __init__(
        self,
        parent: tk.Widget,
        columns: Iterable[Column],
        row_factory: RowFactory[T],
        *,
        selectmode: str = "browse",
    ) -> None:
        self.columns = tuple(columns)
        self.row_factory = row_factory
        self.items: dict[str, T] = {}
        self.tree = ttk.Treeview(
            parent,
            columns=tuple(column.key for column in self.columns),
            show="headings",
            selectmode=selectmode,
        )
        for column in self.columns:
            self.tree.heading(column.key, text=column.title)
            self.tree.column(column.key, width=column.width, anchor="w")

    def pack(self, **kwargs: object) -> None:
        self.tree.pack(**kwargs)

    def grid(self, **kwargs: object) -> None:
        self.tree.grid(**kwargs)

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

    def selected_items(self) -> list[T]:
        return [self.items[item_id] for item_id in self.tree.selection() if item_id in self.items]

    def select_where(self, predicate: Callable[[T], bool]) -> None:
        self.tree.selection_remove(*self.tree.selection())
        for item_id, item in self.items.items():
            if predicate(item):
                self.tree.selection_add(item_id)


class ViewFrame(ttk.Frame):
    def show_error(self, error: Exception) -> None:
        messagebox.showerror("Erro", str(error))

    def show_success(self, message: str) -> None:
        messagebox.showinfo("Sucesso", message)

    def show_warning(self, title: str, message: str) -> None:
        messagebox.showwarning(title, message)
