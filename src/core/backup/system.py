from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import boto3
from src.core.monitoring import MonitoringIntegration

class BackupSystem:
    """Sistema central de backups."""
    
    def __init__(
        self,
        monitoring: MonitoringIntegration,
        backup_bucket: str = "synapse-backups"
    ):
        self.monitoring = monitoring
        self.s3 = boto3.client('s3')
        self.backup_bucket = backup_bucket
        
    async def create_backup(
        self,
        backup_type: str,
        data_path: Optional[Path] = None
    ) -> Dict:
        """Cria novo backup."""
        timestamp = datetime.utcnow().isoformat()
        backup_id = f"{backup_type}-{timestamp}"
        
        try:
            if data_path:
                await self._backup_files(backup_id, data_path)
            
            await self._backup_database(backup_id)
            await self._backup_redis(backup_id)
            await self._backup_qdrant(backup_id)
            
            await self.monitoring.logger.info(
                "Backup created successfully",
                backup_id=backup_id
            )
            
            return {
                "backup_id": backup_id,
                "timestamp": timestamp,
                "status": "success"
            }
            
        except Exception as e:
            await self.monitoring.logger.error(
                "Backup failed",
                error=str(e),
                backup_id=backup_id
            )
            raise
    
    async def restore_backup(
        self,
        backup_id: str,
        components: Optional[List[str]] = None
    ) -> Dict:
        """Restaura backup específico."""
        try:
            if not components:
                components = ["database", "redis", "qdrant", "files"]
                
            for component in components:
                await self._restore_component(backup_id, component)
                
            await self.monitoring.logger.info(
                "Backup restored successfully",
                backup_id=backup_id
            )
            
            return {
                "backup_id": backup_id,
                "components": components,
                "status": "success"
            }
            
        except Exception as e:
            await self.monitoring.logger.error(
                "Restore failed",
                error=str(e),
                backup_id=backup_id
            )
            raise 