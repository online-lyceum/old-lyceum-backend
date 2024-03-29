"""Add user

Revision ID: 086e3bccd639
Revises: 4f58a64a5517
Create Date: 2023-04-26 18:34:55.002979

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '086e3bccd639'
down_revision = '4f58a64a5517'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('access_level', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('user_id', name=op.f('pk_users')),
    sa.UniqueConstraint('name', name=op.f('uq_users_name'))
    )
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)
    op.drop_constraint('fk_semesters_school_id_schools', 'semesters', type_='foreignkey')
    op.create_foreign_key(op.f('fk_semesters_school_id_schools'), 'semesters', 'schools', ['school_id'], ['school_id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('fk_semesters_school_id_schools'), 'semesters', type_='foreignkey')
    op.create_foreign_key('fk_semesters_school_id_schools', 'semesters', 'schools', ['school_id'], ['school_id'])
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
