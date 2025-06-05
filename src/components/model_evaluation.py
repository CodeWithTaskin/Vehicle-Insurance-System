from src.entity.config_entity import ModelEvaluationConfig
from src.entity.artifact_entity import ModelTrainerArtifact, DataIngestionArtifact, ModelEvaluationArtifact
from sklearn.metrics import f1_score
from src.exception import MyException
from src.constants import TARGET_COLUMN
from src.logger import logging
from src.utils.main_utils import load_object
import sys
import pandas as pd
from typing import Optional
from src.entity.azure_estimator import Proj1Estimator
from dataclasses import dataclass

@dataclass
class EvaluateModelResponse:
    trained_model_f1_score: float
    best_model_f1_score: float
    is_model_accepted: bool
    difference: float

class ModelEvaluation:
    def __init__(self, model_eval_config: ModelEvaluationConfig, data_ingestion_artifact: DataIngestionArtifact,
                 model_trainer_artifact: ModelTrainerArtifact):
        self.model_eval_config = model_eval_config
        self.data_ingestion_artifact = data_ingestion_artifact
        self.model_trainer_artifact = model_trainer_artifact

    def get_best_model(self) -> Optional[Proj1Estimator]:
        try:
            container_name = self.model_eval_config.bucket_name
            model_path = self.model_eval_config.s3_model_key_path
            estimator = Proj1Estimator(container_name=container_name, model_path=model_path)
            if estimator.is_model_present(model_path=model_path):
                return estimator
            return None
        except Exception as e:
            raise MyException(e, sys)

    def _map_gender_column(self, df):
        df['Gender'] = df['Gender'].map({'Female': 0, 'Male': 1}).astype(int)
        return df

    def _create_dummy_columns(self, df):
        return pd.get_dummies(df, drop_first=True)

    def _rename_columns(self, df):
        df = df.rename(columns = {
            'Vehicle_Age_< 1 Year': 'Vehicle_Age_It_1_Year',
            'Vehicle_Age_> 2 Years': 'Vehicle_Age_gt_2_Years'
        })
        for col in ['Vehicle_Age_It_1_Year','Vehicle_Age_gt_2_Years','Vehicle_Damage_Yes']:
            if col in df.columns:
                df[col] = df[col].astype('int')
        return df

    def _drop_id_column(self, df):
        if "_id" in df.columns:
            df = df.drop("_id", axis=1)
        return df

    def evaluate_model(self) -> EvaluateModelResponse:
        try:
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)
            x, y = test_df.drop(TARGET_COLUMN, axis=1), test_df[TARGET_COLUMN]

            x = self._map_gender_column(x)
            x = self._drop_id_column(x)
            x = self._create_dummy_columns(x)
            x = self._rename_columns(x)

            trained_model = load_object(file_path=self.model_trainer_artifact.trained_model_file_path)
            trained_model_f1_score = self.model_trainer_artifact.metric_artifact.f1_score

            best_model_f1_score = None
            best_model = self.get_best_model()
            if best_model is not None:
                y_hat_best_model = best_model.predict(x)
                best_model_f1_score = f1_score(y, y_hat_best_model)

            tmp_best_model_score = 0 if best_model_f1_score is None else best_model_f1_score
            result = EvaluateModelResponse(
                trained_model_f1_score=trained_model_f1_score,
                best_model_f1_score=best_model_f1_score,
                is_model_accepted=trained_model_f1_score > tmp_best_model_score,
                difference=trained_model_f1_score - tmp_best_model_score
            )
            return result
        except Exception as e:
            raise MyException(e, sys)

    def initiate_model_evaluation(self) -> ModelEvaluationArtifact:
        try:
            logging.info("Initialized Model Evaluation Component.")
            evaluate_model_response = self.evaluate_model()
            model_evaluation_artifact = ModelEvaluationArtifact(
                is_model_accepted=evaluate_model_response.is_model_accepted,
                s3_model_path=self.model_eval_config.s3_model_key_path,
                trained_model_path=self.model_trainer_artifact.trained_model_file_path,
                changed_accuracy=evaluate_model_response.difference
            )
            logging.info(f"Model evaluation artifact: {model_evaluation_artifact}")
            return model_evaluation_artifact
        except Exception as e:
            raise MyException(e, sys)
