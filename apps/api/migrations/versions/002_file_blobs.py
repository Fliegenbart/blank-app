"""Add file_blobs table for database storage

Revision ID: 002_file_blobs
Revises: 001_initial
Create Date: 2024-01-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_file_blobs'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'file_blobs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('path', sa.String(500), nullable=False, unique=True, index=True),
        sa.Column('data', sa.LargeBinary, nullable=False),
        sa.Column('content_type', sa.String(100), nullable=False, default='application/octet-stream'),
        sa.Column('size', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('file_blobs')
