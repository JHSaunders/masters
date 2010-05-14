# This configuration is specifically for running tests so you don't have
# to mess up your personal config.

import os

# Use sqlite3 because it's quicker
DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.

IDT_HOME = os.path.abspath(".")
GOFLOW_PATH = IDT_HOME
