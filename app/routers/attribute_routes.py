from fastapi import APIRouter

from app.utils.attribute_registry import ATTRIBUTE_REGISTRY
from app.utils.attribute_metadata import ATTRIBUTE_METADATA
from app.auth.dependencies import doctor_or_admin
from fastapi import Depends


router = APIRouter(prefix="/attributes", tags=["Attributes"])



@router.get("/", dependencies=[Depends(doctor_or_admin)])
def get_attributes():


    attributes = []

    for key in ATTRIBUTE_REGISTRY.keys():
        meta = ATTRIBUTE_METADATA.get(key, {})

        attributes.append({
            "key": key,
            "label": meta.get("label", key),
            "type": meta.get("type", "unknown"),
            "unit": meta.get("unit")
        })

    return attributes