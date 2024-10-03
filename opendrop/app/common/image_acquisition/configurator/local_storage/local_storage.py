# Copyright © 2020, Joseph Berry, Rico Tabor (opendrop.dev@gmail.com)
# OpenDrop is released under the GNU GPL License. You are free to
# modify and distribute the code, but always under the same license
#
# If you use this software in your research, please cite the following
# journal articles:
#
# J. D. Berry, M. J. Neeson, R. R. Dagastine, D. Y. C. Chan and
# R. F. Tabor, Measurement of surface and interfacial tension using
# pendant drop tensiometry. Journal of Colloid and Interface Science 454
# (2015) 226–237. https://doi.org/10.1016/j.jcis.2015.05.012
#
# E. Huang, T. Denning, A. Skoufis, J. Qi, R. R. Dagastine, R. F. Tabor
# and J. D. Berry, OpenDrop: Open-source software for pendant drop
# tensiometry & contact angle measurements, submitted to the Journal of
# Open Source Software
#
# These citations help us not only to understand who is using and
# developing OpenDrop, and for what purpose, but also to justify
# continued development of this code and other open source resources.
#
# OpenDrop is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.  You
# should have received a copy of the GNU General Public License along
# with this software.  If not, see <https://www.gnu.org/licenses/>.

from typing import Optional

from injector import inject
from gi.repository import Gtk, GObject

# These widgets are used in templates, import them to make sure they're registered with the GLib type system.
from opendrop.widgets.float_entry import FloatEntry

from opendrop.appfw import Presenter, ComponentFactory, TemplateChild, component, install
from opendrop.app.common.services.acquisition import LocalStorageAcquirer
from opendrop.utility.bindable.gextension import GObjectPropertyBindable
from opendrop.widgets.file_chooser_button import FileChooserButton

@component(
    template_path='./local_storage.ui',
)


class ImageAcquisitionConfiguratorLocalStoragePresenter(Presenter):
    file_chooser_button: TemplateChild[FileChooserButton] = TemplateChild('file_chooser_button')
    frame_interval_entry: TemplateChild[FloatEntry] = TemplateChild('frame_interval_entry')
    frame_interval_grid: TemplateChild[Gtk.Label] = TemplateChild('frame_interval_grid')
   

    @inject
    def __init__(self, cf: ComponentFactory) -> None:
        self.cf = cf
        self.event_connections = ()
        
       
    def after_view_init(self) -> None:
        self.bn_selected_image_paths = GObjectPropertyBindable(self.file_chooser_button, 'file-paths')
        self.bn_frame_interval_sensitive =  GObjectPropertyBindable(self.frame_interval_entry, 'sensitive')
        self.bn_frame_interval_visible =  GObjectPropertyBindable(self.frame_interval_entry, 'visible')
        self.bn_frame_interval_visibility =  GObjectPropertyBindable(self.frame_interval_grid, 'visible')
        print("bn_frame_interval_sensitive: ",self.bn_frame_interval_sensitive.get())
        print("bn_frame_interval_visibility: ",self.bn_frame_interval_visibility.get())
        # self.file_chooser_button
        self.event_connections = [
            self.acquirer.bn_last_loaded_paths.on_changed.connect(self._hdl_model_last_loaded_paths_changed),
            # self.acquirer.bn_frame_interval.on_changed.connect(self.acquirer_frame_interval_changed),
            self.bn_selected_image_paths.on_changed.connect(self._hdl_view_selected_image_paths_changed)
        
        ]

        self._hdl_model_last_loaded_paths_changed()
        # self.acquirer_frame_interval_changed()

    def _hdl_model_last_loaded_paths_changed(self) -> None:
        print("_hdl_model_last_loaded_paths_changed",len(self._acquirer.bn_images.get()))
        if len(self._acquirer.bn_images.get()) <= 1:
            self.bn_frame_interval_visibility.set(False)
            self.bn_frame_interval_sensitive.set(False)
            self.bn_frame_interval_visible.set(False)
            # self.notify('frame_interval_enabled')
        else:
           self.bn_frame_interval_visibility.set(True)
           self.bn_frame_interval_sensitive.set(True)
           self.bn_frame_interval_visible.set(True)
        #    self.notify('frame_interval_enabled')

        last_loaded_paths = self._acquirer.bn_last_loaded_paths.get()
        selected_image_paths = self.bn_selected_image_paths.get()

        if set(last_loaded_paths) != set(selected_image_paths):
            self.bn_selected_image_paths.set(last_loaded_paths)

    def _hdl_view_selected_image_paths_changed(self) -> None:
        print("_hdl_view_selected_image_paths_changed")
        last_loaded_paths = self._acquirer.bn_last_loaded_paths.get()
        selected_image_paths = self.bn_selected_image_paths.get()

        if set(last_loaded_paths) == set(selected_image_paths):
            return

        self._acquirer.load_image_paths(selected_image_paths)

    def _do_destroy(self) -> None:
        for db in self.__data_bindings:
            db.unbind()

        for ec in self.__event_connections:
            ec.disconnect()
    @GObject.Property(flags=GObject.ParamFlags.READWRITE|GObject.ParamFlags.EXPLICIT_NOTIFY)
    def frame_interval(self) -> Optional[float]:
        return self.acquirer.bn_frame_interval.get()

    @frame_interval.setter
    def frame_interval(self, interval: Optional[float]) -> None:
        self.acquirer.bn_frame_interval.set(interval)

    @GObject.Property(type=bool, default=False, flags=GObject.ParamFlags.READABLE|GObject.ParamFlags.EXPLICIT_NOTIFY)
    def frame_interval_enabled(self) -> bool:
        return self.acquirer.bn_num_frames.get() != 1

    @install
    @GObject.Property(flags=GObject.ParamFlags.READWRITE|GObject.ParamFlags.CONSTRUCT_ONLY)
    def acquirer(self) -> LocalStorageAcquirer:
        return self._acquirer

    @acquirer.setter
    def acquirer(self, acquirer: LocalStorageAcquirer) -> None:
        self._acquirer = acquirer

    def destroy(self, *_) -> None:
        for conn in self.event_connections:
            conn.disconnect()