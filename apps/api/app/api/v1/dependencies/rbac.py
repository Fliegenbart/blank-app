from typing import List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.brand import Brand, BrandMember, BrandRole


class RBACDependency:
    """Dependency for role-based access control on brands."""

    def __init__(self, allowed_roles: Optional[List[BrandRole]] = None):
        self.allowed_roles = allowed_roles or [BrandRole.OWNER, BrandRole.EDITOR, BrandRole.VIEWER]

    def __call__(
        self,
        brand_id: str,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
    ) -> BrandMember:
        """Check if user has access to the brand with required role."""
        # Superusers have full access
        if current_user.is_superuser:
            brand = db.query(Brand).filter(Brand.id == brand_id).first()
            if not brand:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Brand not found",
                )
            # Create a fake membership for superusers
            fake_member = BrandMember(
                user_id=current_user.id,
                brand_id=brand_id,
                role=BrandRole.OWNER,
            )
            fake_member.brand = brand
            fake_member.user = current_user
            return fake_member

        # Check actual membership
        membership = (
            db.query(BrandMember)
            .filter(
                BrandMember.brand_id == brand_id,
                BrandMember.user_id == current_user.id,
            )
            .first()
        )

        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this brand",
            )

        if membership.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in self.allowed_roles]}",
            )

        return membership


# Convenience instances
require_brand_access = RBACDependency()
require_brand_owner = RBACDependency([BrandRole.OWNER])
require_brand_editor = RBACDependency([BrandRole.OWNER, BrandRole.EDITOR])


def require_brand_role(roles: List[BrandRole]):
    """Create an RBAC dependency for specific roles."""
    return RBACDependency(roles)
