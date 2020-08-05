import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import glob
from tqdm import tqdm_notebook as tqdm

def load_admissions_df(majors=None):
    """
    Loads the admissions dataset, which is stored in data/undergrad-apps/
    in three different folders: applied, admitted, and committed.

    Within each folder is a list of CSV files containing direct exports from 
    CalAnswers (Dashboards => Undergraduate Applications => Academic Year).

    majors is an ARRAY of majors.
    """

    # Load and merge all CSV files into one massive dataframe.
    dfs = []
    for path in ['applied', 'admitted', 'committed']:
        for file in glob.glob(f'data/undergrad-apps/{path}/*.csv'):
            dfs.append(pd.read_csv(file))
    df = pd.concat(dfs)
    df = df.drop_duplicates()

    # Filter on the majors tab first to trim the size of the dataset down.
    if majors is not None:
        df = df[df['Intended Major'].isin(majors)]

    # Rename columns for easier access.
    # Note: all column meanings can be found in the Cal Answers data dictionary.
    rename_dict = {
        'Income Range Amt 2 - Parent': 'Family Income',
        'Applicant Headcounts': 'Headcount',
        'Derived Residency': 'Residency',
        'Ucb Level2 Ethnic Rollup Desc': 'Ethnicity L2',
        'Ucb Level1 Ethnic Rollup Desc': 'Ethnicity L1',
        'Short Ethnic Desc': 'Ethnicity L3',
        'Neither Parent has Attended College': 'First Generation Student',
    }

    # Print out all the columns.
    print("Columns: ")
    for col in sorted(df.columns):
        if col in rename_dict:
            print(f' • {col} (renamed to: {rename_dict[col]})')
        else:
            print(f' • {col}')

    df = df.rename(columns=rename_dict)

    # Drop columns that we won't be analyzing (some of these are actually deprecated).
    df = df.drop(columns=['Neither Parent has 4 Year College Degree', 'High School API Rank', 'LCFF+ Flg'])

    # Drop empty demographic buckets.
    df = df.dropna(subset=['Headcount'])

    # Fill empty Admit/Yield Rate values with 0s (i.e. nobody from the bucket got in)
    df['Admit Rate'] = df['Admit Rate'].fillna(0)
    df['Yield Rate'] = df['Yield Rate'].fillna(0)

    # Clean up column values.
    df['Family Income'] = df['Family Income'].apply(fix_family_income)
    df['First Generation Student'] = df['First Generation Student'].apply(fix_first_gen)
    
    # Split the dataset back into three different components.
    applied = df[~pd.isna(df["('Applied')"])]
    admitted = df[~pd.isna(df["('Admitted')"])]
    committed = df[~pd.isna(df["('SIRed')"])]

    print()
    print('Years Present: ' + ', '.join(np.unique(df['Academic Yr'])) + '\n')
    print(f'Total # Applied:  {sum(applied["Headcount"])} students')
    print(f'Total # Admitted: {sum(admitted["Headcount"])} students')
    print(f'Total # SIRed:    {sum(committed["Headcount"])} students')

    latest_yr = list(sorted(np.unique(df['Academic Yr'])))[-1]
    print()
    print(f'Latest Academic Year (Cross Check This Data with Public Information): {latest_yr}')
    print(f'Total # Applied:  {sum(applied[applied["Academic Yr"] == latest_yr]["Headcount"])} students')
    print(f'Total # Admitted: {sum(admitted[admitted["Academic Yr"] == latest_yr]["Headcount"])} students')
    print(f'Total # SIRed:    {sum(committed[committed["Academic Yr"] == latest_yr]["Headcount"])} students')

    return applied, admitted, committed

def fix_first_gen(s):
    """
    Cleans up the first generation college student column.
    """
    if pd.isna(s): return 'Unknown'
    if s == 'Y': return 'FG'
    elif s == 'N': return 'NFG'
    else: return 'Unknown'
        
def fix_family_income(i):
    """
    Cleans up the family income column.
    """
    if pd.isna(i): return 'Unknown'
    if '60,000' in i: return '$60-80K'
    elif '80,000' in i: return '$80-150K'
    elif '150,000' in i: return '$150K+'
    elif '25,000' in i: return '$25-60K'
    elif '24,999' in i: return '$0-25K'
    else: return 'Unknown'

def group(data, categories):
    """
    Groups data on a category or multiple categories.
    Takes a weighted average of Admit Rate and Yield Rate 
    (since the original dataset represents demographics using bucketing).
    Sums over the Headcount column.
    """
    filtered = data.copy()
    filtered['Admit Rate'] = filtered['Admit Rate'] * filtered['Headcount']
    filtered['Yield Rate'] = filtered['Yield Rate'] * filtered['Headcount']
    filtered = filtered[filtered['Headcount'] != 0]
    weighted_average = lambda x: round(sum(x) / sum(filtered.loc[x.index, "Headcount"]), 2)
    filtered = filtered.groupby(categories).agg({
        'Admit Rate': weighted_average,
        'Yield Rate': weighted_average,
        'Headcount': 'sum'
    }).reset_index()
    return filtered