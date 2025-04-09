from modules.IFT.analysis import PendantAnalysisService
from modules.classes import ExperimentalSetup, IFTExperimentalDrop, DropData, Tolerances
#from modules.PlotManager import PlotManager
from modules.ExtractData import ExtractedData
from modules.read_image import get_image
from modules.select_regions import set_drop_region,set_surface_line, correct_tilt
from modules.extract_profile import extract_drop_profile
from utils.enums import *
from utils.config import *
from modules.CA.fit.fits import perform_fits
from utils.geometry import Rect2
from modules.select_regions import set_needle_region

import matplotlib.pyplot as plt

import os
import numpy as np
import tkinter as tk
from tkinter import font as tkFont

import timeit

class IFTDataProcessor:
    def process_data(self, fitted_drop_data, user_input_data, callback):

        # print("user_input_data: ", vars(user_input_data))
        n_frames = user_input_data.number_of_frames
        extracted_data = ExtractedData(n_frames, fitted_drop_data.parameter_dimensions)

        self.output = []

        for i in range(n_frames):
            print("\nProcessing frame %d of %d..." % (i+1, n_frames))
            input_file = user_input_data.import_files[i]
            print("\nProceccing " + input_file)
            time_start = timeit.default_timer()

            raw_experiment = IFTExperimentalDrop()
            get_image(raw_experiment, user_input_data, i) # save image in here...
            set_drop_region(raw_experiment, user_input_data, i+1)
            set_needle_region(raw_experiment, user_input_data)

            if i == 0:
                extracted_data.initial_image_time = raw_experiment.time

            analysis_service = PendantAnalysisService()
            analysis = analysis_service.analyse(raw_experiment, user_input_data)

            if analysis.bn_is_done:
                print('result:')
                print(raw_experiment.apex_radius)
                print(raw_experiment.surface_area)
                print(raw_experiment.volume)
                print(raw_experiment.interfacial_tension)
                print(raw_experiment.worthington)

            
            # extracted_data.contact_angles = raw_experiment.contact_angles # DS 7/6/21
            # self.output.append(extracted_data)

            #if callback:
                #callback(extracted_data)

    def save_result(self, input_file, output_directory, filename):
        for index, extracted_data in enumerate(self.output):
            extracted_data.export_data(input_file, output_directory, filename, index)