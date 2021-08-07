from sklearn.tree import DecisionTreeClassifier 
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
import pandas as pd

##This file intends to display the results of out resnet model alongside a baseline decision tree model. 



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
    # assert dataset_name in ["ri_traffic_stops", "banknote_authentication"], \
    #         f"Invalid input for function get_model: dataset_name = {dataset_name}, supposed to be in ['ri_traffic_stops', 'banknote_authentication']"
    assert model_name in ["decision_tree", "k_nearest_neighbor", "logistic_regression", "dummy"], \
            f"Invalid input for function get_model: model_name = {model_name}, supposed to be in ['decision_tree', 'k_nearest_neighbor', 'logistic_regression', 'dummy']"
    
    data = dataset.copy() #creating a copy of the dataset to work on
    # creating a OneHotEncoder for non-numeric features
    ohe = OneHotEncoder(handle_unknown='ignore')

    # getting the exact model - the formatting is a lil cursed :P
    if model_name == "decision_tree": model = DecisionTreeClassifier(random_state=RANDOM_SEED)
    if model_name == "logistic_regression": model = LogisticRegression(random_state=RANDOM_SEED)
    if model_name == "k_nearest_neighbor": model = KNeighborsClassifier(n_neighbors=KNN_NUM_NEIGHBORS)
    # # this model is a dummy model - for baseline model! :)
    # if model_name == "dummy": model = DummyClassifier(random_state=RANDOM_SEED)

    # if dataset_name == "ri_traffic_stops":
    #     """
    #     Default assumption: target label is `stop_outcome`, feature_names are the rest
    #     """
    #     data = get_ri_stops_df()
    #     if target_name == None:
    #         target_name = "stop_outcome" # default assumption

    #     if feature_names == None:
    #         feature_names = [e for e in data.columns if e != target_name] # default assumption

    # if dataset_name == "banknote_authentication":
    #     """
    #     Assumption: target label is `Class`, feature_names are the rest
    #     """
    #     data = get_banknote_df()
    #     if target_name == None:
    #         target_name = "Class" # default assumption

    #     if feature_names == None:
    #         feature_names = [e for e in data.columns if e != target_name] # default assumption

    # now assert a few things to make sure all the column names are valid
    assert target_name in data.columns, f"Column not found: {target_name}"
    for lbl in feature_names:
        assert lbl in data.columns, f"Column not found: {lbl}"
    

    train_df, test_df = train_test_split(data, test_size=TEST_SIZE)

    ##########################modify to our model ################################
    # if dataset_name == "ri_traffic_stops":
    #     X = ohe.fit_transform(train_df[[e for e in feature_names if e in TRAFFIC_STOPS_NONNUMERICAL_COLS]]).toarray()
    #     X_PRIME = train_df[[e for e in feature_names if e not in TRAFFIC_STOPS_NONNUMERICAL_COLS]].to_numpy()
    #     train_data = np.concatenate((X, X_PRIME), axis=1)

    # if dataset_name == "banknote_authentication":
    #     train_data = train_df[feature_names].copy()


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
    ##### INPUT ASSERTIONS #####
    # # if either target_name == None or feature_names == None, dataset_name has to be != None
    # if target_name == None or feature_names == None:
    #     assert dataset_name in ["ri_traffic_stops", "banknote_authentication"], \
    #         """if either target_name == None or feature_names == None, dataset_name has to be != None.
    #             Check input to get_model_accuracy"""
    
    # # if nothing is passed to target_name and feature_names, we'll use the default
    # default_targ_label = {
    #     "ri_traffic_stops": "stop_outcome",
    #     "banknote_authentication": "Class"
    # }

    # if nothing was inputted into target_lalbel, use the default target label
    # if target_name == None:
    #     target_name = default_targ_label[dataset_name]
    
    # if feature_names == None:
    #     feature_names = [e for e in df.columns if e != target_name]

    # # and then assert that target_name and each of feature_names in df
    # ohe_bool = False
    # assert target_name in df.columns, f"Column not found: {target_name}"
    # for lbl in feature_names:
    #     assert lbl in df.columns, f"Column not found: {lbl}"
    #     # alright, and check if we need to slap one hot encoding on top of this or nah
    #     if lbl in TRAFFIC_STOPS_NONNUMERICAL_COLS:
    #         ohe_bool = True


    ##### Alright. Now onto the meat of the function! #####
    # encode the features
    if not ohe_bool:
        encoded = df[feature_names]
    else:
        X = one_hot_encoder.transform(df[[e for e in feature_names if e in TRAFFIC_STOPS_NONNUMERICAL_COLS]]).toarray()
        X_PRIME = df[[e for e in feature_names if e not in TRAFFIC_STOPS_NONNUMERICAL_COLS]].to_numpy()
        encoded = np.concatenate((X, X_PRIME), axis=1)

    # and then use the model to predict
    y_pred = model.predict(encoded)
    
    # get the y_target
    y_targ = df[target_name].to_numpy()

    # get the accuracy
    acc = (y_pred == y_targ).sum() / len(y_pred)    
    
    return acc, y_pred, y_targ



