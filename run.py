# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 15:55:09 2021

Runs the code in survey_data.py using data in data.csv

@author: Stroud Stacy
"""

import survey_data

data = survey_data.importData('data.csv')
survey_results = survey_data.SurveyResults(data)
survey_results.genHists()
survey_results.genFits()
