#!/usr/bin/env python
# coding: utf-8

# In[1]:


# This is code for visualizations in article U.S. Refinery Processing, over the Years


# In[2]:


# (1) Import needed packages

import tabula
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as pg
import chart_studio.plotly as py


# In[3]:


# (2) Import necessary data from pdf report of U.S. refinery capacity and .csv from the Energy Information Administration,'
# with history on refinery capacity going back to 1985. Let's also import list of refineries and capacity by state

data = tabula.read_pdf("Refinery Capacity Report.pdf", pages='all')
capacitydata = pd.read_csv('List Of Refineries.csv')
refineriesbystate = pd.read_csv("Refineries By States.csv")


# In[4]:


# (3) Explore data and complete pre-processing, cleaning

capacitydata.drop(columns='Unnamed: 17', inplace=True)

capacitydata.isnull().sum()  
# One entry to be dropped.

capacitydata.dropna(inplace=True)


# In[5]:


capacitydata = capacitydata.drop(columns=[
    'Refining District East Coast Refinery District Gross Inputs to Refineries (Thousand Barrels Per Day)',
    'Appalachian No. 1 Refinery District Gross Inputs to Refineries (Thousand Barrels Per Day)',
    'Indiana, Illinois, Kentucky Refinery District Gross Inputs to Refineries (Thousand Barrels Per Day)',
    'Minnesota, Wisconsin, North and South Dakota Refinery District Gross Inputs to Refineries (Thousand Barrels Per Day)',
    'Refining District Oklahoma-Kansas-Missouri Gross Inputs to Atmospheric Crude Oil Distillation Units (Thousand Barrels per Day)',
    'Refining District New Mexico Gross Inputs to Atmospheric Crude Oil Distillation Units (Thousand Barrels per Day)'
])


# In[6]:


# We know all numbers are kbd feed to refineries, so drop excess detail to make titles cleaner.
capacitydata = capacitydata.rename(
    {
        "U.S. Gross Inputs to Refineries (Thousand Barrels Per Day)":
        "Gross refinery input (kbd)",
        "East Coast (PADD 1) Gross Inputs to Atmospheric Crude Oil Distillation Units (Thousand Barrels per Day)":
        "PADD 1",
        "Midwest (PADD 2) Gross Inputs to Refineries (Thousand Barrels Per Day)":
        "PADD 2",
        "Gulf Coast (PADD 3) Gross Inputs to Refineries (Thousand Barrels Per Day)":
        "PADD 3",
        "Texas Inland Refinery District Gross Inputs to Refineries (Thousand Barrels Per Day)":
        "Texas Inland",
        "Refining District Texas Gulf Coast Gross Inputs to Atmospheric Crude Oil Distillation Units (Thousand Barrels per Day)":
        "Texas GC",
        "Louisiana Gulf Coast Refinery District Gross Inputs to Refineries (Thousand Barrels Per Day)":
        "LA",
        "Rocky Mountains (PADD 4) Gross Inputs to Refineries (Thousand Barrels Per Day)":
        "PADD 4",
        "West Coast (PADD 5) Gross Inputs to Refineries (Thousand Barrels Per Day)":
        "PADD 5",
        "Refining District North Louisiana-Arkansas Gross Inputs to Refineries (Thousand Barrels per Day)":
        "N.LA-ARK"
    },
    axis='columns')


# In[7]:


# (3.a) We've cleaned titles and dropped columns that expand on PADD regions, since we're currently interested only in'
# overall PADD numbers. Since we're focused only on capacity and location, let's create a new dataframe with only that info


# In[8]:


capacitybystate = refineriesbystate.loc[:, [
    "STATE_NAME", "QUANTITY", 'PRODUCT', 'SUPPLY'
]]

#The capacitybystate dataframe has a lot of detail unrelated to refinery crude feed capacity, so let's focus on that.

FeedCapacityByState = capacitybystate[capacitybystate.PRODUCT.str.contains(
    'TOTAL OPERABLE CAPACITY')]


