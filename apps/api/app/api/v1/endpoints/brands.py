from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.dependencies.auth import get_current_active_user
from app.api.v1.dependencies.rbac import require_brand_access, require_brand_editor, require_brand_owner
from app.models.user import User
from app.models.organization import Organization
from app.models.brand import Brand, BrandMember, BrandRole
from app.schemas.brand import (
    BrandCreate,
    BrandUpdate,
    BrandResponse,
    BrandMemberCreate,
    BrandMemberResponse,
    BrandMemberUpdate,
)

router = APIRouter(prefix="/brands", tags=["brands"])


@router.post("", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
def create_brand(
    brand_data: BrandCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new brand."""
    # Check if slug is unique
    existing_brand = db.query(Brand).filter(Brand.slug == brand_data.slug).first()
    if existing_brand:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand slug already exists",
        )

    # Create or get organization
    if brand_data.organization_id:
        org = db.query(Organization).filter(Organization.id == brand_data.organization_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
    else:
        # Create default org for user
        org = Organization(
            name=f"{current_user.email}'s Organization",
            slug=f"org-{current_user.id[:8]}",
        )
        db.add(org)
        db.flush()

    # Create brand
    brand = Brand(
        name=brand_data.name,
        slug=brand_data.slug,
        description=brand_data.description,
        organization_id=org.id,
    )
    db.add(brand)
    db.flush()

    # Add creator as owner
    membership = BrandMember(
        user_id=current_user.id,
        brand_id=brand.id,
        role=BrandRole.OWNER,
    )
    db.add(membership)
    db.commit()
    db.refresh(brand)

    # Construct response with properly formatted members
    members = [
        BrandMemberResponse(
            id=membership.id,
            user_id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            role=membership.role,
            created_at=membership.created_at,
        )
    ]

    return BrandResponse(
        id=brand.id,
        name=brand.name,
        slug=brand.slug,
        description=brand.description,
        organization_id=brand.organization_id,
        created_at=brand.created_at,
        updated_at=brand.updated_at,
        members=members,
    )


@router.get("", response_model=List[BrandResponse])
def list_brands(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List all brands the user has access to."""
    if current_user.is_superuser:
        brands = db.query(Brand).all()
    else:
        brands = (
            db.query(Brand)
            .join(BrandMember)
            .filter(BrandMember.user_id == current_user.id)
            .all()
        )

    # Convert to response without members (for list view)
    return [
        BrandResponse(
            id=brand.id,
            name=brand.name,
            slug=brand.slug,
            description=brand.description,
            organization_id=brand.organization_id,
            created_at=brand.created_at,
            updated_at=brand.updated_at,
            members=None,
        )
        for brand in brands
    ]


@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(
    brand_id: str,
    membership: BrandMember = Depends(require_brand_access),
    db: Session = Depends(get_db),
):
    """Get a brand by ID."""
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    # Load members for response
    members = []
    for m in brand.members:
        members.append(
            BrandMemberResponse(
                id=m.id,
                user_id=m.user_id,
                email=m.user.email,
                full_name=m.user.full_name,
                role=m.role,
                created_at=m.created_at,
            )
        )

    return BrandResponse(
        id=brand.id,
        name=brand.name,
        slug=brand.slug,
        description=brand.description,
        organization_id=brand.organization_id,
        created_at=brand.created_at,
        updated_at=brand.updated_at,
        members=members,
    )


@router.put("/{brand_id}", response_model=BrandResponse)
def update_brand(
    brand_id: str,
    brand_data: BrandUpdate,
    membership: BrandMember = Depends(require_brand_editor),
    db: Session = Depends(get_db),
):
    """Update a brand."""
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    if brand_data.name is not None:
        brand.name = brand_data.name
    if brand_data.description is not None:
        brand.description = brand_data.description

    db.commit()
    db.refresh(brand)

    return BrandResponse(
        id=brand.id,
        name=brand.name,
        slug=brand.slug,
        description=brand.description,
        organization_id=brand.organization_id,
        created_at=brand.created_at,
        updated_at=brand.updated_at,
        members=None,
    )


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand(
    brand_id: str,
    membership: BrandMember = Depends(require_brand_owner),
    db: Session = Depends(get_db),
):
    """Delete a brand."""
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    db.delete(brand)
    db.commit()


@router.post("/{brand_id}/members", response_model=BrandMemberResponse, status_code=status.HTTP_201_CREATED)
def add_member(
    brand_id: str,
    member_data: BrandMemberCreate,
    membership: BrandMember = Depends(require_brand_owner),
    db: Session = Depends(get_db),
):
    """Add a member to a brand."""
    # Find user by email
    user = db.query(User).filter(User.email == member_data.user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if already a member
    existing = (
        db.query(BrandMember)
        .filter(BrandMember.brand_id == brand_id, BrandMember.user_id == user.id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member",
        )

    # Add member
    new_member = BrandMember(
        user_id=user.id,
        brand_id=brand_id,
        role=member_data.role,
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return BrandMemberResponse(
        id=new_member.id,
        user_id=new_member.user_id,
        email=user.email,
        full_name=user.full_name,
        role=new_member.role,
        created_at=new_member.created_at,
    )


@router.put("/{brand_id}/members/{member_id}", response_model=BrandMemberResponse)
def update_member(
    brand_id: str,
    member_id: str,
    member_data: BrandMemberUpdate,
    membership: BrandMember = Depends(require_brand_owner),
    db: Session = Depends(get_db),
):
    """Update a member's role."""
    member = (
        db.query(BrandMember)
        .filter(BrandMember.id == member_id, BrandMember.brand_id == brand_id)
        .first()
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )

    member.role = member_data.role
    db.commit()
    db.refresh(member)

    user = member.user
    return BrandMemberResponse(
        id=member.id,
        user_id=member.user_id,
        email=user.email if user else "",
        full_name=user.full_name if user else None,
        role=member.role,
        created_at=member.created_at,
    )


@router.delete("/{brand_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    brand_id: str,
    member_id: str,
    membership: BrandMember = Depends(require_brand_owner),
    db: Session = Depends(get_db),
):
    """Remove a member from a brand."""
    member = (
        db.query(BrandMember)
        .filter(BrandMember.id == member_id, BrandMember.brand_id == brand_id)
        .first()
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found",
        )

    # Prevent removing the last owner
    if member.role == BrandRole.OWNER:
        owner_count = (
            db.query(BrandMember)
            .filter(BrandMember.brand_id == brand_id, BrandMember.role == BrandRole.OWNER)
            .count()
        )
        if owner_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the last owner",
            )

    db.delete(member)
    db.commit()
