from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from pydantic import BaseModel, ValidationError
from app.repositories.base_repository import BaseRepository
from app.exceptions import ValidationException, NotFoundException, DatabaseException

T = TypeVar('T')
CreateDTO = TypeVar('CreateDTO', bound=BaseModel)
UpdateDTO = TypeVar('UpdateDTO', bound=BaseModel)
ResponseDTO = TypeVar('ResponseDTO', bound=BaseModel)

class BaseService(Generic[T, CreateDTO, UpdateDTO, ResponseDTO]):
    """
    Base service class with generic type support and validation
    T: Database Model
    CreateDTO: DTO for creation
    UpdateDTO: DTO for updates
    ResponseDTO: DTO for responses
    """
    def __init__(
        self,
        repository: BaseRepository[T],
        response_dto_class: Type[ResponseDTO]
    ):
        self.repository = repository
        self.response_dto_class = response_dto_class

    def _to_response_dto(self, model: T) -> ResponseDTO:
        """Convert model to response DTO"""
        try:
            # Convert model to dict, handling SQLAlchemy objects
            model_dict = {
                column.name: getattr(model, column.name)
                for column in model.__table__.columns
            }
            return self.response_dto_class(**model_dict)
        except ValidationError as e:
            raise ValidationException(f"Error converting to response DTO: {str(e)}")

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ResponseDTO]:
        """Get all items with pagination"""
        try:
            items = self.repository.get_all()
            return [self._to_response_dto(item) for item in items[skip:skip + limit]]
        except Exception as e:
            raise DatabaseException(f"Error fetching items: {str(e)}")

    def get_by_id(self, id: int) -> ResponseDTO:
        """Get item by ID"""
        item = self.repository.get_by_id(id)
        if not item:
            raise NotFoundException(f"Item with ID {id} not found")
        return self._to_response_dto(item)

    def create(self, dto: CreateDTO) -> ResponseDTO:
        """Create new item"""
        try:
            # Convert DTO to dict, excluding None values
            create_data = dto.model_dump(exclude_unset=True)
            item = self.repository.create(**create_data)
            return self._to_response_dto(item)
        except ValidationError as e:
            raise ValidationException(f"Validation error: {str(e)}")
        except Exception as e:
            raise DatabaseException(f"Error creating item: {str(e)}")

    def update(self, id: int, dto: UpdateDTO) -> ResponseDTO:
        """Update existing item"""
        item = self.repository.get_by_id(id)
        if not item:
            raise NotFoundException(f"Item with ID {id} not found")
        
        try:
            # Convert DTO to dict, excluding None values
            update_data = dto.model_dump(exclude_unset=True)
            updated_item = self.repository.update(item, **update_data)
            return self._to_response_dto(updated_item)
        except ValidationError as e:
            raise ValidationException(f"Validation error: {str(e)}")
        except Exception as e:
            raise DatabaseException(f"Error updating item: {str(e)}")

    def delete(self, id: int) -> bool:
        """Delete item by ID"""
        item = self.repository.get_by_id(id)
        if not item:
            raise NotFoundException(f"Item with ID {id} not found")
        
        try:
            return self.repository.delete(item)
        except Exception as e:
            raise DatabaseException(f"Error deleting item: {str(e)}")

    def exists(self, **kwargs) -> bool:
        """Check if item exists"""
        try:
            return self.repository.exists(**kwargs)
        except Exception as e:
            raise DatabaseException(f"Error checking existence: {str(e)}")

    async def validate(self, data: Dict[str, Any]) -> bool:
        """
        Override this method to implement custom validation logic
        Returns True if validation passes, raises ValidationException otherwise
        """
        return True 