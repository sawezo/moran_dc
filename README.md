# Moran's DC: Exploring Spatial Autocorrelation at the Nation's Capitol


Autocorrelation is an important concept in statistics, and often needs to be accounted for when creating models. Simply put, autocorrelation can be defined as the correlation of some effect with a lagged copy of itself as a function of this lag. Informally, it is the similarity between observations as a function of the time lag between them.[1]

Autocorrelation isn't always one-dimensional (e.g. a time series). For example, spatial autocorrelation is a correlation in a signal among nearby locations in a multidimensional space. Due to the multiple dimensions, it can be more difficult to account for and understand, but can also provide novel insights. For these reasons, spatial autocorrelation is going to be the topic of this post, which will explore some of the foundational aspects of the calculation through a case study of community health in Washington DC.

community distress index going to be compared with spatial autocorrelation

To see the notebooks and code used to make all figures and implement the comparison, check out the corresponding github repository at https://github.com/sawezo/moran_dc

## Community Distress Index

The Economic Innovation Group serves as a great example overview of what we can do with the Census data we are pulling. The EIG focuses on a custom community distress index, which we could calculate or use as a general template for making our own meaningful aggregative community measures for analysis. The DCI exploration ([DCI]) studies data from the 5 Year ACS over the following seven DCI Variables:

- <b>No high school diploma</b>: Percent of the 25+ population without a high school diploma or equivalent.
- <b>Housing vacancy rate</b>: Percent of habitable housing that is unoccupied, excluding properties that are for seasonal, recreational, or occasional use.
- <b>Adults not working</b>: Percent of the prime-age population (25-64) not currently in work.
- <b>Poverty rate</b>: Percent of the population living under the poverty line.
- <b>Median income ratio</b>: Median household income as a percent of the state’s median household income (to account for cost of living differences across states).
- <b>Change in employment</b>: Percent change in the number of jobs.
- <b>Change in establishments</b>: Percent change in the number of business establishments.

The index is calculated by ranking units per each variable, averaging the ranks, and then normalizing the average to a percentile (see [DCI_methodology]). The communities are then grouped into quintiles and labeled (distressed, etc.). They also grouped study units (zip codes) into three population density categories (rural, suburban and urban) so that each is comprised of a third of the data used.  

## The Data

As a result, I decided we should follow suit of the DCI and use ACS 5 year survey data, which has finer geographies. In addition, the ACS 5 data is more reliable/accurate in its estimates than the AC1 data. I found that the only remaining geographies that were available in both the ACS 5 year survey and the TIGER data. American Community 5 Year survey at the Block Group level from the year 2018.

With the geography and survey selection out of the way, I now look to identify some initial features of interest to ping for in our calls. There are tens of thousands of Census Bureau variables, but the selected survey (which was chosen for us by the geography selection as explained above) whittles down our options a good amount and makes this process a little easier for us.

