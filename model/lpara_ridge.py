import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.utils.validation import check_is_fitted, check_X_y, check_array

class DomainAdaptiveRidgeRegressor(BaseEstimator, RegressorMixin):
    _estimator_type = "regressor"

    def __sklearn_tags__(self):
        tags = super().__sklearn_tags__()
        tags.estimator_type = "regressor"
        return tags
    """
    LPARA-Ridge: Domain-Adaptive Group-Regularized Ridge Regressor
    
    Solves the domain-structured regularized least-squares objective:
        min_{\\beta} || y - X \\beta ||_2^2 + \\sum_{g} \\lambda_g || \\beta_g ||_2^2
        
    Where feature spaces are grouped into:
        1. Hardware Physical Features (hw)
        2. Brand Multipliers & Positioning (brand)
        3. Laptop Segment Baselines (seg)
        4. Segment-Hardware Interactions (inter)
    """

    def __init__(
        self,
        alpha_hw: float = 1.0,
        alpha_brand: float = 5.0,
        alpha_seg: float = 2.0,
        alpha_inter: float = 10.0,
        fit_intercept: bool = True,
        hw_indices=None,
        brand_indices=None,
        seg_indices=None,
        inter_indices=None
    ):
        self.alpha_hw = alpha_hw
        self.alpha_brand = alpha_brand
        self.alpha_seg = alpha_seg
        self.alpha_inter = alpha_inter
        self.fit_intercept = fit_intercept
        self.hw_indices = hw_indices
        self.brand_indices = brand_indices
        self.seg_indices = seg_indices
        self.inter_indices = inter_indices

    def _infer_feature_groups(self, n_features: int):
        """
        Default partitioning if explicit column indices are not provided.
        """
        if all(idx is not None for idx in [self.hw_indices, self.brand_indices, self.seg_indices, self.inter_indices]):
            return self.hw_indices, self.brand_indices, self.seg_indices, self.inter_indices
            
        # Heuristic default partitioning based on feature dimension
        quarter = n_features // 4
        hw = list(range(0, min(10, n_features)))
        brand = list(range(10, min(30, n_features)))
        seg = list(range(30, min(40, n_features)))
        inter = list(range(40, n_features)) if n_features > 40 else []
        
        # Ensure all features belong to at least one group
        assigned = set(hw + brand + seg + inter)
        unassigned = [i for i in range(n_features) if i not in assigned]
        hw.extend(unassigned)
        
        return hw, brand, seg, inter

    def fit(self, X, y):
        X, y = check_X_y(X, y, accept_sparse=False, dtype=[np.float64, np.float32])
        n_samples, n_features = X.shape

        hw_idx, brand_idx, seg_idx, inter_idx = self._infer_feature_groups(n_features)
        self.hw_indices_ = hw_idx
        self.brand_indices_ = brand_idx
        self.seg_indices_ = seg_idx
        self.inter_indices_ = inter_idx

        if self.fit_intercept:
            self.x_mean_ = np.mean(X, axis=0)
            self.y_mean_ = np.mean(y)
            X_centered = X - self.x_mean_
            y_centered = y - self.y_mean_
        else:
            self.x_mean_ = np.zeros(n_features)
            self.y_mean_ = 0.0
            X_centered = X
            y_centered = y

        # Construct diagonal regularization penalty matrix D
        d_diag = np.zeros(n_features, dtype=np.float64)
        d_diag[hw_idx] = self.alpha_hw
        d_diag[brand_idx] = self.alpha_brand
        d_diag[seg_idx] = self.alpha_seg
        if len(inter_idx) > 0:
            d_diag[inter_idx] = self.alpha_inter

        D = np.diag(d_diag)

        # Closed-form analytical solve: beta = (X^T X + D)^(-1) X^T y
        XtX = np.dot(X_centered.T, X_centered)
        XtX_reg = XtX + D
        Xty = np.dot(X_centered.T, y_centered)

        try:
            self.coef_ = np.linalg.solve(XtX_reg, Xty)
        except np.linalg.LinAlgError:
            self.coef_ = np.linalg.lstsq(XtX_reg, Xty, rcond=None)[0]

        if self.fit_intercept:
            self.intercept_ = self.y_mean_ - np.dot(self.x_mean_, self.coef_)
        else:
            self.intercept_ = 0.0

        self.is_fitted_ = True
        return self

    def predict(self, X):
        check_is_fitted(self, ["coef_", "intercept_", "is_fitted_"])
        X = check_array(X, accept_sparse=False, dtype=[np.float64, np.float32])
        return np.dot(X, self.coef_) + self.intercept_


