# app/services/resources/documents_service.py

from datetime import datetime
from typing import List, Optional

from app.schemas.resources import DocumentResponse, DocumentCreate
from ..base_service import BaseService
from ...exceptions.business_exceptions import ResourceException


class DocumentsService(BaseService):
    """Сервис для управления документами с mock данными"""
    
    def __init__(self):
        super().__init__()
        self.mock_documents = [
            {
                "id": 1,
                "title": "Техническая документация API",
                "content": "Подробное описание всех endpoints системы аутентификации...",
                "author": "admin@test.com",
                "created_at": datetime(2025, 9, 15, 10, 0, 0),
                "is_public": False
            },
            {
                "id": 2,
                "title": "Руководство пользователя",
                "content": "Инструкция по использованию системы для обычных пользователей...",
                "author": "moderator@test.com",
                "created_at": datetime(2025, 9, 16, 14, 30, 0),
                "is_public": True
            },
            {
                "id": 3,
                "title": "Конфиденциальный отчет",
                "content": "Секретная информация доступная только администраторам...",
                "author": "admin@test.com",
                "created_at": datetime(2025, 9, 16, 9, 15, 0),
                "is_public": False
            }
        ]
    
    async def get_all_documents(self) -> List[DocumentResponse]:
        """Получить все документы"""
        try:
            return [DocumentResponse(**doc) for doc in self.mock_documents]
        except Exception as e:
            self._handle_service_error(e, "get_all_documents")
            raise
    
    async def create_document(self, document_data: DocumentCreate, author_email: str) -> DocumentResponse:
        """Создать новый документ"""
        try:
            new_doc = {
                "id": self._generate_document_id(),
                "title": document_data.title,
                "content": document_data.content,
                "author": author_email,
                "created_at": datetime.utcnow(),
                "is_public": document_data.is_public
            }
            self.mock_documents.append(new_doc)
            return DocumentResponse(**new_doc)
        except Exception as e:
            self._handle_service_error(e, "create_document")
            raise
    
    async def delete_document(self, document_id: int, user_email: str) -> dict:
        """Удалить документ"""
        try:
            doc_index = self._find_document_index(document_id)
            
            if doc_index is None:
                raise ResourceException("Document not found", "DOCUMENT_NOT_FOUND")
            
            deleted_doc = self.mock_documents.pop(doc_index)
            return {
                "message": "Document deleted successfully",
                "deleted_document": deleted_doc["title"],
                "deleted_by": user_email
            }
        except ResourceException:
            raise
        except Exception as e:
            self._handle_service_error(e, "delete_document")
            raise
    
    def _find_document_index(self, document_id: int) -> Optional[int]:
        """Найти индекс документа по ID"""
        for i, doc in enumerate(self.mock_documents):
            if doc["id"] == document_id:
                return i
        return None
    
    def _generate_document_id(self) -> int:
        """Сгенерировать новый ID документа"""
        if not self.mock_documents:
            return 1
        return max(doc["id"] for doc in self.mock_documents) + 1
