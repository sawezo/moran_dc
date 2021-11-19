# geospatial
import esda
import libpysal as lp


def get_spatial_weights(df):
    spatial_weights = lp.weights.Queen.from_dataframe(df)
    spatial_weights.transform = 'r' # row-standardizing
    return spatial_weights

def get_lagged_y(spatial_weights, y):
    return lp.weights.lag_spatial(spatial_weights, y)

def moran_rate_test(population_array, base_feature_name, event_variable_array, spatial_weights):
    morans_i_test = esda.moran.Moran_Rate(event_variable_array, population_array, spatial_weights, 
                                            permutations=9999)
    local_i_stats = esda.moran.Moran_Local_Rate(event_variable_array, population_array, 
                                                            spatial_weights, permutations=9999)   

    return morans_i_test, local_i_stats                                                                

def moran_test(y, spatial_weights):
    morans_i_test = esda.moran.Moran(y, spatial_weights, transformation="r", permutations=9999)
    local_i_stats = esda.moran.Moran_Local(y, spatial_weights, transformation="r", 
                                                    permutations=9999)
    return morans_i_test, local_i_stats                                            

def get_global_results(morans_i_test):
    global_i_statistic = round(morans_i_test.I, 3) # test statistic
    global_i_p = morans_i_test.p_sim
    return global_i_statistic, global_i_p

def get_sig_area_quadrants(local_i_stats, alpha):
    sig_sim_stats = 1*(local_i_stats.p_sim < alpha) 
    diamond_diamond = 1*(sig_sim_stats*local_i_stats.q==1)
    rough_in_diamonds = 2*(sig_sim_stats*local_i_stats.q==2)
    rough_rough = 3*(sig_sim_stats*local_i_stats.q==3)
    diamonds_in_rough = 4*(sig_sim_stats*local_i_stats.q==4)
    combined_spots = diamond_diamond+rough_in_diamonds+rough_rough+diamonds_in_rough

    # format as text for plotting
    label_text = ["No Significance", "Q1: (+, +)", "Q2: (-, +)", "Q3: (-, -)", "Q4: (+, -)"]
    quadrant_labels = local_i_stats.q # list of areas and their Moran's i quadrant
    sig_quadrant_labels = [label_text[i] for i in combined_spots]    

    return quadrant_labels, sig_quadrant_labels

def calculate_moran_for_feature(df, target_feature, rate, alpha=0.05):
    """
    Calculate Moran's statistic for a single feature.
    """
    # calculate spatial weights/lagged feature
    spatial_weights = get_spatial_weights(df)
    y_lag = get_lagged_y(spatial_weights, df[target_feature])


    # global and local autocorrelation computational testing (differs if feature is a proportion)
    if rate == True: # The target is expressed as a rate.
        population_array = df["population"] # the population-at-risk variable across each of the n spaces
        base_feature_name = target_feature.split("_NORMED")[0]
        event_variable_array = df[base_feature_name] # the raw count by district, not normalized
        morans_i_test, local_i_stats = moran_rate_test(population_array, base_feature_name, event_variable_array, spatial_weights)
    elif rate == False: # the target is expressed as a proportion over a uniform total
        morans_i_test, local_i_stats = moran_test(df[target_feature], spatial_weights)
    

    # global testing results
    global_i_statistic, global_i_p = get_global_results(morans_i_test)


    # get list of locally significant get significant quadrant regions
    quadrant_labels, sig_quadrant_labels = get_sig_area_quadrants(local_i_stats, alpha)

    return quadrant_labels, sig_quadrant_labels, local_i_stats.Is, y_lag

def get_moran_features_for_col(df, feature, alpha=0.05):
    """function calculates and formats moran's statistics features 

    Args:
        df (pandas dataframe): pandas dataframe to add the moran features to.
        feature (string): column to test 
        alpha (float): significance to test against. Defaults to 0.05.

    Returns:
        df: pandas dataframe with new features
    """

    rate = True if "rate" in feature else False # running rate features with the Moran rate option
    quadrant_labels, significant_quadrant_labels, \
    local_i_stats, y_lag = calculate_moran_for_feature(df, feature, rate=rate, alpha=alpha)


    # adding features based off of characteristic column information and the i statistics
    df[feature+"_moran_quadrant"] = quadrant_labels
    quartile2description = {0:"No Significance", 1:"Q1: (+, +)", 2:"Q2: (-, +)", 3:"Q3: (-, -)", 4:"Q4: (+, -)"}
    df[feature+"_moran_quadrant_descriptive"] = df[feature+"_moran_quadrant"].replace(quartile2description)

    df[feature+"_significant_moran_quadrant_descriptive"] = significant_quadrant_labels
    description2quartile = {"No Significance":0, "Q1: (+, +)":1, "Q2: (-, +)":2, "Q3: (-, -)":3, "Q4: (+, -)":4}
    df[feature+"_significant_moran_quadrant"] = \
            df[feature+"_significant_moran_quadrant_descriptive"].replace(description2quartile)

    df[feature+"_moran_i"] = local_i_stats
    df[feature+"_ylag"] = y_lag


    return df
