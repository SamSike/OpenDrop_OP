#!/usr/bin/env python
# coding=utf-8


from opendrop_ml.modules.core.classes import DropData
from opendrop_ml.views.main_window import MainWindow
from opendrop_ml.views.function_window import call_user_input
from opendrop_ml.utils.enums import FunctionType
from opendrop_ml.utils.os import is_windows

import os
import numpy as np
import time

# from __future__ import unicode_literals
# from __future__ import print_function
# from opendrop_ml.modules.classes import ExperimentalDrop, DropData, Tolerances
# from opendrop_ml.modules.static_setup_class import ExperimentalSetup
# # from opendrop_ml.modules.ui import initialise_ui
# from opendrop_ml.modules.user_interface import call_user_input
# # from opendrop_ml.modules.load import load_data
# from opendrop_ml.modules.extract_data import extract_drop_profile
# from opendrop_ml.modules.initialise_parameters import initialise_parameters
# # from opendrop_ml.modules.fit_data import fit_raw_experiment
# # from opendrop_ml.modules.user_set_regions
# from opendrop_ml.modules.PlotManager import PlotManager
# from opendrop_ml.modules.analyse_needle import calculate_needle_diameter
# from opendrop_ml.modules.fit_data import fit_experimental_drop
# from opendrop_ml.modules.generate_data import generate_full_data
# from opendrop_ml.modules. import add_data_to_lists


np.set_printoptions(suppress=True)
np.set_printoptions(precision=3)

DELTA_TOL = 1.0e-6
GRADIENT_TOL = 1.0e-6
MAXIMUM_FITTING_STEPS = 10
OBJECTIVE_TOL = 1.0e-4
ARCLENGTH_TOL = 1.0e-6
MAXIMUM_ARCLENGTH_STEPS = 10
NEEDLE_TOL = 1.0e-4
NEEDLE_STEPS = 20


def main():
    clear_screen()

    continue_processing = {"status": True}

    while continue_processing["status"]:
        fitted_drop_data = DropData()
        """
        tolerances = Tolerances(
            DELTA_TOL,
            GRADIENT_TOL,
            MAXIMUM_FITTING_STEPS,
            OBJECTIVE_TOL,
            ARCLENGTH_TOL,
            MAXIMUM_ARCLENGTH_STEPS,
            NEEDLE_TOL,
            NEEDLE_STEPS)
        """
        # user_inputs = ExperimentalSetup()

        def open_ift(main_window: MainWindow):
            call_user_input(
                FunctionType.INTERFACIAL_TENSION, fitted_drop_data, main_window
            )

        def open_ca(main_window):
            call_user_input(FunctionType.CONTACT_ANGLE,
                            fitted_drop_data, main_window)

        main_window = MainWindow(continue_processing, open_ift, open_ca)


#    cheeky_pause()


def clear_screen():
    os.system("cls" if is_windows() else "clear")


def pause_wait_time(elapsed_time, requested_time):
    if elapsed_time > requested_time:
        print("WARNING: Fitting took longer than desired wait time")
    else:
        time.sleep(requested_time - elapsed_time)


def cheeky_pause():
    import Tkinter

    #    cv2.namedWindow("Pause")
    #    while 1:
    #        k = cv2.waitKey(1) & 0xFF
    #        if (k==27):
    #            break
    # root = Tkinter.Tk()
    #    B = Tkinter.Button(top, text="Exit",command = cv2.destroyAllWindows())
    #    B = Tkinter.Button(root, text="Exit",command = root.destroy())
    #
    #    B.pack()
    #    root.mainloop()

    root = Tkinter.Tk()
    frame = Tkinter.Frame(root)
    frame.pack()

    button = Tkinter.Button(frame)
    button["text"] = "Good-bye."
    button["command"] = root.destroy()  # close_window(root)
    button.pack()

    root.mainloop()


def quit_(root):
    root.quit()


# def close_window(root):
#    root.destroy()


if __name__ == "__main__":
    main()
    """
    root = tk.Tk()
    # quit button
    buttonFont = tkFont.Font(family='Helvetica', size=48, weight='bold') #This isn't working for some reason (??)
    quit_button = tk.Button(master=root, font=buttonFont,text='Quit',height=4,width=15,
                            command=lambda: quit_(root),bg='blue',fg='white',activeforeground='white',activebackground='red')
    quit_button.pack()
    
    root.mainloop()
    """
