from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy.orm import Session
from app import db

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
        self.db = db

    def get_all(self) -> List[T]:
        return self.model.query.all()

    def get_by_id(self, id: int) -> Optional[T]:
        return self.model.query.get(id)

    def create(self, **kwargs) -> T:
        instance = self.model(**kwargs)
        self.db.session.add(instance)
        self.db.session.commit()
        return instance

    def update(self, instance: T, **kwargs) -> T:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        self.db.session.commit()
        return instance

    def delete(self, instance: T) -> bool:
        try:
            self.db.session.delete(instance)
            self.db.session.commit()
            return True
        except Exception:
            self.db.session.rollback()
            return False

    def bulk_create(self, items: List[dict]) -> List[T]:
        instances = [self.model(**item) for item in items]
        self.db.session.bulk_save_objects(instances)
        self.db.session.commit()
        return instances

    def find_by(self, **kwargs) -> List[T]:
        return self.model.query.filter_by(**kwargs).all()

    def find_one_by(self, **kwargs) -> Optional[T]:
        return self.model.query.filter_by(**kwargs).first()

    def exists(self, **kwargs) -> bool:
        return self.model.query.filter_by(**kwargs).first() is not None 