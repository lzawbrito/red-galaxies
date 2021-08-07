from sklearn.tree import DecisionTreeClassifier 
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.impute import SimpleImputer

##This file intends to display the results of out resnet model alongside a baseline decision tree model. 

####### CONSTANTS #######################################################
# confidence interval
G_MAG_LOWER = 18.600463384786813
R_MAG_LOWER = 17.044586722150783
Z_MAG_LOWER = 15.859586722150778

G_MAG_HIGHER = 23.75807349550339
R_MAG_HIGHER = 22.202196832867358
Z_MAG_HIGHER = 21.017196832867356

#ratio for sampling
NUM_CANDIDATES = 15088 #conserving ratio of 92-8)

################# Cleaning the data #####################################

# Produce dataframes with numerical values
known_lenses = pd.read_csv("../red-galaxies/huang_candidates_2021.txt") #in radians
candidate_lenses = pd.read_csv("../red-galaxies/all_galaxies.csv") # in degrees

### Known Lenses ###
#1,312 rows
known_lenses = known_lenses[["g mag", "r mag" ,"z mag"]]
known_lenses = known_lenses.rename(columns={"g mag": "g_mag", "r mag":"r_mag" ,"z mag":"z_mag"})
# fill in missing info 
known_means = known_lenses.mean()
known_lenses = known_lenses.fillna(known_means)
known_lenses['is_lense'] = 'True' #labeling data
# print(known_lenses.head)


### Lense Candidates ###
#4,119,097 rows initially from all 
candidate_lenses = candidate_lenses[["g_mag", "r_mag", "z_mag"]]
# filter by confidence interval
candidate_lenses = candidate_lenses[candidate_lenses['g_mag'].between(G_MAG_LOWER, G_MAG_HIGHER)]
candidate_lenses = candidate_lenses[candidate_lenses['r_mag'].between(R_MAG_LOWER, R_MAG_HIGHER)]
candidate_lenses = candidate_lenses[candidate_lenses['z_mag'].between(Z_MAG_LOWER, Z_MAG_HIGHER)]
# --> 368,176 rows
# fill in missing info 
candidate_means = candidate_lenses.mean()
candidate_lenses = candidate_lenses.fillna(candidate_means)
candidate_lenses['is_lense'] = 'False' #labeling data
# print(candidate_lenses.count)

candidate_lenses = candidate_lenses.sample(n=NUM_CANDIDATES, random_state=1)

#combine known and ambiguous 
labeled_data = pd.concat([candidate_lenses, known_lenses])
#shuffle the rows to avoid biases
labeled_data = labeled_data.sample(frac=1).reset_index(drop=True)
# 
print(labeled_data.count)


# labeled_data = pd.DataFrame(np.asarray(labeled_data, dtype=np.float))
# Clean data from NaNs
# means = labeled_data.iloc[:, [True, True, True, False]].astype(float).mean()
# means = labeled_data.mean(axis = 0, skipna = True, convert_numeric=True)

############### MACHINE LEARNING MODELS (copied from HW6) ###############

TEST_SIZE = 0.2 # TODO: Feel free to modify this!
KNN_NUM_NEIGHBORS = 2 # lense or no lense
RANDOM_SEED = 0
# TRAFFIC_STOPS_NONNUMERICAL_COLS = ["county_name", "driver_gender", "driver_race", "violation", "search_conducted",\
#                                     "stop_outcome", "is_arrested", "drugs_related_stop"]

def get_trained_model(dataset, model_name, target_name=None, feature_names=None):
    """
    Input:
    - dataset: a dataframe of the dataset to operate on
    - A model name: str, a model name. One of ["decision_tree", "k_nearest_neighbor", "logistic_regression", "dummy"]
    - target_name: str, the name of the variable that you want to make the label of the regression/classification model
    - feature_names: list[str], the list of strings of the variable names that you want to be the features of your
                        regression/classification model
    
    What it does:
    - Create a model that matches with the model_name, and then fit to the One-Hot-Encoded dataset
    Output: A tuple of four things:
    - model: The model associated with the model_name - **TRAINED**
    - ohe: The one hot encoder that is used to encode non-numeric features in the dataset
    - train_df: The training dataset (DataFrame)
    - test_df: The testing dataset (DataFrame)
    """
    # first, check if the inputs are valid
    assert model_name in ["decision_tree", "k_nearest_neighbor", "logistic_regression"], \
            f"Invalid input for function get_model: model_name = {model_name}, supposed to be in ['decision_tree', 'k_nearest_neighbor', 'logistic_regression']"
    
    data = dataset.copy() #creating a copy of the dataset to work on
    
    # creating a OneHotEncoder for non-numeric features
    ohe = OneHotEncoder(handle_unknown='ignore')

    # getting the exact model - the formatting is a lil cursed :P
    if model_name == "decision_tree": model = DecisionTreeClassifier(random_state=RANDOM_SEED)
    if model_name == "logistic_regression": model = LogisticRegression(random_state=RANDOM_SEED)
    if model_name == "k_nearest_neighbor": model = KNeighborsClassifier(n_neighbors=KNN_NUM_NEIGHBORS)
   
    #setting default target feature to predict
    """
    Default assumption: target label is `is_lense`, feature_names are the rest
    """
    if target_name == None:
        target_name = "is_lense" # default assumption

    if feature_names == None:
        feature_names = [e for e in data.columns if e != target_name] # default assumption


    # now assert a few things to make sure all the column names are valid
    assert target_name in data.columns, f"Column not found: {target_name}"
    for lbl in feature_names:
        assert lbl in data.columns, f"Column not found: {lbl}"
    
    train_df, test_df = train_test_split(data, test_size=TEST_SIZE)

    train_data = train_df[feature_names].copy()


    model.fit(train_data, train_df[target_name])
    return model, ohe, train_df, test_df
    



