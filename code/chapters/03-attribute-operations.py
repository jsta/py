# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Attribute data operations {#attr}
#
# ## Prerequisites

#| echo: false
import pandas as pd
import matplotlib.pyplot as plt
pd.options.display.max_rows = 6
pd.options.display.max_columns = 6
pd.options.display.max_colwidth = 35
plt.rcParams['figure.figsize'] = (5, 5)

# Packages...

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import rasterio

# Sample data...

#| echo: false
from pathlib import Path
data_path = Path('data')
file_path = Path('data/landsat.tif')
if not file_path.exists():
  if not data_path.is_dir():
     os
     os.mkdir(data_path)
  import os
  print('Attempting to get the data')
  import requests
  r = requests.get('https://github.com/geocompr/py/releases/download/0.1/landsat.tif')  
  with open(file_path, 'wb') as f:
    f.write(r.content)

world = gpd.read_file('data/world.gpkg')
src_elev = rasterio.open('data/elev.tif')
src_multi_rast = rasterio.open('data/landsat.tif')

# ## Introduction
#
# ...
#
# ## Vector attribute manipulation
#
# As mentioned previously (...), vector layers (`GeoDataFrame`, from package `geopandas`) are basically extended tables (`DataFrame` from package `pandas`), the difference being that a vector layer has a geometry column. Since `GeoDataFrame` extends `DataFrame`, all ordinary table-related operations from package `pandas` are supported for vector laters as well, as shown below.
#
# ### Vector attribute subsetting {#sec-vector-attribute-subsetting}
#
# `pandas` supports several subsetting interfaces, though the most [recommended](https://stackoverflow.com/questions/38886080/python-pandas-series-why-use-loc) ones are:
#
# * `.loc`, which uses pandas indices, and
# * `.iloc`, which uses (implicit) numpy-style numeric indices.
#
# In both cases the method is followed by square brackets, and two indices, separated by a comma. Each index can comprise:
#
# * A specific value, as in `1`
# * A slice, as in `0:3`
# * A `list`, as in `[0,2,4]`
# * `:`—indicating "all" indices
#
# The once exception which we are going to with subsetting by indices is when selecting columns, directly using a list, as in `df[['a','b']]`, instead of `df.loc[:, ['a','b']]`, to select columns `'a'` and `'b'` from `df`.
#
# Here are few examples of subsetting the `GeoDataFrame` of world countries.
#
# Subsetting rows by position:

world.iloc[0:3, :]

# Subsetting columns by position:

world.iloc[:, 0:3]

# Subsetting rows and columns by position:

world.iloc[0:3, 0:3]

# Subsetting columns by name:

world[['name_long', 'geometry']]

# "Slice" of columns between given ones:

world.loc[:, 'name_long':'pop']

# Subsetting by a boolean series:

x = np.array([1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0], dtype=bool)
world.iloc[:, x]

# We can remove a specific row by id use the `.drop` method:

world.drop([2, 3, 5])

# Or remove specific columns using the `.drop` method and `axis=1` (i.e., columns):

world.drop(['name_long', 'continent'], axis=1)

# We can rename (some of) the selected columns using the `.rename` method:

world[['name_long', 'pop']].rename(columns={'pop': 'population'})

# The standard `numpy` comparison operators can be used in boolean subsetting, as illustrated in Table ...
#
# TABLE ...: Comparison operators that return Booleans (TRUE/FALSE).
#
# |`Symbol` | `Name` |
# |---|---|
# | `==` | Equal to |
# | `!=` | Not equal to |
# | `>`, `<` | Greater/Less than |
# | `>=`, `<=` | Greater/Less than or equal |
# | `&`, `|`, `~` | Logical operators: And, Or, Not |
#
# A demonstration of the utility of using logical vectors for subsetting is shown in the code chunk below. This creates a new object, small_countries, containing nations whose surface area is smaller than 10,000 km^2^:

idx_small = world['area_km2'] < 10000  ## a logical 'Series'
small_countries = world[idx_small]
small_countries

