# main_menu.ui

# ift_experiment.ui
class IFTExperimentPresenter(Presenter[Gtk.Notebook]):

# adjust app.py
def _goto_ift(self, *_) -> None:


local_storage_cs = ComponentSymbol()  # type: ComponentSymbol[Gtk.Widget]


@local_storage_cs.view()
class LocalStorageView(View['LocalStoragePresenter', Gtk.Widget]):
    STYLE = '''
    .small-pad {
         min-height: 0px;
         min-width: 0px;
         padding: 6px 4px 6px 4px;
    }

    .error {
        color: red;
        border: 1px solid red;
    }

    .error-text {
        color: red;
    }
    '''

    _STYLE_PROV = Gtk.CssProvider()
    _STYLE_PROV.load_from_data(bytes(STYLE, 'utf-8'))
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), _STYLE_PROV, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    _FILE_INPUT_FILTER = Gtk.FileFilter()

    # OpenCV supported image types
    _FILE_INPUT_FILTER.add_mime_type('image/bmp')
    _FILE_INPUT_FILTER.add_mime_type('image/png')
    _FILE_INPUT_FILTER.add_mime_type('image/jpeg')
    _FILE_INPUT_FILTER.add_mime_type('image/jp2')
    _FILE_INPUT_FILTER.add_mime_type('image/tiff')
    _FILE_INPUT_FILTER.add_mime_type('image/webp')
    _FILE_INPUT_FILTER.add_mime_type('image/x‑portable‑anymap')
    _FILE_INPUT_FILTER.add_mime_type('image/vnd.radiance')

    def _do_init(self) -> Gtk.Widget:
        self._widget = Gtk.Grid(row_spacing=10, column_spacing=10)

        file_chooser_lbl = Gtk.Label('Image files:', xalign=0)
        self._widget.attach(file_chooser_lbl, 0, 0, 1, 1)

        self._file_chooser_inp = FileChooserButton(
            file_filter=self._FILE_INPUT_FILTER,
            select_multiple=True
        )
        self._file_chooser_inp.get_style_context().add_class('small-pad')
        self._widget.attach_next_to(self._file_chooser_inp, file_chooser_lbl, Gtk.PositionType.RIGHT, 1, 1)

        frame_interval_lbl = Gtk.Label('Frame interval (s):')
        self._widget.attach(frame_interval_lbl, 0, 1, 1, 1)

        frame_interval_inp_container = Gtk.Grid()
        self._widget.attach_next_to(frame_interval_inp_container, frame_interval_lbl, Gtk.PositionType.RIGHT, 1, 1)

        self._frame_interval_inp = FloatEntry(lower=0, width_chars=6, invisible_char='\0', caps_lock_warning=False)
        self._frame_interval_inp.get_style_context().add_class('small-pad')
        frame_interval_inp_container.add(self._frame_interval_inp)

        # Error message labels

        self._file_chooser_err_msg_lbl = Gtk.Label(xalign=0)
        self._file_chooser_err_msg_lbl.get_style_context().add_class('error-text')
        self._widget.attach_next_to(self._file_chooser_err_msg_lbl, self._file_chooser_inp, Gtk.PositionType.RIGHT, 1, 1)

        self._frame_interval_err_msg_lbl = Gtk.Label(xalign=0)
        self._frame_interval_err_msg_lbl.get_style_context().add_class('error-text')
        self._widget.attach_next_to(self._frame_interval_err_msg_lbl, frame_interval_inp_container, Gtk.PositionType.RIGHT, 1, 1)

        self._widget.show_all()

        self._frame_interval_inp.bind_property(
            'sensitive',
            self._frame_interval_inp,
            'visibility',
            GObject.BindingFlags.SYNC_CREATE
        )

        self.bn_selected_image_paths = GObjectPropertyBindable(self._file_chooser_inp, 'file-paths')
        self.bn_frame_interval = GObjectPropertyBindable(self._frame_interval_inp, 'value')
        self.bn_frame_interval_sensitive = GObjectPropertyBindable(self._frame_interval_inp, 'sensitive')

        # Set which widget is first focused
        self._file_chooser_inp.grab_focus()

        self.presenter.view_ready()

        return self._widget

    def _do_destroy(self) -> None:
        self._widget.destroy()
