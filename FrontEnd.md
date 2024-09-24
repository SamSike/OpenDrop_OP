# main_menu.ui

# ift_experiment.ui
class IFTExperimentPresenter(Presenter[Gtk.Notebook]):

# adjust app.py
def _goto_ift(self, *_) -> None:


      <object class="GtkBox">
        <property name="orientation">vertical</property>
        <property name="spacing">10</property>
        <child>
          <object class="GtkProgressBar" id="progress_bar">
            <property name="show-text">True</property>
            <property name="orientation">horizontal</property>
            <property name="fraction">0.33</property> <!-- Set to 0.33 for Acquisition -->
          </object>
        </child>
        <child>
          <object class="GtkLabel" id="stage_label">
            <property name="label">Acquisition</property> <!-- Display current stage -->
            <property name="halign">center</property>
          </object>
        </child>
      </object>
    </child>


    ----
    <child>
      <object class="GtkNotebook" id="notebook">
        <property name="can-focus">False</property>
        <property name="scrollable">False</property>

        <child>
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
          <object class="IFTReport" id="report_page">
            <property name="visible">True</property>
            <property name="can_focus">False</property>
          </object>
          <packing>
            <property name="tab-label" translatable="yes">Analysis</property>
          </packing>
        </child>

        <child>
            <!-- Third Tab: Output (Report) -->
            <object class="GtkBox" id="output_page">
              <property name="visible">True</property>
              <property name="can-focus">False</property>
              <child>
                <object class="GtkLabel">
                  <property name="label">Output will be displayed here.</property>
                </object>
              </child>
            </object>
            <packing>
              <property name="tab-label" translatable="yes">Output</property>
            </packing>
          </child>
      </object>
    </child>