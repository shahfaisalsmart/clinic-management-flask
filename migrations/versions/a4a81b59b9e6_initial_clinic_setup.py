"""Initial_clinic_Setup

Revision ID: a4a81b59b9e6
Revises: 
Create Date: 2026-07-14 21:15:21.198478

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4a81b59b9e6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    
    # 2. departments
    op.create_table(
        'departments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # 3. insurance_products
    op.create_table(
        'insurance_products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('product_cost', sa.Float(), nullable=False),
        sa.Column('total_coverage', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. roles
    roles_table = op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # --- DATA SEEDING FOR ROLES ---
    op.bulk_insert(
        roles_table,
        [
            {'id': 1, 'name': 'Admin'},
            {'id': 2, 'name': 'Doctor'},
            {'id': 3, 'name': 'Member'}
        ]
    )

    # 5. users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password', sa.String(length=256), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # 6. doctor_configs
    op.create_table(
        'doctor_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('venue_address', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 7. doctor_profiles
    op.create_table(
        'doctor_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=False),
        sa.Column('specialization', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. doctor_availability
    op.create_table(
        'doctor_availability',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('venue_address', sa.String(length=255), nullable=False),
        sa.Column('fee', sa.Float(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 9. doctor_holidays
    op.create_table(
        'doctor_holidays',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('holiday_date', sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 10. appointments
    op.create_table(
        'appointments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('member_id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('slot_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 11. medical_records
    op.create_table(
        'medical_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doctor_id', sa.Integer(), nullable=False),
        sa.Column('member_id', sa.Integer(), nullable=False),
        sa.Column('treatment_name', sa.String(length=150), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 12. user_insurances
    op.create_table(
        'user_insurances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('member_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('purchase_date', sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 13. reimbursement_claims
    op.create_table(
        'reimbursement_claims',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_insurance_id', sa.Integer(), nullable=False),
        sa.Column('medical_record_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # sabse pehle wo tables delete hongi jinme Foreign keys lagi hui h
    op.drop_table('reimbursement_claims')
    op.drop_table('user_insurances')
    op.drop_table('medical_records')
    op.drop_table('appointments')
    op.drop_table('doctor_holidays')
    op.drop_table('doctor_availability')
    
    # doctor_configs pehle delete hongi qki ye doctor_profiles prr depend hai
    op.drop_table('doctor_configs')
    op.drop_table('doctor_profiles')
    
    # and lastly base table delete hongi
    op.drop_table('users')
    op.drop_table('roles')
    op.drop_table('insurance_products')
    op.drop_table('departments')
