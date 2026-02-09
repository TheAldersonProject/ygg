import argparse
import os

from dotenv import load_dotenv

from ygg.services.data_contract_service_manager import DataContractServiceManager
from ygg.utils.ygg_logs import get_logger

logs = get_logger()

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Ygg Starter")

    parser.add_argument(
        "-r",
        "--recreate",
        action="store_true",
        help="Recreate all database objects in the database.",
    )
    parser.add_argument("-f", "--file", "--contract", help="Path to the contract file.")
    parser.add_argument("-c", "--create-db", action="store_true", help="Create the Ygg database.")

    args = parser.parse_args()
    contracts_input_folder = os.getenv("CONTRACTS_INPUT_FOLDER", None)

    contract_data_path = None
    if contracts_input_folder and args.file:
        contracts_input_folder = contracts_input_folder + "/"
        contract_data_path = contracts_input_folder + args.file

    manager = DataContractServiceManager(recreate_existing=args.recreate, contract_data=contract_data_path)
    if args.create_db:
        manager.build()

    if args.file:
        manager.build_contract()


if __name__ == "__main__":
    main()
