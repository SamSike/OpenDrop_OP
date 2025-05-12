from modules.core.classes import ExperimentalSetup, ExperimentalDrop, DropData, Tolerances
#from modules.PlotManager import PlotManager
from modules.preprocessing.ExtractData import ExtractedData
from modules.image.read_image import get_image
from modules.image.select_regions import set_drop_region, set_surface_line, correct_tilt, set_needle_region
from modules.contact_angle.extract_profile import extract_drop_profile
from utils.enums import *
from utils.config import *
from modules.fitting.fits import perform_fits

import matplotlib.pyplot as plt
from utils.enums import FittingMethod
import os
import numpy as np
import tkinter as tk
from tkinter import font as tkFont

import timeit

class iftDataProcessor:
    def process_data(self, fitted_drop_data, user_input_data, callback):

        analysis_methods = dict(user_input_data.analysis_methods_pd)

        n_frames = user_input_data.number_of_frames
        extracted_data = ExtractedData(n_frames, fitted_drop_data.parameter_dimensions)
        raw_experiment = ExperimentalDrop()

        #if user_input_data.interfacial_tension_boole:
        #    plots = PlotManager(user_input_data.wait_time, n_frames)

        self.output = []

        for i in range(n_frames):
            print("\nProcessing frame %d of %d..." % (i+1, n_frames))
            input_file = user_input_data.import_files[i]
            print("\nProceccing " + input_file)
            time_start = timeit.default_timer()
            raw_experiment = ExperimentalDrop()
            get_image(raw_experiment, user_input_data, i) # save image in here...
            set_drop_region(raw_experiment, user_input_data)
            set_needle_region(raw_experiment, user_input_data)

            # extract_drop_profile(raw_experiment, user_input_data)
            extract_drop_profile(raw_experiment, user_input_data)

            if i == 0:
                extracted_data.initial_image_time = raw_experiment.time

            set_surface_line(raw_experiment, user_input_data) #fits performed here if baseline_method is User-selected


            # TODO: Add analysis

            #print('Extracted outputs:')
            #self.output.append(extracted_data)

            if callback:
                None
                #callback(extracted_data)

    def save_result(self, input_files, output_directory, filename):
        for index, extracted_data in enumerate(self.output):
            extracted_data.export_data(input_files[index], output_directory, filename, index)