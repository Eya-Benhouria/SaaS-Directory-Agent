"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types (IF NOT EXISTS for idempotency)
    op.execute("DO $$ BEGIN CREATE TYPE submissionstatus AS ENUM ('pending', 'in_progress', 'submitted', 'approved', 'rejected', 'failed', 'retry'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    
    # Create saas_products table
    op.create_table(
        'saas_products',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('tagline', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=False),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('pricing_model', sa.String(length=50), nullable=True),
        sa.Column('features', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('screenshots', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('social_links', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_saas_products_id', 'saas_products', ['id'], unique=False)
    op.create_index('ix_saas_products_name', 'saas_products', ['name'], unique=False)
    
    # Create directories table
    op.create_table(
        'directories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('submission_url', sa.String(length=500), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('priority', sa.Integer(), nullable=True, default=1),
        sa.Column('requires_approval', sa.Boolean(), nullable=True, default=True),
        sa.Column('submission_frequency', sa.String(length=50), nullable=True),
        sa.Column('field_mappings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('extra_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url')
    )
    op.create_index('ix_directories_id', 'directories', ['id'], unique=False)
    op.create_index('ix_directories_name', 'directories', ['name'], unique=False)
    
    # Create submissions table
    op.create_table(
        'submissions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('saas_product_id', sa.Integer(), nullable=False),
        sa.Column('directory_id', sa.Integer(), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'in_progress', 'submitted', 'approved', 'rejected', 'failed', 'retry', name='submissionstatus', create_type=False), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('response_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True, default=0),
        sa.Column('max_retries', sa.Integer(), nullable=True, default=3),
        sa.Column('screenshot_path', sa.String(length=500), nullable=True),
        sa.Column('form_data_sent', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['directory_id'], ['directories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['saas_product_id'], ['saas_products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_submissions_id', 'submissions', ['id'], unique=False)
    
    # Create submission_logs table
    op.create_table(
        'submission_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('submission_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['submission_id'], ['submissions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_submission_logs_id', 'submission_logs', ['id'], unique=False)
    
    # Create form_mappings table
    op.create_table(
        'form_mappings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('directory_id', sa.Integer(), nullable=False),
        sa.Column('field_selector', sa.String(length=500), nullable=False),
        sa.Column('field_type', sa.String(length=50), nullable=True),
        sa.Column('maps_to', sa.String(length=100), nullable=False),
        sa.Column('transform_function', sa.String(length=100), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=True, default=False),
        sa.Column('default_value', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['directory_id'], ['directories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_form_mappings_id', 'form_mappings', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('form_mappings')
    op.drop_table('submission_logs')
    op.drop_table('submissions')
    op.drop_table('directories')
    op.drop_table('saas_products')
    op.execute('DROP TYPE submissionstatus')
