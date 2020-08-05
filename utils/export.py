import os
from dotenv import load_dotenv
import chart_studio
import chart_studio.plotly as py

def setup_chart_studio():
    # The .env file for this project contains my PLOTLY_API_KEY and PLOTLY_USERNAME.
    # This lets us push plots to the Plotly Cloud for easy embedding.
    # To create your Plotly account, follow these instructions: 
    # https://plotly.com/python/getting-started-with-chart-studio/

    load_dotenv()

    PLOTLY_API_KEY = os.getenv('PLOTLY_API_KEY')
    PLOTLY_USERNAME = os.getenv('PLOTLY_USERNAME')

    chart_studio.tools.set_credentials_file(username=PLOTLY_USERNAME, api_key=PLOTLY_API_KEY)
    chart_studio.tools.set_config_file(world_readable=True, sharing='public')