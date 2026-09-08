import argparse
from pathlib import Path
import duckdb


def load(csv_path: Path, database: Path) -> None:
    database.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(database)) as con:
        con.execute("create or replace table raw_orders as select * from read_csv_auto(?, header=true)", [str(csv_path)])
        count = con.execute("select count(*) from raw_orders").fetchone()[0]
    print(f"Loaded {count} rows from {csv_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/orders.csv")
    parser.add_argument("--database", default="data/warehouse.duckdb")
    args = parser.parse_args()
    load(Path(args.input), Path(args.database))
