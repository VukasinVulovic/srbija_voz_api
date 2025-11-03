import SerbiaTrainApi

api = SerbiaTrainApi.TrainApi()

arrivals = api.getTimeTable(SerbiaTrainApi.Station.TOSIN_BUNAR, "11.3.2025")

with open("out.json", "w+") as f:
    f.write(arrivals.toJSON())