# Downloads monthly report of how many ASCEND enrollments there are in each cohort.
# Requires moodle_downloader.py to be in the same directory and .env file with MOODLE_USERNAME and MOODLE_PASSWORD set.
# 

from moodle_downloader import download_moodle_data
import pandas as pd
import datetime as dt

# Load data
download_moodle_data()
cohorts = pd.read_csv('data/Cohorts.csv')
english_intake = pd.read_csv('data/Intake Responses - English.csv')
french_intake = pd.read_csv('data/Intake Responses - French.csv')


# Merge cohorts with intake responses to get enrollment counts by cohort and language
english_enrollments = pd.merge(
    cohorts,
    english_intake,
    left_on='Email address',
    right_on='Email',
    how='inner')
english_enrollments = english_enrollments[~english_enrollments['Email address'].str.contains('iecbc.ca')] # filter out test accounts
en_enrollment_count = english_enrollments.groupby('Cohort Name').size()


french_enrollments = pd.merge(
    cohorts,
    french_intake,
    left_on='Email address',
    right_on='Veuillez confirmer votre adresse courriel',
    how='inner')
french_enrollments = french_enrollments[~french_enrollments['Email address'].str.contains('iecbc.ca')] # filter out test accounts
fr_enrollment_count = french_enrollments.groupby('Cohort Name').size()

# Combine english and french enrollment counts into a single dataframe
enrollments = pd.concat([en_enrollment_count, fr_enrollment_count], axis=1, keys=['English', 'French'])

# cast english and french columns as integers and fill NaN with 0
enrollments['English'] = enrollments['English'].fillna(0).astype(int)
enrollments['French'] = enrollments['French'].fillna(0).astype(int)

# Save enrollment counts to csv
last_month = (dt.datetime.now() - pd.DateOffset(months=1)).strftime('%B %Y')
enrollments.to_csv(f'data/cohort_enrollments_{last_month}.csv')