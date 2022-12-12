from typing import List

from apps.iam.constants import PermissionStatusChoices
from apps.iam.models import UserPermission, UserPermissionSnapshot
from core.logger import logger


def sync_snapshot(permission_ids: List[str], action: str):
    def allow(p_map: dict):
        # init
        to_update = list(UserPermissionSnapshot.objects.filter(id__in=p_map.keys()))
        to_update_ids = [p.id for p in to_update]
        to_create = [p for (p_id, p) in p_map.items() if p_id not in to_update_ids]
        # create
        UserPermissionSnapshot.objects.bulk_create(to_create)
        # update
        for p in to_update:
            p.instances = p_map[p.id].instances
            p.all_instances = p_map[p.id].all_instances
        UserPermissionSnapshot.objects.bulk_update(to_update, fields=["instances", "all_instances", "update_at"])
        # log
        logger.info("[SyncUserPermissionSnapshot] Allow => %s", p_map)

    def deny(p_map: dict):
        logger.info("[SyncUserPermissionSnapshot] Deny => %s", p_map)

    # load permissions
    permission_map = {p.id: p for p in UserPermission.objects.filter(id__in=permission_ids)}

    # action
    if action == PermissionStatusChoices.ALLOWED.value:
        allow(permission_map)
    elif action == PermissionStatusChoices.DENIED.value:
        deny(permission_map)
    else:
        logger.warning("[SyncUserPermissionSnapshot] Action Not Support => %s", action)


def update_snapshot(permission_id: str, instances: List[str], all_instances: bool):
    snapshot = UserPermissionSnapshot.objects.get(id=permission_id)
    snapshot.instances = list(set(snapshot.instances) | set(instances))
    snapshot.all_instances = all_instances
    snapshot.save(update_fields=["instances", "all_instances", "update_at"])
    logger.info(
        "[SyncUserPermissionSnapshot] Update => %s; Instances => %s; AllInstances => %s",
        permission_id,
        instances,
        all_instances,
    )
