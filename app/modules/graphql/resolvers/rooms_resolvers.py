from typing import Optional
from ...models.rooms import Room
from ...models.base import db
from ...managers.rooms_manager import RoomsManager
from ..utils import return_validation_error, return_not_found_error, update_fields


def resolve_create_room(*_, input: dict):
    try:
        room = Room(**input)
        RoomsManager.save_room(room)
    except ValueError as validation_error:
        return return_validation_error(validation_error)
    return {'room': room, 'status': {
        'success': True,
    }}


def resolve_update_room(*_, id: int, input: dict):
    room: Room = db.session.query(Room).filter(
        Room.id == id,
        Room.date_deleted == None
    ).first()
    if room is None:
        return return_not_found_error(Room.REPR_MODEL_NAME)
    try:
        update_fields(room, input)
        RoomsManager.save_room(room)
    except ValueError as validation_error:
        return return_validation_error(validation_error)
    print(room.room_number)
    return {'room': room, 'status': {
        'success': True,
    }}


def resolve_delete_room(*_, id: int):
    room: Room = db.session.query(Room).filter(
        Room.id == id,
        Room.date_deleted == None
    ).first()
    if room is None:
        return return_not_found_error(Room.REPR_MODEL_NAME)
    RoomsManager.delete_room(room)
    return {'status': {
        'success': True,
    }}


def resolve_rooms(*_, room_id: Optional[int] = None):
    if room_id:
        return db.session.query(Room).filter_by(id=room_id, date_deleted=None)
    return db.session.query(Room).filter_by(date_deleted=None)