"""
api/routers/dashboard.py — read-only endpoints the dashboard polls. All
data comes straight from the CSVs in data/tabular via dashboard_service,
so it always reflects the latest state of those files.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter

from api.models import (
    CarriersSummary,
    DashboardSummary,
    ImpactSummary,
    InventorySummary,
    ShipmentsSummary,
)
from api.services import analytics_service, dashboard_service
from api.services.email_service import list_escalations

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def summary():
    open_escalations = sum(1 for e in list_escalations() if not e["sent"])
    return dashboard_service.get_dashboard_summary(open_escalations=open_escalations)


@router.get("/inventory", response_model=InventorySummary)
def inventory():
    return dashboard_service.get_inventory_summary()


@router.get("/shipments", response_model=ShipmentsSummary)
def shipments():
    return dashboard_service.get_shipments_summary()


@router.get("/carriers", response_model=CarriersSummary)
def carriers():
    return dashboard_service.get_carriers_summary()


@router.get("/impact", response_model=ImpactSummary)
def impact():
    escalations_handled = len(list_escalations())
    return analytics_service.get_impact_summary(escalations_handled=escalations_handled)
