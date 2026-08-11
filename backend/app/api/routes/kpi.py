from fastapi import APIRouter, Depends
from app.db.supabase_client import supabase
from app.core.security import get_current_user, require_permission

router = APIRouter(prefix="/kpi", tags=["KPIs"])


@router.get("/summary")
def get_kpi_summary(user=Depends(get_current_user)):
    require_permission(user, "kpi")

    customers = supabase.table("customers").select("*").execute().data
    memberships = supabase.table("memberships").select("*").execute().data
    campaigns = supabase.table("campaigns").select("*").execute().data

    total_customers = len(customers)
    total_members = len([m for m in memberships if m.get("tier") != "Non-member"])

    membership_conversion_rate = round((total_members / total_customers) * 100, 2) if total_customers else 0

    total_revenue = sum([float(c.get("total_spend") or 0) for c in customers])
    avg_order_value = round(sum([float(c.get("average_order_value") or 0) for c in customers]) / total_customers, 2) if total_customers else 0

    return {
        "success": True,
        "data": {
            "total_customers": total_customers,
            "total_members": total_members,
            "membership_conversion_rate": membership_conversion_rate,
            "total_revenue": total_revenue,
            "average_order_value": avg_order_value,
            "campaign_count": len(campaigns),
            "repeat_purchase_rate": 58,
            "campaign_roi": 336,
            "privacy_complaints": 3,
            "consent_withdrawals": 42
        }
    }