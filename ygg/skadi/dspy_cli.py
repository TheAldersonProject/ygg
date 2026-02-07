"""DsPy CLI"""

import os

from dotenv import load_dotenv

from ygg.utils.custom_decorators import singleton


@singleton
class DsPyCli:
    """DsPy CLI"""

    def __init__(self, llm_provider: str | None = None, llm_model: str | None = None, llm_api_key: str | None = None):
        """Initialize DsPy CLI"""

        load_dotenv()
        self._dspy = None
        self._llm_provider: str = llm_provider or "gemini"
        self._llm_model: str = llm_model or "gemini-3-flash-preview"
        self._llm_api_key: str = llm_api_key or os.getenv(f"{self._llm_provider.upper()}_API_KEY")

        self._configure()

    @property
    def dspy(self):
        return self._dspy

    def _configure(self):
        """Configure DsPy CLI"""

        if not self._dspy:
            import dspy

            llm_config: str = f"{self._llm_provider}/{self._llm_model}"
            lm = dspy.LM(model=llm_config, api_key=self._llm_api_key)
            dspy.configure(lm=lm)

            self._dspy = dspy
