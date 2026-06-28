"""add insurance and reimbursement tables

Revision ID: 2a040ff7a281
Revises: 099fcdd410c7
Create Date: 2026-06-25 17:34:25.337102

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a040ff7a281'
down_revision = '099fcdd410c7'
branch_labels = None
depends_on = None


def upgrade():
    # 🚀 1. Sirf insurance_products table banegi safely
    op.create_table('insurance_products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('product_cost', sa.Float(), nullable=False),
    sa.Column('total_coverage', sa.Float(), nullable=False),
    sa.Column('product_benefit', sa.JSON(), nullable=False),
    sa.Column('claim_window_days', sa.Integer(), nullable=False),
    sa.Column('validity_months', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    
    #  2. Sirf user_insurances table banegi safely
    op.create_table('user_insurances',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('member_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('purchase_date', sa.DateTime(), nullable=True),
    sa.Column('expiry_date', sa.DateTime(), nullable=False),
    sa.Column('initial_coverage', sa.Float(), nullable=False),
    sa.Column('remaining_coverage', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['member_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['insurance_products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    


def downgrade():
    op.drop_table('user_insurances')
    op.drop_table('insurance_products')