from gi.repository import GObject,Gtk

from opendrop.appfw import Presenter, component, install


@component(
    template_path='./main_menu.ui',
)
class MainMenuPresenter(Presenter):
    @GObject.Property(type=str)
    def version_text(self) -> str:
        from opendrop import __version__ as version
        return 'Version: {}'.format(version)
    
    def exit_btn_clicked(self, *_) -> None:
        self.exit_application.emit()



    def ift_btn_clicked(self, *_) -> None:
        self.ift.emit()

    def conan_btn_clicked(self, *_) -> None:
        self.conan.emit()

    @install
    @GObject.Signal
    def ift(self) -> None: pass

    @install
    @GObject.Signal
    def conan(self) -> None: pass

    @install
    @GObject.Signal
    def exit_application(self) -> None: pass  # Define the exit signal