# In[9]:


FeedCapacityByState.head()


# In[10]:


# (3.b) We're interested in understanding capacity by state, so group all states together.

FeedCapacityByState = FeedCapacityByState.groupby(
    FeedCapacityByState['STATE_NAME']).aggregate({
        'QUANTITY': 'sum'
    }).reset_index()

# We'll eventually want to use the chloropeth U.S. state map to plot capacity, which uses two-letter abbreviations for'
# states rather than the whole name. Map state names using the us_state_abbrev dictionary on github

get_ipython().run_line_magic('run', 'us_state_abbrev.ipynb')
FeedCapacityByState['STATE_NAME'] = FeedCapacityByState['STATE_NAME'].map(
    us_state_abbrev)


# In[11]:


fig = pg.Figure(data=pg.Choropleth(
    locations=FeedCapacityByState['STATE_NAME'],
    z=FeedCapacityByState['QUANTITY'],
    locationmode='USA-states',
    colorscale='Reds',
    colorbar_title="KBD",
))

fig.update_layout(
    title_text='January 2019 U.S. Refinery Processing Capacity',
    geo_scope='usa',  # limit map scope to USA
)

fig.update_annotations(FeedCapacityByState['QUANTITY'])

fig.show()


# In[12]:


# Some interesting insights there. Texas and Louisiana clearly bear the burden of refining capacity in the U.S., followed
# at some distance by California. Just how dependent is U.S. refining capacity on PADD 3 refining capacity?


# In[13]:


# 4) Adjusting capacitydata refinery input units of measurement, to make numbers smaller on subsequent graph axes.

capacitydata['Gross refinery input (million bpd)'] = capacitydata[
    'Gross refinery input (kbd)'] / 1000
capacitydata = capacitydata.drop(columns='Gross refinery input (kbd)')

# Set date as index

capacitydata = capacitydata.set_index('Date')  #Set date as index


# In[14]:


from plotly.subplots import make_subplots

fig = make_subplots(specs=[[{"secondary_y": True}]])
x = capacitydata.loc[:, 'Gross refinery input (million bpd)']
x1 = capacitydata.loc[:, 'PADD 1']
x2 = capacitydata.loc[:, 'PADD 2']
x3 = capacitydata.loc[:, 'PADD 3']
x4 = capacitydata.loc[:, 'PADD 4']
x5 = capacitydata.loc[:, 'PADD 5']

fig.add_trace(
    pg.Scatter(x=x.index, y=x.values, name="U.S. wide - million bbl/day"))
fig.add_trace(pg.Scatter(x=x3.index, y=x3.values, name="PADD 3 - kbd"),
              secondary_y=True)
fig.add_trace(pg.Scatter(x=x5.index, y=x3.values, name="PADD 5 - kbd"),
              secondary_y=True)

fig.update_layout(title="Refinery inputs over the years",
                  yaxis_title="U.S. wide refining input, million bbl/day")


# In[15]:


# The x-axis doesn't specify Feb 2020, but that's the end of the scale. Key take-away is that U.S. has continued to
# refine more crude over the years - in the last 35 years, total refinery input has increased by 41%.


# In[16]:


#Just how well correlated or how dependent is U.S. refining capacity on PADD 3 refinery input?

fig2 = plt.figure(figsize=(8, 8))
fig2 = plt.scatter(x3.values, x.values, marker='o')
figu2 = plt.title(
    'PADD 3 (Gulf Coast) refinery input vs. Nationwide refinery inputs')
z = np.polyfit(x3.values, x.values, 1)
p = np.poly1d(z)
plt.plot(x3.values, p(x3.values), c='b')
plt.xlabel('PADD 3 refinery input, kbd'), plt.ylabel(
    'Nationwide refinery input, million bbl/d')


# In[17]:


# We notice an appreciable linear correlation in the trend above of PADD 3 input vs. U.S.-wide refinery input

