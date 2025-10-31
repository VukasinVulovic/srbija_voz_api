import SerbiaTrainApi

api = SerbiaTrainApi.TrainApi()

print(api.getTimeTable(SerbiaTrainApi.Station.TOSIN_BUNAR, "31.10.2025"))