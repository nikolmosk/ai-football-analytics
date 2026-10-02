from __future__ import annotations
import os
from alembic import context
from sqlalchemy import engine_from_config,pool
from app.models import Base
config=context.config
target_metadata=Base.metadata
def _url(): return os.getenv("DATABASE_URL","postgresql+asyncpg://postgres:postgres@localhost:5432/football").replace("+asyncpg","")
def run_migrations_offline():
 context.configure(url=_url(),target_metadata=target_metadata,literal_binds=True,compare_type=True)
 with context.begin_transaction(): context.run_migrations()
def run_migrations_online():
 cfg=config.get_section(config.config_ini_section) or {}; cfg["sqlalchemy.url"]=_url(); connectable=engine_from_config(cfg,prefix="sqlalchemy.",poolclass=pool.NullPool)
 with connectable.connect() as connection:
  context.configure(connection=connection,target_metadata=target_metadata,compare_type=True)
  with context.begin_transaction(): context.run_migrations()
if context.is_offline_mode(): run_migrations_offline()
else: run_migrations_online()
