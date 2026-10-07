"""add date time

Revision ID: f49ec490ea9a
Revises: 5a6738cc79fa
Create Date: 2026-10-06 15:35:20.400031

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f49ec490ea9a'
down_revision = '5a6738cc79fa'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'created_at',
                sa.DateTime(),
                nullable=False,
                server_default=sa.text('CURRENT_TIMESTAMP')
            )
        )

    # ### end Alembic commands ###

def downgrade():
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###
