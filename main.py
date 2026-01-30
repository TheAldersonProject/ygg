import argparse
import os

from dotenv import load_dotenv

from ygg.services.contract_manager import ContractManagerService
from ygg.utils.ygg_logs import get_logger

logs = get_logger()

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Ygg Starter")

    parser.add_argument("-r", "--recreate", action="store_true", help="Recreate all database objects in the database.")
    parser.add_argument("-f", "--file", "--contract", required=True, help="Path to the contract file.")
    parser.add_argument("-d", "--db", "--database", default="database.duckdb", help="Database name.")
    parser.add_argument("-o", "--output", help="Path to the output folder.")

    args = parser.parse_args()

    data_folder = args.output or os.getenv("DATA_FOLDER", None)

    logs.debug("Data folder set.", args=args, data_folder=data_folder)
    logs.debug("Destination set.", destination_path=data_folder or "Data will be saved in the current folder.")

    db_url = f"{data_folder + '/' or ''}{args.db}"
    manager = ContractManagerService(recreate_existing=args.recreate, contract_data=args.file, db_url=db_url)
    manager.build_contract()


if __name__ == "__main__":
    main()
