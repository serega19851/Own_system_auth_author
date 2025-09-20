# app/services/resources/reports_service.py

from datetime import datetime
from typing import List

from app.schemas.resources import ReportResponse, ReportCreate


class ReportsService:
    """Сервис для управления отчетами с mock данными"""
    
    def __init__(self):
        # Перенос MOCK_REPORTS из resources.py
        self.mock_reports = [
            {
                "id": 1,
                "name": "Статистика пользователей",
                "report_type": "user_stats",
                "data": {"active_users": 4, "inactive_users": 1, "total_logins": 42},
                "generated_at": datetime(2025, 9, 16, 8, 0, 0),
                "generated_by": "admin@test.com"
            },
            {
                "id": 2,
                "name": "Отчет по безопасности",
                "report_type": "security",
                "data": {"failed_logins": 3, "suspicious_activity": 0, "blocked_ips": []},
                "generated_at": datetime(2025, 9, 16, 12, 0, 0),
                "generated_by": "moderator@test.com"
            }
        ]
    
    async def get_all_reports(self) -> List[ReportResponse]:
        """Получить все отчеты"""
        return [ReportResponse(**report) for report in self.mock_reports]
    
    async def create_report(self, report_data: ReportCreate, generator_email: str) -> ReportResponse:
        """Создать новый отчет"""
        new_report = {
            "id": self._generate_report_id(),
            "name": report_data.name,
            "report_type": report_data.report_type,
            "data": report_data.data,
            "generated_at": datetime.utcnow(),
            "generated_by": generator_email
        }
        self.mock_reports.append(new_report)
        return ReportResponse(**new_report)
    
    async def export_reports(self, format: str, user_email: str) -> dict:
        """Экспортировать отчеты"""
        export_data = self._prepare_export_data(format)
        return {
            "message": f"Reports exported in {format} format",
            "total_reports": len(self.mock_reports),
            "exported_by": user_email,
            "export_time": datetime.utcnow(),
            "download_url": export_data["download_url"]
        }
    
    def _generate_report_id(self) -> int:
        """Сгенерировать новый ID отчета"""
        if not self.mock_reports:
            return 1
        return max(report["id"] for report in self.mock_reports) + 1
    
    def _prepare_export_data(self, format: str) -> dict:
        """Подготовить данные для экспорта"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return {
            "format": format,
            "download_url": f"/downloads/reports_{timestamp}.{format}",
            "timestamp": timestamp
        }
