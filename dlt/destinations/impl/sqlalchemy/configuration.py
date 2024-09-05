from typing import TYPE_CHECKING, Optional, Any, Final, Type, Dict
import dataclasses

from dlt.common.configuration import configspec
from dlt.common.configuration.specs import ConnectionStringCredentials
from dlt.common.destination.reference import DestinationClientDwhConfiguration

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine, Dialect


@configspec
class SqlalchemyCredentials(ConnectionStringCredentials):
    if TYPE_CHECKING:
        _engine: Optional["Engine"] = None

    username: Optional[str] = None  # e.g. sqlite doesn't need username

    def parse_native_representation(self, native_value: Any) -> None:
        from sqlalchemy.engine import Engine

        if isinstance(native_value, Engine):
            self.engine = native_value
            super().parse_native_representation(
                native_value.url.render_as_string(hide_password=False)
            )
        else:
            super().parse_native_representation(native_value)

    @property
    def engine(self) -> Optional["Engine"]:
        return getattr(self, "_engine", None)  # type: ignore[no-any-return]

    @engine.setter
    def engine(self, value: "Engine") -> None:
        self._engine = value

    def get_dialect(self) -> Optional[Type["Dialect"]]:
        if not self.drivername:
            return None
        # Type-ignore because of ported URL class has no get_dialect method,
        # but here sqlalchemy should be available
        if engine := self.engine:
            return type(engine.dialect)
        return self.to_url().get_dialect()  # type: ignore[attr-defined,no-any-return]


@configspec
class SqlalchemyClientConfiguration(DestinationClientDwhConfiguration):
    destination_type: Final[str] = dataclasses.field(default="sqlalchemy", init=False, repr=False, compare=False)  # type: ignore
    credentials: SqlalchemyCredentials = None
    """SQLAlchemy connection string"""

    engine_args: Dict[str, Any] = dataclasses.field(default_factory=dict)
    """Additional arguments passed to `sqlalchemy.create_engine`"""

    def get_dialect(self) -> Type["Dialect"]:
        return self.credentials.get_dialect()