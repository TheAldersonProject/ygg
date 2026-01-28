"""Shared Model Mixin."""

from typing import Self

import ygg.utils.ygg_logs as log_utils

logs = log_utils.get_logger()


class SharedModelMixin:
    """Shared Model Mixin."""

    def _model_hydrate(self, hydrate_data: dict) -> None:
        """Hydrate the model."""

        if not hydrate_data:
            return

        me = self
        dct = {k: v for k, v in hydrate_data.items() if k in me.model_fields}
        for k, v in dct.items():
            setattr(self, k, v)

    @classmethod
    def inflate(cls, data: dict, model_hydrate: dict | None = None) -> Self:
        """Inflate the model."""

        logs.debug("Inflating Model.", name=cls.__name__)

        model = cls(**data)
        if model_hydrate:
            model._model_hydrate(model_hydrate)

        return model
