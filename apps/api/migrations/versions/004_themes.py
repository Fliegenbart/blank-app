"""Add themes tables for campaign-specific asset generation

Revision ID: 004_themes
Revises: 003
Create Date: 2025-01-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_themes'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create themes table
    op.create_table(
        'themes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('brand_id', sa.String(36), sa.ForeignKey('brands.id'), nullable=False),
        sa.Column('created_by', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('context_json', sa.Text, nullable=True),
        sa.Column('asset_config_json', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_themes_brand_id', 'themes', ['brand_id'])
    op.create_index('ix_themes_brand_slug', 'themes', ['brand_id', 'slug'], unique=True)

    # Create theme_documents table
    op.create_table(
        'theme_documents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('theme_id', sa.String(36), sa.ForeignKey('themes.id'), nullable=False),
        sa.Column('uploaded_by', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('document_type', sa.String(50), nullable=False, server_default='other'),
        sa.Column('file_type', sa.String(50), nullable=False),
        sa.Column('file_size', sa.Integer, nullable=False),
        sa.Column('storage_path', sa.String(500), nullable=False),
        sa.Column('extracted_text', sa.Text, nullable=True),
        sa.Column('summary_json', sa.Text, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='uploaded'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_theme_documents_theme_id', 'theme_documents', ['theme_id'])

    # Create theme_assets table
    op.create_table(
        'theme_assets',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('theme_id', sa.String(36), sa.ForeignKey('themes.id'), nullable=False),
        sa.Column('job_id', sa.String(36), sa.ForeignKey('jobs.id'), nullable=True),
        sa.Column('asset_type', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('storage_path', sa.String(500), nullable=True),
        sa.Column('preview_path', sa.String(500), nullable=True),
        sa.Column('file_size', sa.Integer, nullable=True),
        sa.Column('content_type', sa.String(100), nullable=True),
        sa.Column('print_pdf_path', sa.String(500), nullable=True),
        sa.Column('figma_file_key', sa.String(100), nullable=True),
        sa.Column('variants_json', sa.Text, nullable=True),
        sa.Column('metadata_json', sa.Text, nullable=True),
        sa.Column('generation_params_json', sa.Text, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_theme_assets_theme_id', 'theme_assets', ['theme_id'])
    op.create_index('ix_theme_assets_theme_type', 'theme_assets', ['theme_id', 'asset_type'])

    # Create theme_jobs table
    op.create_table(
        'theme_jobs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('theme_id', sa.String(36), sa.ForeignKey('themes.id'), nullable=False),
        sa.Column('created_by', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('total_assets', sa.Integer, nullable=False, server_default='0'),
        sa.Column('completed_assets', sa.Integer, nullable=False, server_default='0'),
        sa.Column('failed_assets', sa.Integer, nullable=False, server_default='0'),
        sa.Column('asset_job_ids_json', sa.Text, nullable=True),
        sa.Column('error_messages_json', sa.Text, nullable=True),
        sa.Column('rq_job_id', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_theme_jobs_theme_id', 'theme_jobs', ['theme_id'])


def downgrade() -> None:
    op.drop_index('ix_theme_jobs_theme_id', table_name='theme_jobs')
    op.drop_table('theme_jobs')

    op.drop_index('ix_theme_assets_theme_type', table_name='theme_assets')
    op.drop_index('ix_theme_assets_theme_id', table_name='theme_assets')
    op.drop_table('theme_assets')

    op.drop_index('ix_theme_documents_theme_id', table_name='theme_documents')
    op.drop_table('theme_documents')

    op.drop_index('ix_themes_brand_slug', table_name='themes')
    op.drop_index('ix_themes_brand_id', table_name='themes')
    op.drop_table('themes')
