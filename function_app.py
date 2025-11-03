import azure.functions as func
import logging
import SerbiaTrainApi

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="Stations")
def Stations(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        SerbiaTrainApi.Station.asJSON(),
        mimetype="application/json",
        status_code=200
    )

@app.route(route="Arrivals")
def Arrivals(req: func.HttpRequest) -> func.HttpResponse:
    station = req.params.get('station')
    date = req.params.get('date')

    logging.info(f'Someone requested to see the arrival times for station {station}, and date {date}')

    if not station or not date:
        return func.HttpResponse(
            "Station and date are required.",
            status_code=400
        )

    api = SerbiaTrainApi.TrainApi()

    try:
        result = api.getTimeTable(SerbiaTrainApi.Station[station], date)
    except Exception as e:
        logging.error(e)

        return func.HttpResponse(
            f"An error occured: {e}",
            mimetype="text/plain",
            status_code=500
        )

    except SerbiaTrainApi.TrainException as e:
        return func.HttpResponse(
            f"An error occured: {e}",
            mimetype="text/plain",
            status_code=400
        )

    return func.HttpResponse(
        result.toJSON(),
        mimetype="application/json",
        status_code=200
    )