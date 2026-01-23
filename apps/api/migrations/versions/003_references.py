"""Add references table for website reference analysis

Revision ID: 003_references
Revises: 002_file_blobs
Create Date: 2024-01-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002_file_blobs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'references',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('brand_id', sa.String(36), sa.ForeignKey('brands.id'), nullable=False),
        sa.Column('created_by', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('urls_json', sa.Text, nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('scraped_data_json', sa.Text, nullable=True),
        sa.Column('structure_json', sa.Text, nullable=True),
        sa.Column('screenshots_path', sa.String(500), nullable=True),
        sa.Column('page_count', sa.Integer, nullable=True),
        sa.Column('total_word_count', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_references_brand_id', 'references', ['brand_id'])


def downgrade() -> None:
    op.drop_index('ix_references_brand_id', table_name='references')
    op.drop_table('references')