# The intermediary `idx_small` (short for index representing small countries) is a boolean `Series` that can be used to subset the seven smallest countries in the world by surface area. A more concise command, which omits the intermediary object, generates the same result:

small_countries = world[world['area_km2'] < 10000]

# The various methods shown above can be chained for any combination with several subsetting steps. For example:

world[world['continent'] == 'Asia']  \
    .loc[:, ['name_long', 'continent']]  \
    .iloc[0:5, :]

# We can also combine indexes

idx_small = world['area_km2'] < 10000
idx_asia = world['continent'] == 'Asia'
world.loc[idx_small & idx_asia, ['name_long', 'continent', 'area_km2']]

# ### Vector attribute aggregation
#
# Aggregation involves summarizing data with one or more *grouping variables*, typically from columns in the table to be aggregated (geographic aggregation is covered in the next chapter). An example of attribute aggregation is calculating the number of people per continent based on country-level data (one row per country). The `world` dataset contains the necessary ingredients: the columns `pop` and `continent`, the population and the grouping variable, respectively. The aim is to find the `sum()` of country populations for each continent, resulting in a smaller data frame (aggregation is a form of data reduction and can be a useful early step when working with large datasets). This can be done with a combination of `.groupby` and `.sum`:

world_agg1 = world[['continent', 'pop']].groupby('continent').sum()
world_agg1

# The result is a (non-spatial) table with eight rows, one per continent, and two columns reporting the name and population of each continent.
#
# Alternatively, to include the geometry in the aggregation result, we can use the `.dissolve` method. That way, in addition to the summed population we also get the associated geometry per continent, i.e., the union of all countries. Note that we use the `by` parameter to choose which column(s) are used for grouping, and the `aggfunc` parameter to choose the summary function for non-geometry columns:

world_agg2 = world[['continent', 'pop', 'geometry']] \
    .dissolve(by='continent', aggfunc='sum')
world_agg2

# Here is a plot of the result:

world_agg2.plot(column='pop');

# The resulting `world_agg2` object is a vector layer containing 8 features representing the continents of the world (and the open ocean). 
#
# Other options for the `aggfunc` parameter in `.dissolve` [include](https://geopandas.org/en/stable/docs/user_guide/aggregation_with_dissolve.html):
#
# * `'first'`
# * `'last'`
# * `'min'`
# * `'max'`
# * `'sum'`
# * `'mean'`
# * `'median'`
#
# Additionally, we can pass a custom functiom.
#
# For example, here is how we can calculate the summed population, summed area, and count of countries, per continent. We do this in two steps, then join the results:

world_agg3a = world[['continent', 'area_km2', 'geometry']] \
    .dissolve(by='continent', aggfunc='sum')
world_agg3b = world[['continent', 'name_long', 'geometry']] \
    .dissolve(by='continent', aggfunc=lambda x: x.nunique()) \
    .rename(columns={'name_long': 'n'})
world_agg = pd.merge(world_agg3a, world_agg3b, on='continent')

# ...
#
# ### Vector attribute joining {#sec-vector-attribute-joining}
#
# Combining data from different sources is a common task in data preparation. Joins do this by combining tables based on a shared 'key' variable. `pandas` has a function named `pd.merge` for joining tables or vector layers based on common column(s). The `pd.merge` function follows conventions used in the database language SQL (Grolemund and Wickham 2016). Using `pd.merge` to join non-spatial datasets to vector layers is the focus of this section. The `pd.merge` function works the same on tables (`DataFrame`) and vector layer (`GeoDataFrame`) objects, the only important difference being the presence of the geometry column (which is not involved in the join operation anyway). The result of data joins can be either a `DataFrame` or a `GeoDataFrame` object, depending on the inputs. The most common type of attribute join on spatial data takes a `GeoDataFrame` object as the first argument and adds columns to it from a `DataFrame` specified as the second argument.
#
# To demonstrate joins, we will combine data on coffee production with the `world` dataset. The coffee data is in a `DataFrame` called `coffee_data` imported from a CSV file. It has 3 columns: 
#
# * `name_long` names major coffee-producing nations
# * `coffee_production_2016` and `coffee_production_2017` contain estimated values for coffee production in units of 60-kg bags in each year. 

