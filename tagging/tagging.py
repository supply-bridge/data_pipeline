"""
Usage: With a CSV file which include ids of suppliers, as shown below:
id     ......
12345  ......

Run: python tagging.py csvfile offering_id
The script creates/remove links from all the supplier ids contained in the file to the target offering id

Run: python tagging.py -h
Get the help info
"""

import argparse
import csv
import psycopg2
from psycopg2.extras import execute_values
import sys

DB_CONFIGS = {
    "test": {
        "dbname": "supplybridge",
        "user": "sbadmintest",
        "password": "87pm<z-YVO?jFYtHU}!=g]Nm",
        "host": "supplybridge-pg-test-fc90ks.postgres.database.azure.com",
        "port": "5432",
    },
    "prod": {
        "dbname": "supply-bridge-prod",
        "user": "sbadminprod",
        "password": "uiK>NL6v4EJ[$[<cC-&Ce?7E",
        "host": "supplybridge-pg-prod-txe4ib.postgres.database.azure.com",
        "port": "5432",
    },
}

def connect_to_db(env):
    """连接到数据库"""
    config = DB_CONFIGS.get(env)
    if not config:
        print(f"Invalid environment: {env}")
        sys.exit(1)
    try:
        conn = psycopg2.connect(**config)
        return conn
    except Exception as e:
        print(f"Error connecting to database ({env}): {e}")
        sys.exit(1)

def process_suppliers(csv_file, offering_id, env, unlink=False):
    """处理supplier IDs的链接或解除链接"""
    # 读取CSV文件中的supplier IDs
    supplier_ids = []
    try:
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["id"].strip():  # 确保id不为空
                    supplier_ids.append(int(row["id"]))
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

    if not supplier_ids:
        print("No supplier IDs found in CSV file")
        sys.exit(1)

    print(f"Found {len(supplier_ids)} supplier IDs in CSV file")

    # 连接到数据库
    conn = connect_to_db(env)
    cur = conn.cursor()

    try:
        if unlink:
            # 解除链接
            delete_query = """
            DELETE FROM sb_supplier_offering
            WHERE offering_id = %s AND supplier_id = ANY(%s)
            """
            cur.execute(delete_query, (offering_id, supplier_ids))
            affected_rows = cur.rowcount
            print(
                f"Successfully unlinked {affected_rows} suppliers from offering {offering_id}"
            )
        else:
            # 建立链接
            values = [
                (offering_id, supplier_id) for supplier_id in supplier_ids
            ]
            insert_query = """
            INSERT INTO sb_supplier_offering (offering_id, supplier_id)
            VALUES %s
            ON CONFLICT (offering_id, supplier_id, supplier_offering_group_id) DO NOTHING
            """
            execute_values(cur, insert_query, values)
            print(
                f"Successfully processed {len(supplier_ids)} suppliers for offering {offering_id}"
            )

        # 提交事务
        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"Error processing data: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Link or unlink suppliers to/from an offering using a CSV file"
    )
    parser.add_argument(
        "csv_file", help="Path to CSV file containing supplier IDs"
    )
    parser.add_argument(
        "offering_id",
        type=int,
        help="ID of the offering to link/unlink suppliers to/from",
    )
    parser.add_argument(
        "--unlink",
        action="store_true",
        help="Unlink suppliers instead of linking them",
    )

    parser.add_argument(
        "env",
        choices=["test", "prod"],
        default="test",
        help="Target environment for database operations: 'test' or 'prod' (default: 'test')",
    )

    args = parser.parse_args()

    process_suppliers(args.csv_file, args.offering_id, args.env, args.unlink)


if __name__ == "__main__":
    main()
