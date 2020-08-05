import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import glob
from tqdm import tqdm_notebook as tqdm
from tabulate import tabulate

def write_table(frames, category, title, file_name, year, write=False, write_folder=''):
    text = title
    for name, data in frames.items():
        data = group(data[data['Academic Yr'] == year], [category])
        totals = sum(data['Headcount'])
        calculate_percentage = lambda row : 100 * (row.get('Headcount') / totals)
        data['Percentage'] = data.apply(calculate_percentage, axis=1)
        data = data[[category, 'Headcount', 'Percentage']]
        text += '\n' * 4 + '-' * 70 + f'\n{name.upper()}\n' + '-' * 70 + '\n'
        data = data.sort_values('Percentage')
        text += tabulate(data, headers=data.columns)

    text = text + '\n' * 3
    if not write: print(text)
    else:
        with open(write_folder + file_name, 'w') as file: 
            file.write(text)

def plot_line_graph(frames, column, title, file_name, write, write_folder, publish, publish_prefix, categories=['Applied', 'Admitted', 'Committed']):
    fig = go.Figure()
    for name, data in frames.items():
        if name not in categories: continue
        data = data.groupby(['Academic Yr', column]).sum().reset_index()

        totals = data.groupby('Academic Yr').sum()['Headcount']
        calculate_percentage = lambda row : 100 * (row.get('Headcount') / totals[row.get('Academic Yr')])
        data['Percentage'] = data.apply(calculate_percentage, axis=1)

        for category in np.unique(data[column]):
            filtered = data[data[column] == category]
            fig.add_trace(go.Scatter(
                mode='lines+markers',
                x=filtered['Academic Yr'],
                y=filtered['Percentage'],
                name=f'{name} ({category})',
                hoverlabel={
                    'namelength': -1
                }
            ))
    
    style_figure(fig, title=title, x_title='Academic Year', y_title='Percentage')
    if not write: fig.show()
    else: fig.write_html(write_folder + file_name + '.html', include_plotlyjs='cdn')
    if publish: py.plot(fig, filename=publish_prefix + file_name, auto_open=True)

        

def style_figure(fig, title, x_title, y_title):
    if title is not None:
        fig.update_layout({'title': title, 'xaxis_title': x_title, 'yaxis_title': y_title})
    fig.update_layout({'xaxis_type': 'category'})
    fig.update_layout({'plot_bgcolor': '#f9f9f9'})
    fig.update_layout({'font_family': 'Avenir Next', 'font_color': 'black'})

def group(data, categories):
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



def plot_treemap(data, title, path, top_level, file_name, year, color_col, write, write_folder, publish, publish_prefix): 
    data = data.copy()    
    
    path = [px.Constant(top_level)] + path

    # Filter by year.
    data = data[data['Academic Yr'] == year]
    
    # Group by columns in path.
    cols = path[1:]
    filtered = group(data, cols) 

    # Calculate Percentages.    
    total = data.groupby('Academic Yr').sum()['Headcount']
    calculate_percentage = lambda row : 100 * (row.get('Headcount') / total)
    filtered['Percentage'] = filtered.apply(calculate_percentage, axis=1)    
    
    # Convert Admit Rate into Percentage.
    filtered['Admit Rate'] = filtered['Admit Rate'].apply(lambda x : x / 100)
    
    if color_col == 'Headcount':        
        fig = px.treemap(filtered, 
                         path=path, 
                         values='Headcount', 
                         color=color_col, 
                         hover_data={'Admit Rate': True, 'Percentage': True}, 
                         color_continuous_scale='BuGn')
        
    elif color_col == 'Admit Rate':
        fig = px.treemap(filtered, 
                         path=path, 
                         values='Headcount', 
                         color=color_col, 
                         color_continuous_scale='OrRd',
                         hover_data={'Admit Rate': True, 'Percentage': True}, )
    
    fig.update_layout({'font_family': 'Avenir Next', 'font_color': 'black'})
    fig.update_layout(margin={'b': 10})
    fig.update_layout(title={'text': title, 'x': 0.5, 'y': 0.97, 'xanchor': 'center', 'yanchor': 'top'})
    
    fig._data_objs[0].hovertemplate = '%{id}<br><br>' + \
                                      'Headcount: %{value}<br>' + \
                                      'Fraction of Total: %{percentRoot:.2f}<br>' + \
                                      'Fraction of Parent: %{percentParent:.2f}<br>' + \
                                      'Admit Rate: %{customdata[0]:.2f}'
    
    if not write: fig.show()
    else: fig.write_html(write_folder + file_name + '.html', include_plotlyjs='cdn')
    if publish: py.plot(fig, filename=publish_prefix + file_name, auto_open=False)