import pandas as pd
import math
import numpy as np


class Euclidian_Similarity():
    """
    This class is used to create a dataframe holding euclidian similarity scores
    
    Input: 
    df_input - A pandas dataframe with observations in rows, features in columns and values/ratings in the cells
    
    Exposed Methods:
    get_sim_scores_df(): 
    returns a pandas dataframe containing euclidian similarity scorse
    
    get_similarity_with(obs, rounding=3):
    returns the similarity scores with a specific observation
    
    
    display_euclidian_similarity_matrix(self):
    displays the similarity matrix    
    
    """   
    
    def __init__(self, df_input, verbose=0):
        self.verbose = verbose
        self._df_input = df_input.copy()
        cols = self._df_input.columns.to_list()
        cols.sort()        
        self._df_input.columns = cols        
        
        self._obs = df_input.index.to_list()
        self._obs.sort()
        self._df_eu_sim = pd.DataFrame(index=self._obs, columns=self._obs)
        self._df_eu_sim.fillna(0, inplace=True)
        self._make_identity_matrix()
        self._calc_euclidian_similarity()

    def _set_lcell_to_val(self, l_row, l_col, val):
        # lbl row, col
        self._df_eu_sim.loc[l_row,l_col] = val        
        
    def _set_icell_to_val(self, i_row, i_col, val):
        # integer row, col
        self._df_eu_sim.iloc[i_row,i_col] = val
        
    def _make_identity_matrix(self):
        _ = [self._set_icell_to_val(i,i,1) for i in list(range(self._df_eu_sim.shape[0]))]
    
    def _pairwise_euclidian_similarity(self, obs1, obs2):
        """
        this function calculates the euclidian distance between two observations (aka rows in a dataframe,
        columns are features). After that, it is scaled to be between 0 and 1.
        
        obs1 and obs2 started out in the index rows. df.T makes these rows the columns, which 
        we then isolate the two columns of interest. (pair-wise)       
        
        Input:
        obs1: string, name of the index row of interest
        obs2: string, name of the index row of interest
        
        Returns: pairwise_eu_dist (a dataframe)   
        
        """
        if self.verbose>0:
            print('"_pairwise_euclidian_similarity()": before transpose:')
            display(self._df_input)
            
        # this transpose is done so that it is easy to do col 0 minus col 1 below
        df = self._df_input.loc[[obs1, obs2],:].copy().T           
        
        if self.verbose>0:
            print('"_pairwise_euclidian_similarity()": temp dataframe df created:')
            display(df)
            
        df.dropna(axis=0, inplace=True)                   
        df['temp'] = (df.iloc[:,0] - df.iloc[:,1])**2                
        pairwise_eu_dist = (df.temp.sum())**0.5        
        
        # convert to similarity
        pairwise_eu_dist = 1 / (1+pairwise_eu_dist)  # scale it to between 0 and 1
        return pairwise_eu_dist
    
    def _calc_euclidian_similarity(self):        
        _ = [self._set_lcell_to_val(ob1,ob2,self._pairwise_euclidian_similarity(ob1,ob2))
             for ob1 in self._obs for ob2 in self._obs if ob1!=ob2]    
    
    def get_similarity_with(self, obs, rounding=3):
        # return similarity scores for a specific observation with all other observations
        return self._df_eu_sim.loc[obs].sort_values(ascending=False).round(rounding)
    
    def get_sim_scores_df(self):
        # exposed method to retrieve the similarity matrix
        return self._df_eu_sim
    
    def display_euclidian_similarity_matrix(self):
        display("Euclidian Similarity Matrix:",self._df_eu_sim)
        
        