To start, I take inspiration from the DCI ([DCI](https://eig.org/dci)) and identified variables that matched these closely. Notably, many variables can be further broken down (high school degree attainment per individual races, etc.), but I kept the variables high-level for now to keep the initial data and associated API calls simple. Here are some selected current variables again, with the approximate corresponding census variables/descriptions I was able to find listed under each. Note all variables were ensured to exist over both 2013 and 2018 data.

- No high school diploma rate

  :

  - `B15003_017E`: Estimated total with a regular high school diploma aged 25+.
  - divide by `B01003_001E`- total population (used to calculate rates)

- Housing vacancy rate

  : Percent of habitable housing that is unoccupied, excluding properties that are for seasonal, recreational, or occasional use. This feature in particular was deemed a good indicator of DCI status.

  - `B25004_001E`: Total Estimate vacancy status.
  - `B25004_006E`: Total estimate for seasonal, recreational or occasional usage.
  - dividing by `B01003_001E`- total population (used to calculate rates)

- Median household income 

  - `B19013_001E`: Median household income in the past 12 months (in 2017 inflation-adjusted dollars)

Followed DCI to make my own metric with categories:

```
Prosperous, At Risk, Worst, Decent
```



## Spatial Autocorrelation

Spatial autocorrelation refers to the combination of two types of similarity:

1. spatial similarity
2. attribute similarity

These two similarities are combined to get an idea of how much a target feature changes over in a region with respect to itself (ie autocorrelation). The fundamental objective is to visualize and statistically quantify a relationship between the target feature and geography.

using median_hh_income for example

First I will calculate spatial similarity by using the queen contiguity weight in particular, which checks if an adjacency relationship exists between two polygons (if a pair shares an edge or vertex).

Now that we have measured similarity with respect to the spatial region, we are ready to measure it with respect to the target feature. 

This is calculated (for each district $i$) as:
$y_{\text{lag }i} = \sum_j w_{i, j} y_j$

where $w_{i, j}$ is a matrix of the spatial weights (row-standardized if continuous) that we just calculated above.

Mathematically, this is the <b>weighted sum of neighboring-district target feature values</b>.



spatial lag

We should expect to see a change in the range (due to calculations when lagging the raw values) and a shift in the colors of some districts. It is expected that any high values (red in color) will 'spread' to the neighboring districts (think of it as ironing them out).



Above is a nice visual, but we still need to compare the two versions of the target (raw and spatially lagged) statistically to draw more reliable conclusions.

To recap, we now have calculated the raw target values versus the weighted sum of the target with respect to each area's neighborhood (the lagged target values). To see if the geospatial aspect of this data affects the target variable distribution, we statistically compare these two versions of the target feature.



#### Global Autocorrelation

To start, we compare the target feature over the scope of the entire map, with the ambition of discovering any geographical clusters that exist.

In this case, we have null hypothesis: 
- $H_0$: the data is completely spatially random (CSR)/no spatial autocorrelation. 

I will use Moran's I test to measure the correlation between a feature (raw target or lagged target) and the geographical space.

This statistic 𝑖 𝜖 [−1,1]i ϵ [−1,1], where -1 is perfect dispersion (think of a chess board) and perfect separation (one half white, the other black, for example). A value of 0 is random.

```
i = 0.61
```

simulation

We will take a computational approach (I found multiple sources describing that, due to the variability in geographical structures, analytical approaches to spatial autocorrelation are very unreliable).

Here we assume the target feature to be distributed CSR. We then calculate a Moran's I statistic, and build up a distribution of statistics by repeating this process. Then we see where our actual calculated statistic falls relative to this distribution to calculated a significance value respective to the CSR hypothesis.

simulation

p sim = 0.0001

If we reject the null hypothesis/with a significant p-value, we can conclude the target feature distribution is not spatially random, and that there is a signficant spatial association relative to Dodoma region districts.

Recall this result applies to the map as a whole, as it is the **global** spatial autocorrelation.



#### Local Autocorrelation

Whereas global autocorrelation can be interpreted as finding overall clustering of the target feature distribution relative to a region, the local autocorrelation looks to identify specific local clusters themselves. It is very similar to the above, only we perform a similar procedure over every individual geometric polygon (district) and get a significance measure for each. We can further put significant findings in context by turning to a local analysis where the attention shifts to detection of spatially correlated districts and spatial outliers.


Mathematically, the local Moran's I is simply the product of the target feature value and its spatial lag at a particular location (district). As a result, the global Moran's I we calculated above is the average rate of change of the local statistics. 


As before, here I take the computational approach (as the analytical is very unreliable for a small sample size like we have), which looks to use conditional permutations for each location. The conditional part here means I hold out the target feature observation at a particular location $i$ (to avoid additional spatial dependency), and then randomly shuffle the remaining values before computing the local Moran value. This builds up a simulated reference distribution, <b>which I do for each individual location</b>.

From here, we get determine if each district is locally significant in terms of the target feature distribution, relative to the other districts. To make this result more interpretable, I group findings according to the quadrant of the Moran's I scatterplot they come from; this is explained in much more detail below.

To recap and put this all in context, the main objective here is to identify specific areas in the region that are driving overall patterns observed in the target feature.





morans scatterplot

The interpretation of the above is as follows: We have essentially taken an array of local Moran's i statistics instead of a single global I like we did earlier (which would be the slope of the red regression line above).

By using the mean dividing lines of each axis (the raw feature value and spatially lagged feature values), we divide the two dimensional space into four quadrants. Each quadrant has a characteristic we may be interested in characterizing a district by:

- 1

   

  (top right)

  :

  - there is a spatial association here (+, +)
  - points represent districts with high average target feature value surrounded by districts that also have high average
  - for simplicity, these will be referenced as 'diamond diamond'

- 2

   

  (top left)

  :

  - there is no spatial association here
  - points represent districts with low average target feature value, but surrounded by districts with high average
  - for simplicity, these will be referenced as 'rough in the diamonds'

- 3

   

  (bottom left)

  :

  - there is a spatial association here (-, -)
  - points represent districts with low average target feature value surrounded by districts that also have a low average
  - for simplicity, these will be referenced as 'rough rough'

- 4

   

  (bottom right)

  :

  - there is no spatial association here
  - points represent districts with high average target feature value, but are surrounded by districts with low average
  - for simplicity, these will be referenced as 'diamonds in the rough'

In technical terms, we can group these four quadrants into two supgroups:

1. spatial clusters: quadrants one and three, where there is a spatial correlation (positive or negative)
2. spatial outliers: quadrants two and four





### Comparison






[DCI]: https://eig.org/dci
[DCI_methodology]: https://eig.org/dci/methodology
[1]: https://en.wikipedia.org/wiki/Autocorrelation

- http://darribas.org/gds_scipy16/ipynb_md/04_esda.html [article on exploratory spatial analysis]
- https://readthedocs.org/projects/splot/downloads/pdf/stable/ [pysal documentation with methods, pg. 25: weight transformations, pg. 26: spatial lag, pg. 39: Moran's I, local Moran's I: 43]
- https://www.youtube.com/watch?v=_SmNHt4r79k [lecture on local autocorrelation]
- https://www.youtube.com/watch?v=kJXUUO5M4ok (@1:58:00) [public talk on spatial analysis statistics]
- https://towardsdatascience.com/walkthrough-mapping-basics-with-bokeh-and-geopandas-in-python-43f40aa5b7e9 [Bokeh interactive map with spatial data]