from _decimal import Decimal
from datetime import datetime
from typing import Optional
from sqlalchemy import func
from ..models.orders import Purchase
from ..models.categories import Category
from ..models.sales import Sale
from ..models.rooms import Room
from ..models.base import db
from .categories_manager import CategoriesManager
from .orders_manager import OrdersManager


class PurchasesManager:
    @staticmethod
    def set_price(purchase: Purchase):
        category: Category = db.session.query(Room).get(purchase.room_id).category
        delta_seconds: Decimal = (purchase.end - purchase.start).total_seconds()
        SECONDS_IN_DAY: int = 86400
        days: int = round(Decimal(delta_seconds / SECONDS_IN_DAY), 0)
        default_price: Decimal = category.price * days
        sale = db.session.query(func.max(Sale.discount)).filter(
            Sale.start_date <= datetime.now(),
            Sale.end_date >= datetime.now(),
            Sale.date_deleted == None,
            Sale.categories.any(id=category.id)
        ).scalar()
        if sale:
            sale_ration = Decimal(sale / 100)
            purchase.price = default_price - (default_price * sale_ration)
        else:
            purchase.price = default_price

        prepayment_ratio = Decimal(category.prepayment_percent / 100)
        purchase.prepayment = purchase.price * prepayment_ratio
        refund_ratio = Decimal(category.refund_percent / 100)
        purchase.refund = purchase.price * refund_ratio

    @staticmethod
    def set_room(purchase: Purchase, category: Category):
        room_id = CategoriesManager.pick_room(
            category=category,
            start=purchase.start,
            end=purchase.end,
            purchase_id=purchase.id
        )
        if room_id is None:
            raise ValueError('На эти даты нет свободных комнат этой категории')

        purchase.room_id = room_id

    @staticmethod
    def save_purchase(purchase: Purchase, category: Optional[Category] = None):
        db.session.add(purchase)
        category = category if category is not None else purchase.room.category

        PurchasesManager.set_room(purchase, category)
        PurchasesManager.set_price(purchase)
        db.session.commit()
        OrdersManager.save_order(purchase.order)

    @staticmethod
    def mark_as_canceled(purchase: Purchase):
        db.session.add(purchase)
        if purchase.is_prepayment_paid or purchase.is_paid:
            purchase.is_canceled = True
        else:
            db.session.delete(purchase)
        db.session.commit()