# main_menu.ui

# ift_experiment.ui
class IFTExperimentPresenter(Presenter[Gtk.Notebook]):

# adjust app.py
def _goto_ift(self, *_) -> None:


<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated with glade 3.38.1 -->
<interface>
  <requires lib="gtk+" version="3.20"/>
  <template class="IFTExperiment" parent="GtkBox">
    <property name="width-request">800</property>
    <property name="height-request">600</property>
    <property name="can-focus">False</property>
    <property name="orientation">vertical</property>

    <child>
      <object class="GtkNotebook" id = "notebook">
        <property name="can-focus">False</property>

        <child>
          <!-- First Tab: Image Acquisition -->
          <object class="GtkBox">
            <property name="visible">True</property>
            <property name="can_focus">False</property>
            <child>
              <object class="ImageAcquisition">
                <property name="visible">True</property>
                <property name="can_focus">False</property>
              </object>
            </child>
          </object>
          <packing>
            <property name="tab-label" translatable="yes">Acquisition</property>
          </packing>
        </child>

        <child>
          <!-- Second Tab: Preparation -->
          <object class="GtkGrid">
            <property name="visible">True</property>
            <property name="can-focus">False</property>
            <child>
              <object class="IFTPhysicalParametersForm">
                <property name="visible">True</property>
                <property name="can_focus">False</property>
              </object>
              <packing>
                <property name="left-attach">0</property>
                <property name="top-attach">0</property>
              </packing>
            </child>
            <child>
              <object class="GtkSeparator">
                <property name="visible">True</property>
                <property name="orientation">vertical</property>
              </object>
              <packing>
                <property name="left-attach">1</property>
                <property name="top-attach">0</property>
              </packing>
            </child>
            <child>
              <object class="IFTImageProcessing">
                <property name="visible">True</property>
                <property name="can_focus">False</property>
              </object>
              <packing>
                <property name="left-attach">2</property>
                <property name="top-attach">0</property>
              </packing>
            </child>
          </object>
          <packing>
            <property name="tab-label" translatable="yes">Preparation</property>
          </packing>
        </child>

        <child>
          <!-- Third Tab: Report (Analysis) -->
          <object class="IFTReport" id="report_page">
            <property name="visible">True</property>
            <property name="can_focus">False</property>
          </object>
          <packing>
            <property name="tab-label" translatable="yes">Analysis</property>
          </packing>
        </child>
      </object>
    </child>

    <child>
      <object class="GtkBox">
        <property name="halign">fill</property>
        <property name="valign">end</property>
        <property name="can-focus">False</property>
        <property name="orientation">vertical</property>
        <child>
          <object class="GtkStack" id="action_area">
            <property name="visible">True</property>
            <property name="can-focus">False</property>
            <child>
              <object class="LinearFooter">
                <property name="visible">True</property>
                <property name="previous-label">Back</property> <!-- Label for Back button -->
                <property name="next-label">Next</property>
                <signal name="next" handler="next_page"/> <!-- Signal for Next -->
                <signal name="previous" handler="previous_page"/> <!-- Signal for Back -->
              </object>
              <packing>
                <property name="name">0</property>
              </packing>
            </child>
            <child>
              <object class="LinearFooter">
                <property name="visible">True</property>
                <property name="next-label">Next</property> <!-- Label for Next button -->
                <signal name="next" handler="next_page"/> <!-- Signal for Next -->
                <signal name="previous" handler="previous_page"/> <!-- Signal for Back -->
              </object>
              <packing>
                <property name="name">1</property>
                <property name="position">1</property>
              </packing>
            </child>
            <child>
              <object class="AnalysisFooter" id="analysis_footer">
                <property name="visible">True</property>
                <signal name="save" handler="save_analyses"/>
                <signal name="stop" handler="cancel_analyses"/>
                <signal name="previous" handler="previous_page"/>
              </object>
              <packing>
                <property name="name">2</property>
                <property name="position">2</property>
              </packing>
            </child>
          </object>
          <packing>
            <property name="expand">True</property>
            <property name="fill">True</property>
          </packing>
        </child>
      </object>
    </child>  

  </template>
</interface>

``
from gi.repository import GObject, Gtk
from injector import inject

from opendrop.app.common.footer.analysis import AnalysisFooterStatus
from opendrop.appfw import Presenter, TemplateChild, component
from opendrop.widgets.yes_no_dialog import YesNoDialog

from .analysis_saver import ift_save_dialog_cs
from .services.progress import IFTAnalysisProgressHelper
from .services.session import IFTSession, IFTSessionModule


@component(
    template_path='./ift_experiment.ui',
    modules=[IFTSessionModule],
)

