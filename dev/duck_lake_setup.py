"""Ygg Repositories Manager"""

from ygg.config import YGG_CONFIG_FILE, YggRepositoryConfiguration
from ygg.utils.commons import get_yaml_content

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


class DuckLakeSetup:
    """Ygg Repositories Manager"""

    def __init__(self, config: YggRepositoryConfiguration):
        """Initialize the Ygg Repositories Manager."""

        if not config:
            raise ValueError("Repository configuration cannot be empty.")

        self._config: YggRepositoryConfiguration = config

    def _configure_ducklake(self) -> None:
        """Configure the DuckLake Metadata Repository."""


if __name__ == "__main__":
    from ygg.config import YggRepositoryConfiguration, YggSetup

    config_content = get_yaml_content(YGG_CONFIG_FILE)
    s = YggSetup(config_data=config_content)
    config_ = YggSetup()
    conf_ = config_.ygg_s3_config
    # conf_ = RepositoryConfiguration(**repo_config)
