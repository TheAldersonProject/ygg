"""Ygg Repositories Manager"""

from ygg.config import DuckLakeRepository, YggRepositoryConfiguration
from ygg.utils.files_utils import get_yaml_content

"""
# Unique service

*. DuckLake Metadata Repository
    *. ducklake - local - centralized
    *. postgres - decentralized

*. DuckLake Repository
    *. object storage - decentralized - s3
    *. local disk - centralized


# Methods

*. create >> create_if_not_exists | create_or_replace (no data purge)
*. create_or_rebuild | rebuild >> clear data and recreate 
*. __vacuum__ 

"""


class YggRepositoriesManager:
    """Ygg Repositories Manager"""

    def __init__(self, config: YggRepositoryConfiguration):
        """Initialize the Ygg Repositories Manager."""

        if not config:
            raise ValueError("Repository configuration cannot be empty.")

        self._config = config
        if self._config.ducklake_repository == DuckLakeRepository.LOCAL:
            self._create_repository_data_location_folder()

    def _configure_ducklake(self) -> None:
        """Configure the DuckLake Metadata Repository."""

    def _create_repository_data_location_folder(self) -> None:
        """Create the repository data location folder."""

        self._config.ducklake_repository_data_location.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    from ygg.config import YGG_SCHEMA_CONFIG_FILE, DuckLakeRepository, YggRepositoryConfiguration, YggSetup

    config_content = get_yaml_content(YGG_SCHEMA_CONFIG_FILE)
    s = YggSetup(config_data=config_content)
    config_ = YggSetup()
    conf_ = config_.ygg_s3_config
    # conf_ = RepositoryConfiguration(**repo_config)
    print(conf_)