class Recommendations():
    def __init__(self, obs, df_input, df_sim_scores, cf_type='user', verbose=0):
        """
        OBJECTIVE: provide recommendations for a specific user aka obs aka observation aka row
        
        INPUTS:
        `obs`: string,  the specific user we want to provide recommendations for
        
        `df_input`: pandas dataframe, containing the data (e.g. ratings) that class `Euclidian_Similarity()`
        used to calculate the similarity scores.
        
        `cf_type`: string, choose ('user','item') where 
            'user'=='use-based recommendation', 
            'item'=='item-based recommendation'
        
        `verbose`: int, values above 0 allow printing/display of debug and status messages     
        
        EXPOSED METHODS:
        .get_recommendations(threshold=threshold, top_k=top_k)
            get recommendations for the `obs` which is defined when this class is instantiated.
            the recommendations we get from this method is ONLY for this `obs`. 
        
        """
        # load
        self._verbose = verbose
        self._obs = obs        
        self._df_sim_scores = df_sim_scores
        if self._verbose>0:
            print("displaying the loaded self._df_sim_scores:")            
            display(self._df_sim_scores)  
        self._df_input = df_input  # if not modifying this, no need to copy()?
        self._rec_matrix = df_input.copy()
        if self._verbose>0:
            print("displaying the loaded self._df_input:")
            display(self._df_input)        
        
        # transform
        self._cf_type=cf_type
        if self._cf_type == 'user':
            self._remove_watched_features()
        elif self._cf_type == 'item':
            self._create_item_item_matrix()
        if self._verbose>0:
            print("df_input is transformed into self._rec_matrix, type is '{}':".format(self._cf_type))
            print("Observations aka Obs aka Row Indexes are 'users'. ")
            display(self._rec_matrix)        

        self._add_similarity_weights_to_df()        
        self_rec_scores = None
        
    def _remove_watched_features(self):
        null_cols = self._rec_matrix.loc[[self._obs]].isnull().T
        cols_to_keep = null_cols[null_cols[self._obs]==True].index.to_list()        
        self._rec_matrix = self._rec_matrix[cols_to_keep]                   
    
    def _create_item_item_matrix(self):
        # used by 'item-based',
        # objective: to create a df that 
        # put movies (items) that obs has watched in rows, and those not yet watched in cols
        if self._verbose>1:
            print('before')
            display(self._rec_matrix)        
        
        not_null_cols = self._rec_matrix.loc[[self._obs]].notnull().T  # watched already        
        row_idx = not_null_cols[not_null_cols.loc[:,self._obs]==True].index.to_list()    

        if self._verbose>1:
            print('Watched == True')
            display('Watched uses "not null" columns', not_null_cols)        
            print('These items have been watched:\n',row_idx,'\n')        
        

        null_cols = self._rec_matrix.loc[[self._obs]].isnull().T       # not yet watched                    
        col_idx = null_cols[null_cols.loc[:,self._obs]==True].index.to_list()            

        if self._verbose>1:
            print('NOT Watched == True')        
            display('NOT watched uses "null" columns', null_cols)
            print('These items have not been watched:\n',col_idx,'\n')        
        
        self._rec_matrix = self._df_sim_scores.loc[row_idx,col_idx]

        if self._verbose>1:
            print('The Recommendation Matrix:')
            display(self._rec_matrix)
    
    def _add_similarity_weights_to_df(self):
        cols = self._rec_matrix.columns.to_list()
        
        if self._cf_type == 'user':
            if self._verbose>0:
                print('"USER-Based": _add_similarity_weights_to_df() ')        
            self._rec_matrix['sim_weights'] = self._rec_matrix.index.map(lambda x: self._df_sim_scores.loc[self._obs,x])            
        elif self._cf_type == 'item':
            if self._verbose>0:
                print('"ITEM-Based": _add_similarity_weights_to_df()')        
            self._rec_matrix['sim_weights'] = self._rec_matrix.index.map(lambda x: self._df_input.loc[self._obs,x])
            
        cols[:0] = ['sim_weights']
        self._rec_matrix = self._rec_matrix[cols]
        self._rec_matrix.sort_values(by='sim_weights',ascending=False, inplace=True)

        if self._verbose>0:
            print("after adding sim weights with respect to a specific obs:\n\t'{}'".format(self._obs))
            display(self._rec_matrix)
            print('Note that the Feature Columns are those that this specific obs has not watched or used')
            print('or pocessed. These are new to this obs. Thus we want to make one or more recommendations')
            print('from these feature columns because we do not want to recommend items this obs already')
            print('watched, knows, has done, processed.\n')
        
    def _calc_recommendation_score(self):
        # create the output matrix - df_rec_scores
        feature_indices = self._rec_matrix.columns.to_list()[1:]            
        data = {
            'recommendation_score': [0.0] * len(feature_indices)
        }        
        df_rec_scores = pd.DataFrame(data, index=feature_indices) 
        
        if self._verbose>0:
            print('The features we wish to use for making a recommendation to `obs`: "{}" are'.format(self._obs))            
            print('the feature_indices: {}'.format(feature_indices))
            print('For easier calculations, we transpose them into row index.')
            display(df_rec_scores)
            display(self._rec_matrix)
         
        if self._cf_type == 'user':            
            self._rec_matrix.drop(index=[self._obs],inplace=True)             
            for lbl in feature_indices:        
                rec_score = 0            
                selected_rows = self._rec_matrix[~self._rec_matrix[lbl].isnull()]
                if self._verbose>0:
                    print('After selecting rows where this feature: "{}"" has a rating or value in the cell,'.format(lbl))
                    print('i.e. this feature "{}" does not have any null values in the cells'.format(lbl))
                    print('We will now calculate the recommendation scores with this matrix:')
                    display(selected_rows.loc[:,['sim_weights',lbl]])
                total_weighted_sim = (selected_rows['sim_weights'] * selected_rows[lbl]).sum()
                sum_of_used_sim_weights = selected_rows.loc[:,'sim_weights'].sum()           
                rec_score = total_weighted_sim / sum_of_used_sim_weights
                df_rec_scores.loc[[lbl],'recommendation_score'] = rec_score  
                
        elif self._cf_type == 'item':
            for lbl in feature_indices:        
                rec_score = 0
                total_weighted_sim = (self._rec_matrix.loc[:,'sim_weights'] *
                                      self._rec_matrix.loc[:, lbl] ).sum()
                sum_of_lbl_sim = self._rec_matrix.loc[:,lbl].sum()

                rec_score = total_weighted_sim / sum_of_lbl_sim
                df_rec_scores.loc[[lbl],'recommendation_score'] = rec_score    
            
        if self._verbose>0:
            print("rec_score = total_weighted_sim / sum_of_used_sim_weights")
            display(df_rec_scores)            
        return df_rec_scores
    
    
    def get_recommendations(self, threshold=0, top_k=1):        
        self._rec_scores = self._calc_recommendation_score()  
            
        if self._rec_scores.recommendation_score.max() < threshold:
            return None, None        
        else:            
            self._rec_scores=self._rec_scores[self._rec_scores.recommendation_score>=threshold]
            self._rec_scores.sort_values(by=['recommendation_score'], ascending=False, inplace=True)
        return self._rec_scores.iloc[:top_k], self._rec_scores.iloc[:top_k].index.to_list()
        