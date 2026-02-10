"""add_automation_history_manual

Revision ID: 3f83c5d19672
Revises: abe5a447c0fd
Create Date: 2026-02-09 16:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f83c5d19672'
down_revision = 'abe5a447c0fd'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('automation_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fingerprint', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('namespace', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_automation_history_fingerprint'), 'automation_history', ['fingerprint'], unique=False)
    op.create_index(op.f('ix_automation_history_id'), 'automation_history', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_automation_history_id'), table_name='automation_history')
    op.drop_index(op.f('ix_automation_history_fingerprint'), table_name='automation_history')
    op.drop_table('automation_history')
