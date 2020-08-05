import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import glob
from tqdm import tqdm_notebook as tqdm

ROOT_DIR = 'data/census/'

def load_census_df(majors=None):
    """
    Loads the admissions dataset, which is stored in data/undergrad-apps/
    in three different folders: applied, admitted, and committed.

    Within each folder is a list of CSV files containing direct exports from 
    CalAnswers (Dashboards => Undergraduate Applications => Academic Year).

    majors is an ARRAY of majors.
    """

    # Load and merge all CSV files into one massive dataframe.
    dfs = []
    for major in majors:
        data = pd.read_csv(ROOT_DIR + major + '.csv')
        data['Major'] = major
        dfs.append(data)
    df = pd.concat(dfs)
    df = df.drop_duplicates()

    rename_dict = {
        'Ucb Level2 Ethnic Rollup Desc': 'Ethnicity L2',
        'Ucb Level1 Ethnic Rollup Desc': 'Ethnicity L1',
        'Short Ethnic Desc': 'Ethnicity L3',
        'Gender Desc': 'Gender',
        'Student Headcount': 'Headcount',
        'Semester Year Name Concat': 'Semester/Year'
    }

    # Print out all the columns.
    print("Columns: ")
    for col in sorted(df.columns):
        if col in rename_dict:
            print(f' • {col} (renamed to: {rename_dict[col]})')
        else:
            print(f' • {col}')

    df = df.rename(columns=rename_dict)

    df = df[['Ethnicity L1', 'Ethnicity L2', 'Ethnicity L3', 'Semester/Year', 'Gender', 'Headcount', 'Academic Yr', 'Major']]

    return df