class IFTExperimentPresenter(Presenter[Gtk.Notebook]):
    action_area = TemplateChild('action_area')  # type: TemplateChild[Gtk.Stack]
    analysis_footer = TemplateChild('analysis_footer')
    notebook = TemplateChild('notebook')  # Reference to the Gtk.Notebook


    report_page = TemplateChild('report_page')

    @inject
    def __init__(self, session: IFTSession, progress_helper: IFTAnalysisProgressHelper) -> None:
        self.session = session
        self.progress_helper = progress_helper

        session.bind_property('analyses', self.progress_helper, 'analyses', GObject.BindingFlags.SYNC_CREATE)

    def after_view_init(self) -> None:
        print("after_view_init called")  # For debugging
        self.session.bind_property('analyses', self.report_page, 'analyses', GObject.BindingFlags.SYNC_CREATE)

        self.progress_helper.bind_property(
            'status', self.analysis_footer, 'status', GObject.BindingFlags.SYNC_CREATE,
            lambda binding, x: {
                IFTAnalysisProgressHelper.Status.ANALYSING: AnalysisFooterStatus.IN_PROGRESS,
                IFTAnalysisProgressHelper.Status.FINISHED: AnalysisFooterStatus.FINISHED,
                IFTAnalysisProgressHelper.Status.CANCELLED: AnalysisFooterStatus.CANCELLED,
            }[x],
            None,
        )

        self.progress_helper.bind_property(
            'fraction', self.analysis_footer, 'progress', GObject.BindingFlags.SYNC_CREATE
        )
        self.progress_helper.bind_property(
            'time-start', self.analysis_footer, 'time-start', GObject.BindingFlags.SYNC_CREATE
        )
        self.progress_helper.bind_property(
            'est-complete', self.analysis_footer, 'time-complete', GObject.BindingFlags.SYNC_CREATE
        )

    def prepare(self, *_) -> None:
        # Update footer to show current page's action widgets.
        print("before prepare: self host")
        cur_page = self.host.get_current_page()
        print("after prepare: self host")
        self.action_area.set_visible_child_name(str(cur_page))
    # def prepare(self, *_) -> None:
    #     if isinstance(self.host, Gtk.Notebook):
    #         cur_page = self.host.get_current_page()
    #         self.action_area.set_visible_child_name(str(cur_page))
    #     else:
    #         print("Error: self.host is not a Gtk.Notebook instance.")

        

    def next_page(self, *_) -> None:
        cur_page = self.host.gtk_notebook_get_current_page(notebook)
        if cur_page == 0:
            self.host.next_page()
        elif cur_page == 1:
            self.start_analyses()
            self.host.next_page()
        else:
            # Ignore, on last page.
            return

    def previous_page(self, *_) -> None:
        cur_page = self.host.get_current_page()
        if cur_page == 0:
            # Ignore, on first page.
            return
        elif cur_page == 1:
            self.host.previous_page()
        elif cur_page == 2:
            self.clear_analyses()
            self.host.previous_page()

    def start_analyses(self) -> None:
        self.session.start_analyses()

    def clear_analyses(self) -> None:
        self.session.clear_analyses()

    def cancel_analyses(self, *_) -> None:
        if hasattr(self, 'cancel_dialog'): return

        self.cancel_dialog = YesNoDialog(
            parent=self.host,
            message_format='Confirm stop analysis?',
        )

        def hdl_response(dialog: Gtk.Widget, response: Gtk.ResponseType) -> None:
            del self.cancel_dialog
            dialog.destroy()

            self.progress_helper.disconnect(status_handler_id)

            if response == Gtk.ResponseType.YES:
                self.session.cancel_analyses()

        def hdl_progress_status(*_) -> None:
            if (self.progress_helper.status is IFTAnalysisProgressHelper.Status.FINISHED or
                    self.progress_helper.status is IFTAnalysisProgressHelper.Status.CANCELLED):
                self.cancel_dialog.close()

        # Close dialog if analysis finishes or cancels before user responds.
        status_handler_id = self.progress_helper.connect('notify::status', hdl_progress_status)

        self.cancel_dialog.connect('response', hdl_response)

        self.cancel_dialog.show()

    def save_analyses(self, *_) -> None:
        if hasattr(self, 'save_dialog_component'): return

        save_options = self.session.create_save_options()

        def hdl_ok() -> None:
            self.save_dialog_component.destroy()
            del self.save_dialog_component
            self.session.save_analyses(save_options)

        def hdl_cancel() -> None:
            self.save_dialog_component.destroy()
            del self.save_dialog_component

        self.save_dialog_component = ift_save_dialog_cs.factory(
            parent_window=self.host,
            model=save_options,
            do_ok=hdl_ok,
            do_cancel=hdl_cancel,
        ).create()
        self.save_dialog_component.view_rep.show()

    def close(self, discard_unsaved: bool = False) -> None:
        if hasattr(self, 'confirm_discard_dialog'): return

        if discard_unsaved or self.session.safe_to_discard():
            self.session.quit()
            self.host.destroy()
        else:
            self.confirm_discard_dialog = YesNoDialog(
                message_format='Discard unsaved results?',
                parent=self.host,
            )

            def hdl_response(dialog: Gtk.Dialog, response: Gtk.ResponseType) -> None:
                del self.confirm_discard_dialog
                dialog.destroy()

                if response == Gtk.ResponseType.YES:
                    self.close(True)

            self.confirm_discard_dialog.connect('response', hdl_response)
            self.confirm_discard_dialog.show()

    def delete_event(self, *_) -> bool:
        self.close()
        return True
