from typing import MutableMapping, Optional

from gi.repository import Gtk, GObject

from opendrop.app.common.wizard import WizardPositionView, WizardPageID
from opendrop.component.gtk_widget_view import GtkWidgetView
from opendrop.utility.bindable.bindable import AtomicBindableAdapter


class SidebarWizardPositionView(WizardPositionView, GtkWidgetView[Gtk.Box]):
    def __init__(self):
        self._active_key = None  # type: Optional[WizardPageID]
        self._key_to_lbl = {}  # type: MutableMapping[WizardPageID, Gtk.Label]
        self.bn_active_key = AtomicBindableAdapter(setter=self._set_active_key)

        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=10)
        self.widget.show_all()

    def add_key(self, key: WizardPageID) -> None:
        lbl = self._new_label(key.title)
        lbl.show()
        self.widget.add(lbl)
        self._key_to_lbl[key] = lbl

    def clear(self) -> None:
        for lbl in self._key_to_lbl.values():
            lbl.destroy()

        self._key_to_lbl = {}
        self._active_key = None

    def _set_active_key(self, key: Optional[WizardPageID]) -> None:
        old_key = self._active_key

        if old_key is not None:
            old_lbl = self._key_to_lbl[old_key]
            self._format_label_inactive(old_lbl, old_key.title)

        if key is not None:
            lbl = self._key_to_lbl[key]
            self._format_label_active(lbl, key.title)

        self._active_key = key

    @staticmethod
    def _new_label(title: str) -> Gtk.Widget:
        return Gtk.Label(label=title, xalign=0)

    @staticmethod
    def _format_label_active(lbl: Gtk.Label, title: str) -> None:
        lbl.set_markup('<b>{}</b>'.format(GObject.markup_escape_text(title)))

    @staticmethod
    def _format_label_inactive(lbl: Gtk.Label, title: str) -> None:
        lbl.set_markup(GObject.markup_escape_text(title))