"""Add Twitter analysis fields

Revision ID: add_twitter_analysis_fields
Revises: 
Create Date: 2025-03-16
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_twitter_analysis_fields'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add Twitter analysis fields to kol_profiles table
    op.add_column('kol_profiles', sa.Column('bot_percentage', sa.Float(), nullable=True))
    op.add_column('kol_profiles', sa.Column('bot_analysis_date', sa.DateTime(), nullable=True))
    op.add_column('kol_profiles', sa.Column('content_label', sa.Enum('MEME', 'INVESTMENT', 'EDUCATION', 'BEAUTY', 'TECH', 'GAMING', 'ENTERTAINMENT', 'FINANCE', 'OTHER', name='contentfocus'), nullable=True))
    op.add_column('kol_profiles', sa.Column('content_analysis_date', sa.DateTime(), nullable=True))
    op.add_column('kol_profiles', sa.Column('twitter_token', sa.String(), nullable=True))
    op.add_column('kol_profiles', sa.Column('twitter_refresh_token', sa.String(), nullable=True))
    op.add_column('kol_profiles', sa.Column('twitter_token_expiry', sa.DateTime(), nullable=True))

def downgrade():
    # Remove Twitter analysis fields from kol_profiles table
    op.drop_column('kol_profiles', 'twitter_token_expiry')
    op.drop_column('kol_profiles', 'twitter_refresh_token')
    op.drop_column('kol_profiles', 'twitter_token')
    op.drop_column('kol_profiles', 'content_analysis_date')
    op.drop_column('kol_profiles', 'content_label')
    op.drop_column('kol_profiles', 'bot_analysis_date')
    op.drop_column('kol_profiles', 'bot_percentage')