class LPARAHybridRegressor(BaseEstimator, RegressorMixin):
    _estimator_type = "regressor"

    def __sklearn_tags__(self):
        tags = super().__sklearn_tags__()
        tags.estimator_type = "regressor"
        return tags

    """
    LPARA-Hybrid: Two-Stage Domain-Adaptive Linear Base + Residual Gradient Boosting
    Stage 1: Fits DomainAdaptiveRidgeRegressor for physical pricing rules and group regularization.
    Stage 2: Fits residual XGBoost tree booster on (y - y_lpara) to capture non-linear interactions.
    """

    def __init__(
        self,
        alpha_hw: float = 1.0,
        alpha_brand: float = 3.5,
        alpha_seg: float = 1.5,
        xgb_lr: float = 0.04,
        xgb_depth: int = 4,
        n_estimators: int = 120
    ):
        self.alpha_hw = alpha_hw
        self.alpha_brand = alpha_brand
        self.alpha_seg = alpha_seg
        self.xgb_lr = xgb_lr
        self.xgb_depth = xgb_depth
        self.n_estimators = n_estimators

    def fit(self, X, y):
        import xgboost as xgb
        X_arr, y_arr = check_X_y(X, y, accept_sparse=False, dtype=[np.float64, np.float32])

        # Stage 1: Domain-Adaptive Linear Base
        self.lpara_base_ = DomainAdaptiveRidgeRegressor(
            alpha_hw=self.alpha_hw,
            alpha_brand=self.alpha_brand,
            alpha_seg=self.alpha_seg,
            alpha_inter=4.0
        )
        self.lpara_base_.fit(X_arr, y_arr)

        # Stage 2: Residual Tree Boosting
        residuals = y_arr - self.lpara_base_.predict(X_arr)
        self.xgb_res_ = xgb.XGBRegressor(
            n_estimators=self.n_estimators,
            learning_rate=self.xgb_lr,
            max_depth=self.xgb_depth,
            random_state=42,
            n_jobs=4
        )
        self.xgb_res_.fit(X_arr, residuals)
        self.is_fitted_ = True
        return self

    def predict(self, X):
        check_is_fitted(self, ["lpara_base_", "xgb_res_", "is_fitted_"])
        X_arr = check_array(X, accept_sparse=False, dtype=[np.float64, np.float32])
        return self.lpara_base_.predict(X_arr) + self.xgb_res_.predict(X_arr)


class LPARAStackingRegressor(BaseEstimator, RegressorMixin):
    _estimator_type = "regressor"

    def __sklearn_tags__(self):
        tags = super().__sklearn_tags__()
        tags.estimator_type = "regressor"
        return tags

    """
    LPARA-Stacking (A+ Meta Ensemble):
    Meta-Ensemble architecture combining XGBoost, CatBoost, Gradient Boosting,
    and DomainAdaptiveRidgeRegressor as base learners, with DomainAdaptiveRidgeRegressor
    serving as the final group-regularized Meta Blender.
    """

    def __init__(
        self,
        alpha_hw: float = 0.5,
        alpha_brand: float = 2.0,
        alpha_seg: float = 1.0,
        n_estimators: int = 180
    ):
        self.alpha_hw = alpha_hw
        self.alpha_brand = alpha_brand
        self.alpha_seg = alpha_seg
        self.n_estimators = n_estimators

    def fit(self, X, y):
        import xgboost as xgb
        from catboost import CatBoostRegressor
        from sklearn.ensemble import GradientBoostingRegressor, StackingRegressor
        from sklearn.ensemble import RandomForestRegressor

        base_lpara = DomainAdaptiveRidgeRegressor(
            alpha_hw=self.alpha_hw, alpha_brand=self.alpha_brand, alpha_seg=self.alpha_seg
        )
        base_xgb = xgb.XGBRegressor(n_estimators=self.n_estimators, learning_rate=0.06, max_depth=5, random_state=42)
        base_cb = CatBoostRegressor(iterations=220, learning_rate=0.04, depth=5, random_seed=42, verbose=0)
        base_gb = GradientBoostingRegressor(n_estimators=self.n_estimators, learning_rate=0.06, max_depth=5, random_state=42)

        self.stacker_ = StackingRegressor(
            estimators=[
                ("lpara", base_lpara),
                ("xgb", base_xgb),
                ("cb", base_cb),
                ("gb", base_gb)
            ],
            final_estimator=DomainAdaptiveRidgeRegressor(alpha_hw=0.1, alpha_brand=0.5, alpha_seg=0.2),
            n_jobs=1
        )
        self.stacker_.fit(X, y)
        self.is_fitted_ = True
        return self

    def predict(self, X):
        check_is_fitted(self, ["stacker_", "is_fitted_"])
        return self.stacker_.predict(X)


