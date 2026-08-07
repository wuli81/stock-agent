"""add orders client_request_id

Revision ID: bf9e8f205499
Revises: 2b5b36c9bdac
Create Date: 2026-08-07 13:59:08.851160

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'bf9e8f205499'
down_revision: str | None = '2b5b36c9bdac'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # SQLite 需要 batch 模式才能新增带唯一约束的列
    with op.batch_alter_table('orders') as batch_op:
        batch_op.add_column(sa.Column('client_request_id', sa.String(64), nullable=True))
        batch_op.create_unique_constraint('uq_orders_client_request_id', ['client_request_id'])


def downgrade() -> None:
    with op.batch_alter_table('orders') as batch_op:
        batch_op.drop_constraint('uq_orders_client_request_id', type_='unique')
        batch_op.drop_column('client_request_id')
