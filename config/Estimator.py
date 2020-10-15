import json
import jsonschema
from jsonschema import validate

import abc

import error as error

# Describe what kind of json you expect.
estimatorSchema = {
    "type": "object",
    "properties": {
        "estimator": {"type": "string"}
    },
    "required": ["estimator"]
}

class Estimator(object):

    @staticmethod
    def create(jsonFilePath, dataset):
        try:
            with open(jsonFilePath) as json_file:
                try:
                    jsonData = json.load(json_file)           
                    validate(instance=jsonData, schema=estimatorSchema)
                except jsonschema.exceptions.ValidationError as err:
                    template = "An exception of type {0} occurred. Arguments: {1!r}"
                    message = template.format(type(err).__name__, err.args)
                    print(message)
                    raise ValueError(error.errors['estimator_config'])
                except ValueError as err:
                    template = "An exception of type {0} occurred. Arguments: {1!r}"
                    message = template.format(type(err).__name__, err.args)
                    print(message)
                    raise ValueError(error.errors['estimator_config'])
                
                if jsonData['estimator'].startswith('KNeighbors'):                
                    import Knn #as Knn
                    esti = Knn.Knn(jsonData)
                elif jsonData['estimator'].startswith('DecisionTree'):                
                    import DecisionTree
                    esti = DecisionTree.DecisionTree(jsonData)
                elif jsonData['estimator']=='LinearSVC' or jsonData['estimator']=='LinearSVR':                
                    import SVM
                    esti = SVM.SVM(jsonData)
                elif jsonData['estimator'].startswith('ANN'):                
                    import ANN
                    esti = ANN.ANN(jsonData)
                else:
                    est_str = jsonData['estimator']
                    print(f'Invalid value for estimator name: {est_str}')
                    raise ValueError(error.errors['estimator_config'])
                #esti.parse(jsonData) # right???
                esti.assign_dataset(dataset)
                return esti
        except FileNotFoundError as err:
                template = "An exception of type {0} occurred. Arguments: {1!r}"
                message = template.format(type(err).__name__, err.args)
                print(message)
                raise ValueError(error.errors['estimator_config'])

    def assign_dataset(self, dataset):
        self.dataset = dataset
        if not self.is_regr:
            self.n_classes = self.dataset.y.nunique()
            if self.n_classes == 1:
                self.n_classes = 2

    def process(self, prep, cv, X_train, y_train):
        pipe = self.createPipe(prep)
        param_grid = self.createGrid(prep)
        grid = self.fitGrid(pipe, param_grid, cv, X_train, y_train)
        print(grid.best_score_)
        print(grid.best_params_)
        return grid.best_estimator_

    def createPipe(self, prep):
        from sklearn.pipeline import Pipeline
        from sklearn import preprocessing, decomposition

        steps = []
        if len(prep.scalers) > 0:
            steps.append(('scale', preprocessing.StandardScaler()))
        if len(prep.pca_values) > 0:
            steps.append(('reduce_dims', decomposition.PCA()))
        steps.append(('esti', self.estimator))
        pipe = Pipeline(steps)
        return pipe

    def createGrid(self, prep):
        param_grid = {}
        if len(prep.scalers) > 0:
            param_grid['scale'] = prep.scalers
        if len(prep.pca_values) > 0:
            param_grid['reduce_dims__n_components'] = prep.pca_values
        for p in self.params:
            param_grid['esti__'+p] = self.params[p]
        return param_grid

    def fitGrid(self, pipe, param_grid, cv, X_train, y_train):
        from sklearn.model_selection import GridSearchCV
        grid = GridSearchCV(pipe, param_grid=param_grid, cv=cv.cv, scoring = cv.scoring, verbose=cv.verbose)
        grid.fit(X_train.values, y_train.values)
        import pickle
        with open('knn_LM', 'wb') as fp:
            pickle.dump(grid.best_estimator_, fp)
        #print(grid.best_params_)
        return grid

'''
    # Constructor
    def __init__(self, jsonFileName):
        try:
            with open(jsonFileName) as json_file:
                jsonData = json.load(json_file)           
                try:
                    validate(instance=jsonData, schema=estimatorSchema)
                except jsonschema.exceptions.ValidationError as err:
                    print(err)
                    raise ValueError(error.errors['estimator_config'])
                self.parse(jsonData)
        except FileNotFoundError as err:
                print(err)
                raise ValueError(error.errors['estimator_config'])

    def parse(self, jsonData):
        if(jsonData['estimator']=='KNeighborsClassifier'):
            from sklearn.neighbors import KNeighborsClassifier
            self.estimator = KNeighborsClassifier()
            self.is_class = True
            self.params = {}
            if "n_neighbors_array" in jsonData:
                self.params['n_neighbors'] = jsonData['n_neighbors_array']
            elif "n_neighbors" in jsonData:
                self.params['n_neighbors'] = jsonData['n_neighbors']
            else:
                if "n_neighbors_lowerlimit" in jsonData:
                    l = jsonData['n_neighbors_lowerlimit']
                else:
                    l = 1
                if "n_neighbors_upperlimit" in jsonData:
                    u = jsonData['n_neighbors_upperlimit']
                else:
                    u = 5
                if "n_neighbors_step" in jsonData:
                    import numpy as np
                    i = jsonData['n_neighbors_step']
                    self.params['n_neighbors'] = np.arange(l, u, i)
                else:
                    self.params['n_neighbors'] = np.arange(l, u)
            sys.path.insert(1, 'output')
            import Knn_OM as Knn_OM
            self.output_manager = Knn_OM.Knn_OM()
        else:
            est_str = jsonData['estimator']
            print(f'Invalid value for estimator name: {est_str}')
            raise ValueError(error.errors['estimator_config'])
'''