def get_model_accuracy(model, df, one_hot_encoder, dataset_name=None, target_name=None, feature_names=None):
    """
    Inputs:
    - model: sklearn model that was returned by get_model (or created yourself)
    - df: The dataframe that contains the features and the target
    - one_hot_encoder: The sklearn OneHotEncoder that was returned by get_model (or created yourself)
                        that learns how to encode the non-numeric features in the dataset df
    - dataset_name: if not None, has to be one of ["ri_traffic_stops", "banknote_authentication"]
    - target_name, feature_names: if not None, has to be in df.columns
    Outputs: A tuple of three things:
    - acc: Accuracy score
    - y_pred: The model's predictions (numpy array)
    - y_targ: The target labels (numpy array)
    """
    # default target label 
    default_targ_label = "is_lense"

    # if nothing was inputted into target_lalbel, use the default target label
    if target_name == None:
        target_name = default_targ_label
    
    if feature_names == None:
        feature_names = [e for e in df.columns if e != target_name]

    # and then assert that target_name and each of feature_names in df
    ohe_bool = False
    assert target_name in df.columns, f"Column not found: {target_name}"
    for lbl in feature_names:
        assert lbl in df.columns, f"Column not found: {lbl}"


    #### NOTE THIS IMPLEMENTATION ONLY SUPPORTS NON NUMERIC VALUES #####
    # encode the features
    if not ohe_bool:
        encoded = df[feature_names]

    # and then use the model to predict
    y_pred = model.predict(encoded)
    
    # get the y_target
    y_targ = df[target_name].to_numpy()

    # get the accuracy
    acc = (y_pred == y_targ).sum() / len(y_pred)    
    
    return acc, y_pred, y_targ



################# Helper Method Producing Model Performance Data ###########################

models = ["decision_tree", "k_nearest_neighbor", "logistic_regression"]
train_accs = [i for i in range(len(models))]
test_accs= [i for i in range(len(models))]
# labeled_data = LABELED_DATA
for model_name in ["decision_tree", "k_nearest_neighbor", "logistic_regression"]: # dummy: baseline model
        # Get the trained model (trained on train_df)
        model, one_hot_encoder, train_df, test_df = get_trained_model(dataset= labeled_data, model_name=model_name)

        # Getting the training accuracy, model's predictions and the training targets
        training_acc, training_preds, training_targs = get_model_accuracy(model=model,\
                                                                                df=train_df,\
                                                                                one_hot_encoder=one_hot_encoder)

        # You can comment/uncomment this section to print out the accuracy
        testing_acc, testing_preds, testing_targs = get_model_accuracy(model=model,\
                                                                            df=test_df,\
                                                                            one_hot_encoder=one_hot_encoder)
        train_accs[models.index(model_name)]= training_acc
        test_accs[models.index(model_name)] = testing_acc


# labels = list(len(feature_names[i]) for i in range(len(feature_names)))
model_labels = pd.DataFrame(models)
model_accuracies = pd.concat([model_labels.rename(columns={0:"model"}),pd.DataFrame(train_accs).rename(columns={0:"train_acc"}),pd.DataFrame(test_accs).rename(columns={0:"test_acc"})], axis=1)

print(model_accuracies)



####################### ADD PERFORMANCE DATA FROM RESNET TO model_accuracies ######





############################# PLOT THE RESULTS ##############################

N = len(model_accuracies)
train_ind = np.arange(N)  # the x locations for the groups
width = 0.3 # the width of the bars
test_ind = [x + width for x in train_ind]

#trendline --> implemented then realized they dont really apply here
# models_train_trend = Ridge()
# models_train_trend.fit(pd.DataFrame(train_ind), model_accuracies['train_acc'])

# models_test_trend = Ridge()
# models_test_trend.fit(pd.DataFrame(test_ind), model_accuracies['test_acc'])


# set up the figure 
fig, ax = plt.subplots(figsize=(9,5))


train_bars = ax.bar(train_ind, model_accuracies["train_acc"], width)
test_bars = ax.bar(test_ind, model_accuracies["test_acc"], width)
# ax.plot(pd.DataFrame(train_ind), models_train_trend.coef_*train_ind+models_train_trend.intercept_)
# ax.plot(pd.DataFrame(test_ind), models_test_trend.coef_*test_ind+models_test_trend.intercept_)

# annotate the figure 
ax.set_xticks([x + width/2 for x in train_ind])
ax.set_xticklabels(models,fontsize=10)
ax.set_xlabel("Model Used", fontsize=12)
ax.set_ylabel("Accuracy", fontsize=12)
ax.set_title('Performance of ResNet Image Classification Model and Numerical Baseline Models', fontsize=14)
ax.legend((train_bars[0], test_bars[0]), ('Train Accuracies', 'Test Accuracies'), loc=3)

#helper method to annotate labels
def labelvalue(rects):
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1*height,
       round(height, 4) ,ha='center', va='bottom')

#add text describing the process of data cleaning
# ax.text(3, 2, 'unicode: Institut für Festkörperphysik')

labelvalue(train_bars)
labelvalue(test_bars)

plt.show()