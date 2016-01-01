import numpy as np
from rlscore.utilities import sampled_kronecker_products

class PairwisePredictorInterface(object):
    
    def predict(self, X1, X2, row_inds_X1pred = None, row_inds_X2pred = None):
        return self.predictor.predict(X1, X2, row_inds_X1pred, row_inds_X2pred)

class KernelPairwisePredictor(object):
    
    def __init__(self, A, row_inds_K1training = None, row_inds_K2training = None, kernel = None):
        """Initializes the dual model
        @param A: dual coefficient matrix
        @type A: numpy matrix"""
        self.A = A
        self.row_inds_K1training, self.row_inds_K2training = row_inds_K1training, row_inds_K2training
        self.kernel = kernel
    
    
    def predict(self, K1pred, K2pred, row_inds_K1pred = None, row_inds_K2pred = None):
        """Computes predictions for test examples.

        Parameters
        ----------
        K1pred: {array-like, sparse matrix}, shape = [n_samples1, n_basis_functions1]
            the first part of the test data matrix
        K2pred: {array-like, sparse matrix}, shape = [n_samples2, n_basis_functions2]
            the second part of the test data matrix
        
        Returns
        ----------
        P: array, shape = [n_samples1, n_samples2]
            predictions
        """
        if len(K1pred.shape) == 1:
            K1pred = K1pred.reshape(1, K1pred.shape[0])
        if len(K2pred.shape) == 1:
            K2pred = K2pred.reshape(1, K2pred.shape[0])
        if row_inds_K1pred != None:
            row_inds_K1pred = np.array(row_inds_K1pred, dtype = np.int32)
            row_inds_K2pred = np.array(row_inds_K2pred, dtype = np.int32)
            P = sampled_kronecker_products.sampled_vec_trick(
                self.A,
                K2pred,
                K1pred,
                row_inds_K2pred,
                row_inds_K1pred,
                self.row_inds_K2training,
                self.row_inds_K1training)
        else:
            P = sampled_kronecker_products.sampled_vec_trick(
                self.A,
                K2pred,
                K1pred,
                None,
                None,
                self.row_inds_K2training,
                self.row_inds_K1training)
            
            #P = P.reshape((K1pred.shape[0], K2pred.shape[0]), order = 'F')
        P = np.array(P)
        return P


class LinearPairwisePredictor(object):
    
    def __init__(self, W):
        """Initializes the linear model
        @param W: primal coefficient matrix
        @type W: numpy matrix"""
        self.W = W
    
    
    def predict(self, X1pred, X2pred, row_inds_X1pred = None, row_inds_X2pred = None):
        """Computes predictions for test examples.
        
        Parameters
        ----------
        X1pred: {array-like, sparse matrix}, shape = [n_samples1, n_features1]
            the first part of the test data matrix
        X2pred: {array-like, sparse matrix}, shape = [n_samples2, n_features2]
            the second part of the test data matrix
        
        Returns
        ----------
        P: array, shape = [n_samples1, n_samples2]
            predictions
        """
        if len(X1pred.shape) == 1:
            if self.W.shape[0] > 1:
                X1pred = X1pred[np.newaxis, ...]
            else:
                X1pred = X1pred[..., np.newaxis]
        if len(X2pred.shape) == 1:
            if self.W.shape[1] > 1:
                X2pred = X2pred[np.newaxis, ...]
            else:
                X2pred = X2pred[..., np.newaxis]
        if row_inds_X1pred == None:
            P = np.dot(np.dot(X1pred, self.W), X2pred.T)
        else:
            P = sampled_kronecker_products.sampled_vec_trick(
                    self.W.reshape((self.W.shape[0] * self.W.shape[1]), order = 'F'),
                    X2pred,
                    X1pred,
                    np.array(row_inds_X2pred, dtype = np.int32),
                    np.array(row_inds_X1pred, dtype = np.int32),
                    None,
                    None)
        return P.ravel(order = 'F')

