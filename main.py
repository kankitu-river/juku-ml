from fastapi import FastAPI, Depends
from auth import verify_token
from features.churn import ChurnRequest, ChurnResponse, detect as churn_detect
from features.makeup import MakeupRequest, MakeupResponse, score as makeup_score
from features.shift_forecast import ShiftRequest, ShiftResponse, forecast as shift_forecast
from features.intensive_opt import IntensiveRequest, IntensiveResponse, optimize as intensive_optimize

app = FastAPI(title="juku-ml", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/churn/detect", dependencies=[Depends(verify_token)])
def churn_detect_route(payload: ChurnRequest) -> ChurnResponse:
    return churn_detect(payload)


@app.post("/makeup/score", dependencies=[Depends(verify_token)])
def makeup_score_route(payload: MakeupRequest) -> MakeupResponse:
    return makeup_score(payload)


@app.post("/shift/forecast", dependencies=[Depends(verify_token)])
def shift_forecast_route(payload: ShiftRequest) -> ShiftResponse:
    return shift_forecast(payload)


@app.post("/intensive/optimize", dependencies=[Depends(verify_token)])
def intensive_optimize_route(payload: IntensiveRequest) -> IntensiveResponse:
    return intensive_optimize(payload)
