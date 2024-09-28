import numpy as np
import pandas as pd
import os

class MyLinearRegression:
    def __init__(self):
        self.coef_ = None
        self.intercept_ = None

    def fit(self, X_data, y_data):
        X_data = np.insert(X_data, 0, 1, axis=1)
        betas = np.linalg.inv(np.dot(X_data.T, X_data)).dot(X_data.T).dot(y_data)
        self.intercept_ = betas[0]
        self.coef_ = betas[1:]

    def predict(self, X_test):
        X_test_with_intercept = np.insert(X_test, 0, 1, axis=1)
        y_pred = np.dot(X_test_with_intercept, np.concatenate(([self.intercept_], self.coef_)))
        return y_pred

base_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(base_dir, "csv_dataset.csv")

def predict_final_exam_score(attendance, task, mid_term, pre_board):
    df = pd.read_csv(csv_path)
    X_data = df[["attendance", "task", "mid_term", "pre_board"]].values
    y_data = df["board"].values
    lr = MyLinearRegression()
    lr.fit(X_data, y_data)
    new_student_scores = np.array([attendance, task, mid_term, pre_board]).reshape(1, -1)
    predicted_final_exam_score = lr.predict(new_student_scores)

    # Ensure the predicted score is within the range [0, 99]
    predicted_final_exam_score = max(0, predicted_final_exam_score[0])
    predicted_final_exam_score = min(99, predicted_final_exam_score)

    return predicted_final_exam_score