################# Run the models on the dataset to classify lenses ###########################

models = ["decision_tree", "k_nearest_neighbor", "logistic_regression", "dummy"]
train_accs = [i for i in range(len(models))]
test_accs= [i for i in range(len(models))]
dataset_name = "ri_traffic_stops";
for model_name in ["decision_tree", "k_nearest_neighbor", "logistic_regression", "dummy"]: # dummy: baseline model
        # Get the trained model (trained on train_df)
        model, one_hot_encoder, train_df, test_df = get_trained_model(dataset_name=dataset_name, model_name=model_name, target_name="stop_outcome")

        # Getting the training accuracy, model's predictions and the training targets
        training_acc, training_preds, training_targs = get_model_accuracy(model=model,\
                                                                                df=train_df,\
                                                                                one_hot_encoder=one_hot_encoder,\
                                                                                dataset_name=dataset_name)

        # You can comment/uncomment this section to print out the accuracy
        testing_acc, testing_preds, testing_targs = get_model_accuracy(model=model,\
                                                                            df=test_df,\
                                                                            one_hot_encoder=one_hot_encoder,\
                                                                            dataset_name=dataset_name)
        train_accs[models.index(model_name)]= training_acc
        test_accs[models.index(model_name)] = testing_acc

# labels = list(len(feature_names[i]) for i in range(len(feature_names)))
model_labels = pd.DataFrame(models)
model_accuracies = pd.concat([model_labels.rename(columns={0:"model"}),pd.DataFrame(train_accs).rename(columns={0:"train_acc"}),pd.DataFrame(test_accs).rename(columns={0:"test_acc"})], axis=1)
print(model_accuracies)





############################# Make the visualization ##############################
#setup
N = len(models)
train_ind = np.arange(N)  # the x locations for the groups
width = 0.4 # the width of the bars
test_ind = [x + width for x in train_ind]
#trendline --> implemented then realized they dont really apply here
# models_train_trend = Ridge()
# models_train_trend.fit(pd.DataFrame(train_ind), model_accuracies['train_acc'])

# models_test_trend = Ridge()
# models_test_trend.fit(pd.DataFrame(test_ind), model_accuracies['test_acc'])
 
fig, ax = plt.subplots(figsize=(9,5))
train_bars = ax.bar(train_ind, model_accuracies["train_acc"], width)
test_bars = ax.bar(test_ind, model_accuracies["test_acc"], width)
# ax.plot(pd.DataFrame(train_ind), models_train_trend.coef_*train_ind+models_train_trend.intercept_)
# ax.plot(pd.DataFrame(test_ind), models_test_trend.coef_*test_ind+models_test_trend.intercept_)

# rects3 = ax.bar(ind + 2*width, top_5, width, color='g')
ax.set_xticks([x + width/2 for x in train_ind])
ax.set_xticklabels(models,fontsize=10)
ax.set_xlabel("Model Used", fontsize=12)
ax.set_ylabel("Accuracy", fontsize=12)
ax.set_title('Model Accuracy on RI Traffic Stops Data')
ax.legend((train_bars[0], test_bars[0]), ('train accuracies', 'test accuracies'))
ax.set_ylim(.5, 1.1)
def labelvalue(rects):
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1*height,
       round(height, 4) ,ha='center', va='bottom')

labelvalue(train_bars)
labelvalue(test_bars)
plt.show()