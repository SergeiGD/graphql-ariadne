from datetime import datetime
from .base import db
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates, Session
from sqlalchemy import ForeignKey, event, func
import modules.models.categories as categories


class Photo(db.Model):
    __tablename__ = 'photo'
    REPR_MODEL_NAME = 'фото'

    id: Mapped[int] = mapped_column(primary_key=True)
    order: Mapped[int]
    path: Mapped[str]

    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'))
    category: Mapped['categories.Category'] = relationship(back_populates='photos')

    @validates('order')
    def validate_order(self, key, order):
        if self.id is not None and order <= 0:
            raise ValueError('Порядковый номер должен быть больше 0')

        return order

    @validates('category_id')
    def validate_category_id(self, key, category_id):
        if not db.session.query(
                categories.Category.query.filter(
                    categories.Category.id == category_id,
                    categories.Category.date_deleted == None,
                ).exists()
        ).scalar():
            raise ValueError('Не найдена категория с таким id')

        return category_id


# @event.listens_for(Photo, 'before_insert')
# def set_order_before_insert(mapper, connect, target: Photo):
#     with Session(db.engine) as session:
#         current_max = session.query(func.max(Photo.order)).filter(
#             Photo.category_id == target.category_id
#         ).scalar()
#         if current_max:
#             target.order = current_max + 1
#         else:
#             target.order = 1