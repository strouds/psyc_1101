# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 13:37:22 2021

main python code for interpreting survey results and generating statistics and plots

@author: Stroud Stacy
"""

from datetime import datetime
from scipy import stats
import pylab

def importData(filename):
    """
    Imports survey data from .csv, scores and segments the entries, and returns
    a list of survey results as feature vectors.

    Parameters
    ----------
    filename : CSV containing raw survey results (copied from Survio into
          Google Sheets, then exported as CSV file).

    Returns
    -------
    data : Dictionary of lists of each response type.
        'entry' = entry number
        'response time' = time survey response was submitted
        'subjective SES' = MacArthur Scale of Subjective Social Status 
        'income' = score of income level responses
        'education' = score of education level responses
        'businesses' = score of ownership of businesses
        'rentals' = score of ownership of rental properties
        'homes' = score of ownership of homes
        'policy question' 1 - 4 = score of responses to policy questions
        'politics' = score of political alignment

    """
    data = {}
    data['entry'], data['response time'], data['subjective SES'] = [], [], []
    data['income'], data['education'], data['businesses'] = [], [], []
    data['rentals'], data['homes'], data['policy question 1'] = [], [], []
    data['policy question 2'], data['policy question 3'], = [], []
    data['policy question 4'], data['politics'] = [], []
    
    # Dictionaries, used to score the responses
    d_income = {'$10,000 or less' : 0, '$10,001 - $25,000' : 1,
                      '$25,001 - $50,000' : 2, '$50,001 - $75,000' : 3,
                      '$75,001 - $100,000' : 4, '$100,001 - $150,000': 5,
                      '$150,001 or more': 6}
    d_education = {'Did not complete high school' : 0, 'High school diploma' : 1,
                 'Vocational School' : 2, 'College degree' : 3,
                 'Master\'s degree' : 4, 'Higher degree (including doctorate or law degree)' : 5}
    d_business = {'No' : 0, 'Self-employed (no other employees)' : 1,
                  'Small business' : 2, 'Mid-size business (or multiple small businesses, e.g. franchises)' : 3,
                  'Large business' : 4}
    d_rentals = {'No' : 0, 'One or a few (e.g. renting a basement or old family home)' : 1,
                 'Several homes, or a commercial property' : 2,
                 'Many homes or commercial properties' : 3}
    d_homes = {'No' : 0, 'Single home' : 1, 'Single home + vacation property' : 2,
               'Several homes or vacation properties' : 3}
    d_policies = {'Strongly disagree' : -2, 'Disagree' : -1, 'Neutral' : 0,
                  'Agree' : 1, 'Strongly Agree' : 2}
    d_politics = {'Far-left' : -2, 'Liberal' : -1, 'Undecided' : 0,
                  'Conservative' : 1, 'Far-right' : 2}
    
    f = open(filename)
    line = f.readline()
    while line != '':
        # separate entries that contain commas (they are contained in quotes)
        split_quote = line.split('\"')
        # seperate remaining entries
        split_comma = split_quote[4].split(',')
        del split_comma[0]  # removes empty first entry
        
        #creates a list of survey entry numbers
        entry = split_quote[0].strip('#,')
        data['entry'].append(int(entry))
        
        # creates a list of survey response times
        response_time = split_quote[1]
        response_datetime = datetime.strptime(response_time, "%B %d, %Y %H:%M")
        data['response time'].append(response_datetime)
        
        # cleans the subjective SES score and converts to an integer
        subjective_SES = split_quote[2]
        if subjective_SES == ',1 / 10,':
            subjective_SES = '1'
        elif subjective_SES == ',10 / 10,':
            subjective_SES = '10'
        else:
            subjective_SES = subjective_SES.strip(' ,/10')
        data['subjective SES'].append(int(subjective_SES))
        
        # scores entries for income and education by comparing the raw answer
        # to the scoring dictionary above
        # higher score = higher level of income or education
        income = d_income[split_quote[3]]
        education = d_education[split_comma[0]]
        data['income'].append(income)
        data['education'].append(education)
        
        # scores entries for property ownership by comparing the raw answer
        # to the scoring dictionary above
        # higher score = more property owned
        businesses = d_business[split_comma[1]]
        rentals = d_rentals[split_comma[2]]
        homes = d_homes[split_comma[3]]
        data['businesses'].append(businesses)
        data['rentals'].append(rentals)
        data['homes'].append(homes)
        
        # scores entries for policy support by comparing the raw answer
        # to the scoring dictionary above
        # higher score = higher support for redistributive policies
        
        policy_1 = d_policies[split_comma[4]]
        policy_2 = d_policies[split_comma[5]]
        policy_3 = d_policies[split_comma[6]]
        policy_4 = -d_policies[split_comma[7]]
        data['policy question 1'].append(policy_1)
        data['policy question 2'].append(policy_2)
        data['policy question 3'].append(policy_3)
        data['policy question 4'].append(policy_4)
        
        politics = split_comma[8].strip('\n')
        data['politics'].append(d_politics[politics])
        
        line = f.readline()
    f.close()
    return data

class SurveyResults(object):
    def __init__(self, data):
        """ Breaks out raw data set into a data structure, scores each section
        of the survey, and calculates statistics for the data sets """
        # all lists converted to 'array' datatype for linear regression
        self.entries = pylab.array(data['entry'])
        self.response_time = pylab.array(data['response time'])
        
        self.subjective_scores = pylab.array(data['subjective SES'])

        self.income = pylab.array(data['income'])
        self.education = pylab.array(data['education'])
        # combine income and education into an objective SES score
        self.objective_scores = self.income + self.education
        
        self.businesses = pylab.array(data['businesses'])
        self.rentals = pylab.array(data['rentals'])
        self.homes = pylab.array(data['homes'])
        # combine business, rental, and home ownership into a property score
        self.property_scores = []
        self.property_scores = self.businesses + self.rentals + self.homes
        
        self.policy_1 = pylab.array(data['policy question 1'])
        self.policy_2 = pylab.array(data['policy question 2'])
        self.policy_3 = pylab.array(data['policy question 3'])
        self.policy_4 = pylab.array(data['policy question 4'])
        # combine policy question responses into a policy score
        self.policy_scores = []
        self.policy_scores = self.policy_1 + self.policy_2 + \
            self.policy_3 + self.policy_4
        
        self.politics = pylab.array(data['politics'])
        
        # dictionaries of variables
        self.independent_scores = {'subjective scores': self.subjective_scores,
                                 'objective scores': self.objective_scores,
                                 'property scores': self.property_scores,
                                 'politics': self.politics}
        
        self.dependent_scores = {'policy scores': self.policy_scores}
        # generate statistics and save to a CSV file
        self.stats = self.genStats() 

    
    def fitAndPlot(self, independent, dependent, independent_name, dependent_name):
        """
        Uses the Scipy linregress (linear regression) function to produce a linear
        regression model and statistics about that model, and produces a plot
        containing both the original dataset and the linear regression model,
        as well as statistics about the model.
    
        Parameters
        ----------
        independent : Independent variable
        dependent : Dependent variable
        independent_name : String with the name of the independent variable,
            used in the plot.
        dependent_name : String with the name of the dependent variable,
            used in the plot.
    
        Returns
        -------
        slope : Slope of the linear regression model for the dataset
        intercept : Y-intercept of the linear regression model for the dataset
        r_value : R value of the linear regression model for the dataset
            (still need to square it for R-squared)
        p_value : P value of the linear regression model for the dataset
        std_err : Standard Error of the linear regression model for the dataset
    
        """
        slope, intercept, r_value, p_value, std_err = \
            stats.linregress(independent, dependent)
        r_squared = r_value ** 2
        predicted = slope * independent + intercept
        # calculate frequency of points in scatter plot and use to size the
        # points on the plot
        point_list = []
        for i in range(len(independent)):
            point_list.append((independent[i], dependent[i]))
        point_sizes = []
        for point in point_list:
            point_sizes.append(point_list.count(point) * 10)
        pylab.scatter(independent, dependent, s=point_sizes)
        pylab.plot(independent, predicted)
        pylab.xlabel(independent_name)
        pylab.ylabel(dependent_name)
        pylab.title(f'Trend line = {round(slope, 3)}x + {round(intercept, 3)}, ' \
                    + f'R-squared = {round(r_squared, 2)}\n' + \
                    f'P = {round(p_value, 3)}, Standard Error = {round(std_err, 3)}')
        pylab.show()
        return (slope, intercept, r_value, p_value, std_err)
    
    def genFits(self):
        """ generates and plots regression models from data """
        for ind_var in self.independent_scores:
            for dep_var in self.dependent_scores:
                self.fitAndPlot(self.independent_scores[ind_var], 
                           self.dependent_scores[dep_var], 
                           ind_var.capitalize(), dep_var.capitalize())
    
    def genHists(self):
        # This section produces histograms of the number of responses for variables
        # included in the study
        
        # This chart shows when responses arrived.
        pylab.hist(self.response_time, bins=12)
        pylab.xticks([18819., 18820., 18821., 18822., 18823., 18824.],
                     ['7-11', '7-12', '7-13', '7-14', '7-15', '7-16'])
        pylab.xlabel('Date of response')
        pylab.ylabel('Number of responses')
        pylab.title('Date responses arrived\n' +
                    f'Total responses: {len(self.response_time)}')
        pylab.show()
        # frequency of subjective SES scores
        pylab.hist(self.subjective_scores, bins=10, range=(1,10))
        pylab.xlabel('Subjective SES score')
        pylab.ylabel('Number of responses')
        mean = round(self.stats['subjective scores'][2], 3)
        std_dev = round(self.stats['subjective scores'][3], 3)
        pylab.title('Subjective SES responses\n' + f'Mean: {mean}, ' +
                    f'Standard deviation: {std_dev}')
        pylab.show()
        # frequency of objective SES scores
        pylab.hist(self.objective_scores, bins=11, range=(0,10))
        pylab.xlabel('Objective SES score')
        pylab.ylabel('Number of responses')
        mean = round(self.stats['objective scores'][2], 3)
        std_dev = round(self.stats['objective scores'][3], 3)
        pylab.title('Objective SES responses\n' + f'Mean: {mean}, ' +
                    f'Standard deviation: {std_dev}')
        pylab.show()
        # frequency of property scores
        pylab.hist(self.property_scores, bins=10, range=(0,11))
        pylab.xlabel('Property ownership score')
        pylab.ylabel('Number of responses')
        mean = round(self.stats['property scores'][2], 3)
        std_dev = round(self.stats['property scores'][3], 3)
        pylab.title('Property ownership responses\n' + f'Mean: {mean}, ' +
                    f'Standard deviation: {std_dev}')
        pylab.show()
        # frequency of policy scores
        pylab.hist(self.policy_scores, bins=16, range=(-8,8))
        pylab.xlabel('Policy score')
        pylab.ylabel('Number of responses')
        mean = round(self.stats['policy scores'][2], 3)
        std_dev = round(self.stats['policy scores'][3], 3)
        pylab.title('Policy responses\n' + f'Mean: {mean}, ' +
                    f'Standard deviation: {std_dev}')
        pylab.show()
        # frequency of political self-report
        pylab.hist(self.politics, bins=5, range=(-2,2))
        pylab.xticks([-2,-1,0,1,2])
        pylab.xlabel('Political preference')
        pylab.ylabel('Number of responses')
        mean = round(self.stats['politics'][2], 3)
        std_dev = round(self.stats['politics'][3], 3)
        pylab.title('Political alignment responses\n' + f'Mean: {mean}, ' +
                    f'Standard deviation: {std_dev}')
        pylab.show()
        

    
    def genStats(self):
        """ generates statistics from data """
        stats = self.statsCSV({**self.independent_scores, 
                               **self.dependent_scores})
        return stats
        
    
    def singleVariableStats(self, variable):
        """ Calculates basic statistics of a variable using stats.describe
        and returns the minimum and maximum values in the set, the mean,
        and the standard deviation """
        s = stats.describe(variable)
        minmax, mean, variance = s[1], s[2], s[3]
        std_dev = variance ** 0.5
        return minmax, mean, std_dev
    
    def statsCSV(self, variables):
        """ takes a dictionary of variables to generate statistics with,
        outputs a .CSV file with the labeled statistics, builds dictionary
        of statistics labeled by variable """
        stats = {}
        f = open('stats.csv', mode='w')
        f.write(',Minimum,Maximum,Mean,Standard deviation\n')
        for variable in variables:
            minmax, mean, std_dev = self.singleVariableStats(variables[variable])
            stats[variable] = (minmax[0], minmax[1], mean, std_dev)
            mean = round(mean, 3)
            std_dev = round(std_dev, 3)
            f.write(f'{variable.capitalize()},{minmax[0]},{minmax[1]},{mean},{std_dev}\n')
        f.close()
        return stats
