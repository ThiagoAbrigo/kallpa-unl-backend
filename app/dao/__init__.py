"""Base DAO class for database operations"""
from app import db


class BaseDAO:
    """Base class for all DAO objects"""
    
    def __init__(self, model):
        self.model = model
    
    def create(self, **kwargs):
        """Create and save a new entity"""
        try:
            instance = self.model(**kwargs)
            db.session.add(instance)
            db.session.commit()
            return instance
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get_by_id(self, id):
        """Get entity by ID"""
        return self.model.query.get(id)
    
    def get_all(self):
        """Get all entities"""
        return self.model.query.all()
    
    def update(self, id, **kwargs):
        """Update an entity"""
        try:
            instance = self.get_by_id(id)
            if not instance:
                return None
            for key, value in kwargs.items():
                setattr(instance, key, value)
            db.session.commit()
            return instance
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self, id):
        """Delete an entity"""
        try:
            instance = self.get_by_id(id)
            if not instance:
                return False
            db.session.delete(instance)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
