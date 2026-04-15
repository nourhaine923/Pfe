from fastapi import FastAPI
from app.database import db
from app.routers.patient_routes import router as patient_router
from app.routers.transplantation_routes import router as transplantation_router
from app.routers.followup_routes import router as followup_router
from app.routers.therapeutic_routes import router as therapeutic_router
from app.routers.biological_routes import router as biological_router
from app.routers.adverse_event_routes import router as adverse_event_router
from app.routers.immunological_routes import router as immunological_router
from app.routers.outcome_routes import router as outcome_router
from app.routers.transfusion_routes import router as transfusion_router
from app.routers.rejection_routes import router as rejection_router
from app.routers.vital_routes import router as vital_router
from app.routers.adherence_routes import router as adherence_router
from app.routers.barem_routes import router as barem_router
from app.routers.score_routes import router as score_router
from app.routers.attribute_routes import router as attribute_router
from app.routers.immunosuppression_routes import router as immunosuppression_router
from app.routers.auth_routes import router as auth_router
from app.routers.admin_routes import router as admin_router
from app.routers.crossmatch_routes import router as crossmatch_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(patient_router)
app.include_router(transplantation_router)
app.include_router(followup_router)
app.include_router(immunosuppression_router)
app.include_router(therapeutic_router)
app.include_router(biological_router)
app.include_router(adverse_event_router)
app.include_router(immunological_router)
app.include_router(outcome_router)
app.include_router(transfusion_router)
app.include_router(rejection_router)
app.include_router(vital_router)
app.include_router(adherence_router)
app.include_router(barem_router)
app.include_router(score_router)
app.include_router(attribute_router)
app.include_router(auth_router)  # Auth routes (register/login)
app.include_router(admin_router)  # Admin routes (user management)
app.include_router(crossmatch_router)  # Crossmatch test routes

@app.get("/")
def root():
    return {"message": "FastAPI running"}

@app.get("/test-db")
def test_db():
    db.command("ping")
    return {"message": "MongoDB connected successfully"}