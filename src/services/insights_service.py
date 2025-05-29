from datetime import datetime, timedelta
from typing import Dict, Any
import pandas as pd

from .sales_service import SalesService


class InsightsService:
    def __init__(self, sales_service: SalesService):
        self.sales_service = sales_service

    def last_30_days_kpis(self) -> Dict[str, Any]:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Get all sales for the period
        sales = self.sales_service.db.query(Sale).filter(
            Sale.created_at >= start_date,
            Sale.created_at <= end_date
        ).all()
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame([sale.to_dict() for sale in sales])
        
        if df.empty:
            return {
                "total_sales": 0,
                "total_revenue": 0,
                "avg_ticket": 0,
                "top_payment_method": None,
                "top_seller": None
            }
        
        kpis = {
            "total_sales": len(df),
            "total_revenue": float(df["amount"].sum()),
            "avg_ticket": float(df["amount"].mean()),
            "top_payment_method": df["payment_method"].mode().iloc[0] if not df.empty else None,
            "top_seller": df["seller"].mode().iloc[0] if not df.empty else None
        }
        
        return kpis

    def ad_hoc_analysis(self, metric: str, start_date: datetime, end_date: datetime = None) -> Dict[str, Any]:
        if end_date is None:
            end_date = datetime.utcnow()
            
        sales = self.sales_service.db.query(Sale).filter(
            Sale.created_at >= start_date,
            Sale.created_at <= end_date
        ).all()
        
        df = pd.DataFrame([sale.to_dict() for sale in sales])
        
        if df.empty:
            return {"message": "No data available for the specified period"}
            
        analysis = {}
        
        if metric == "daily_sales":
            df["date"] = pd.to_datetime(df["created_at"]).dt.date
            daily = df.groupby("date")["amount"].agg(["count", "sum"]).reset_index()
            analysis = daily.to_dict(orient="records")
            
        elif metric == "payment_methods":
            payment_methods = df["payment_method"].value_counts().to_dict()
            analysis = {"distribution": payment_methods}
            
        elif metric == "seller_performance":
            seller_stats = df.groupby("seller").agg({
                "amount": ["count", "sum", "mean"]
            }).round(2)
            seller_stats.columns = ["total_sales", "total_revenue", "avg_ticket"]
            analysis = seller_stats.to_dict(orient="index")
            
        return analysis 