from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..models import Sale


class SalesService:
    def __init__(self, db: Session):
        self.db = db

    def register_sale(self, amount: float, payment_method: str, seller: str, customer_phone: str) -> Dict[str, Any]:
        sale = Sale(
            amount=amount,
            payment_method=payment_method,
            seller=seller,
            customer_phone=customer_phone
        )
        self.db.add(sale)
        self.db.commit()
        self.db.refresh(sale)
        return sale.to_dict()

    def daily_summary(self, date: datetime) -> Dict[str, Any]:
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        sales = self.db.query(Sale).filter(
            Sale.created_at >= start_date,
            Sale.created_at < end_date
        ).all()
        
        total_amount = sum(sale.amount for sale in sales)
        return {
            "date": date.date().isoformat(),
            "total_sales": len(sales),
            "total_amount": total_amount,
            "sales": [sale.to_dict() for sale in sales]
        }

    def history(self, customer_phone: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        query = self.db.query(Sale)
        if customer_phone:
            query = query.filter(Sale.customer_phone == customer_phone)
        
        sales = query.order_by(Sale.created_at.desc()).limit(limit).all()
        return [sale.to_dict() for sale in sales] 