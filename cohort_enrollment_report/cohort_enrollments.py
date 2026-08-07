#  Downloads monthly report of how many ASCEND enrollments there are in each cohort.
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
english_enrollments['Submitted On'] = pd.to_datetime(english_enrollments['Submitted On'], format='%d-%m-%Y %H:%M:%S')

# Group by cohort and month, then pivot to get a table of counts
en_enrollment_count = english_enrollments.groupby(['Cohort Name', pd.Grouper(key='Submitted On', freq='ME')]).size().reset_index(name='Count')
en_enrollment_count.rename(columns={'Submitted On': 'Month'}, inplace=True)

en_enrollment_count = en_enrollment_count.pivot(index='Cohort Name', columns='Month', values='Count')

french_enrollments = pd.merge(
    cohorts,
    french_intake,
    left_on='Email address',
    right_on='Veuillez confirmer votre adresse courriel',
    how='inner')
french_enrollments = french_enrollments[~french_enrollments['Email address'].str.contains('iecbc.ca')] # filter out test accounts
french_enrollments['Submitted On'] = pd.to_datetime(french_enrollments['Submitted On'], format='%d-%m-%Y %H:%M:%S')

# Group by cohort and month, then pivot to get a table of counts
fr_enrollment_count = french_enrollments.groupby(['Cohort Name', pd.Grouper(key='Submitted On', freq='ME')]).size().reset_index(name='Count')
fr_enrollment_count.rename(columns={'Submitted On': 'Month'}, inplace=True)
fr_enrollment_count = fr_enrollment_count.pivot(index='Cohort Name', columns='Month', values='Count')

# Combine english and french enrollment counts into a single dataframe
# Columns are nested Month > Language, so English/French sit side by side within each month
enrollments = (
    pd.concat(
        [en_enrollment_count, fr_enrollment_count],
        axis=1,
        keys=['English', 'French']
    )
    .swaplevel(0, 1, axis=1)
    .sort_index(axis=1, level=0)
)
enrollments = enrollments.fillna(0).astype(int)

# Rename columns to use Month Year instead of timestamp
enrollments.columns = pd.MultiIndex.from_tuples(
    [(ts.strftime('%B %Y'), lang) for ts, lang in enrollments.columns],
    names=enrollments.columns.names
)


# Save enrollment counts to csv
last_month = (dt.datetime.now() - pd.DateOffset(months=1)).strftime('%B %Y')
enrollments.to_excel(f'reports/cohort_enrollments_{last_month}.xlsx')
