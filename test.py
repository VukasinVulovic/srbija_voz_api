import SerbiaTrainApi

import json
from dataclasses import dataclass, asdict, is_dataclass
from enum import Enum, Flag

print({member.name: member.value for member in SerbiaTrainApi.Station})

api = SerbiaTrainApi.TrainApi()

res = api.getTimeTable(SerbiaTrainApi.Station.TOSIN_BUNAR, "31.10.2025")

print(res.toJSON())