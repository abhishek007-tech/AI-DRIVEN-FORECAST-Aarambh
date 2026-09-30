from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
from app.data.validation import validate_schema


class WeatherDataLoader(ABC):
    """Common ingestion contract for demo and future real NWP data."""

    @abstractmethod
    def load(self) -> pd.DataFrame:
        raise NotImplementedError


class ForecastDataLoader(WeatherDataLoader):
    """CSV loader used by both demo data and future exported NWP/observation pairs."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self) -> pd.DataFrame:
        df = pd.read_csv(self.path, parse_dates=['date'])
        validate_schema(df)
        return df

    def load_csv(self, path: str | Path) -> pd.DataFrame:
        return ForecastDataLoader(path).load()


class DemoDataLoader(ForecastDataLoader):
    """Explicit semantic alias for the synthetic demo source."""
    pass


class RealWeatherDataLoader(WeatherDataLoader):
    """Future adapter contract for real NWP + observation archives.

    The real implementation should normalize source-specific data into the same
    schema accepted by ForecastDataLoader. It intentionally has no fake source.
    """

    def load(self) -> pd.DataFrame:
        raise NotImplementedError(
            'RealWeatherDataLoader is an integration interface. Connect an approved '
            'NWP + observation source and normalize it to the documented schema.'
        )
