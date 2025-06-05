# from src.logger import logging
# from src.exception import MyException
# import sys

# # logging.debug('this is a debug message')

# try:
#     a = 1+'m'
# except Exception as e:
#     logging.info(e)
#     raise MyException(e, sys) from e


from src.pipeline.training_pipeline import TrainPipeline

pipeline = TrainPipeline()

pipeline.run_pipeline()