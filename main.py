import argparse
import os

from dotenv import load_dotenv

from ygg.services.ygg_service import YggService
from ygg.utils.ygg_logs import get_logger

logs = get_logger(logger_name="YggCli")

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Ygg Starter")

    parser.add_argument(
        "-r",
        "--register-contract",
        action="store_true",
        help="Recreate all database objects in the database.",
    )
    parser.add_argument("-f", "--file", "--contract", help="Path to the contract file.")
    parser.add_argument("-c", "--create-db", action="store_true", help="Create the Ygg database.")
    parser.add_argument("-s", "--setup", action="store_true", help="Setup Ygg DuckLake.")
    parser.add_argument("-b", "--build", action="store_true", help="Build the data contract.")

    args = parser.parse_args()
    contracts_input_folder = os.getenv("CONTRACTS_INPUT_FOLDER", None)

    if args.setup:
        logs.info("Setting up Ygg DuckLake")
        YggService.setup()

    if contracts_input_folder and args.file:
        contracts_input_folder = contracts_input_folder + "/"
        contract_data_path = contracts_input_folder + args.file

        if args.register_contract:
            YggService.register_data_contract(contract_data=contract_data_path, insert_on_conflict_ignore=True)

    if args.build:
        YggService.build_contract(contract_data=contract_data_path)


if __name__ == "__main__":
    main()
