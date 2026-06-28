"""add medical records and claims workflows

Revision ID: b06daf682521
Revises: 2a040ff7a281
Create Date: 2026-06-25 23:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b06daf682521'
down_revision = '2a040ff7a281'
branch_labels = None
depends_on = None


def upgrade():
    # 🚀 1. Sirf medical_records table banegi bina purani tables ko chhede
    op.create_table('medical_records',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('member_id', sa.Integer(), nullable=False),
    sa.Column('treatment_name', sa.String(length=100), nullable=False),
    sa.Column('treatment_cost', sa.Float(), nullable=False),
    sa.Column('treatment_date', sa.Date(), nullable=True),
    sa.Column('venue_address', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['member_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    # 🚀 2. Sirf reimbursement_claims table banegi cleanly
    op.create_table('reimbursement_claims',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_insurance_id', sa.Integer(), nullable=False),
    sa.Column('medical_record_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('admin_remarks', sa.String(length=255), nullable=True),
    sa.Column('processed_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['medical_record_id'], ['medical_records.id'], ),
    sa.ForeignKeyConstraint(['user_insurance_id'], ['user_insurances.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('medical_record_id')
    )
    
    
def downgrade():
    op.drop_table('reimbursement_claims')
    op.drop_table('medical_records')