coffee_data = pd.read_csv('data/coffee_data.csv')
coffee_data

# A left join, which preserves the first dataset, merges `world` with `coffee_data`, based on the common `'name_long'` column:

world_coffee = pd.merge(world, coffee_data, on='name_long', how='left')
world_coffee

# The result is a `GeoDataFrame` object identical to the original `world` object, but with two new variables (`coffee_production_2016` and `coffee_production_2017`) on coffee production. This can be plotted as a map, as illustrated in @fig-join-coffee-production:

# +
#| label: fig-join-coffee-production
#| fig-cap: World coffee production (thousand 60-kg bags) by country in 2017 (source International Coffee Organization).

base = world.plot(color='white', edgecolor='lightgrey')
world_coffee.plot(ax=base, column='coffee_production_2017');
# -

# For joining to work, a 'key variable' must be supplied in both datasets. In this case, both `world_coffee` and world objects contained a variable called `name_long`. By default `pd.merge` uses all variables with matching names. However, it is recommended to explicitly specify the names of the columns to be used for matching, like we did in the last example. 
#
# In case where variable names are not the same, you need to rename (using `.rename`) them so that it is, then proceed with the join.
#
# Note that the result `world_coffee` has the same number of rows as the original dataset `world`. Although there are only 47 rows of data in `coffee_data`, all 177 country records are kept intact in `world_coffee`: rows in the original dataset with no match are assigned `np.nan` values for the new coffee production variables. This is characteristic of a lift join (specified with `how='left'`) and is what we typically want to do. 
#
# What if we only want to keep countries that have a match in the key variable? In that case an inner join can be used:
#
#
#
# ### Creating attributes and removing spatial information
#
# Calculate new column...

world2 = world.copy()
world2['pop_dens'] = world2['pop'] / world2['area_km2']

# Unite columns...

world2['con_reg'] = world['continent'] + ':' + world2['region_un']
world2 = world2.drop(['continent', 'region_un'], axis=1)

# Split column...

world2[['continent', 'region_un']] = world2['con_reg'] \
    .str.split(':', expand=True)

# Rename...

world2.rename(columns={'name_long': 'name'})

# Renaming all columns...

new_names =['i', 'n', 'c', 'r', 's', 't', 'a', 'p', 'l', 'gP', 'geom']
world.columns = new_names

# Reordering columns, for example reverse alphabetical order...

names = sorted(world.columns, reverse=True)
world2 = world[names]
world2

# Dropping geometry...

pd.DataFrame(world.drop(columns='geom'))

# ## Manipulating raster objects
#
# ### Raster subsetting
#
# When using `rasterio`, raster values are accessible through a `numpy` array, which can be imported with the `.read` method:

elev = src_elev.read(1)
elev

# Then, we can access any subset of cell values using `numpy` methods. For example:

elev[0, 0]  ## Value at row 1, column 1

# Cell values can be modified by overwriting existing values in conjunction with a subsetting operation. The following expression, for example, sets the upper left cell of elev to 0:

elev[0, 0] = 0
elev

# Multiple cells can also be modified in this way:

elev[0, 0:2] = 0
elev

# ### Summarizing raster objects
#
# Global summaries of raster values can be calculated by applying `numpy` summary functions---such as `np.mean`---on the array with raster values. For example:

np.mean(elev)

# Note that "No Data"-safe functions--such as `np.nanmean`---should be used in case the raster contains "No Data" values which need to be ignored:

elev[0, 2] = np.nan
elev

np.mean(elev)

np.nanmean(elev)

# Raster value statistics can be visualized in a variety of ways. One approach is to "flatten" the raster values into a one-dimensional array, then use a graphical function such as `plt.hist` or `plt.boxplot` (from `matplotlib.pyplot`). For example:

x = elev.flatten()
plt.hist(x);

# ## Exercises
#
