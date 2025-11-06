import os
from typing import Any, Optional, Type, Union


def _get_env_value(
    key: str,
    default: Optional[Any] = None,
    cast_to: Type[Any] = str,
) -> Optional[Any]:
    value = os.getenv(key)

    if value is None:
        return default

    if cast_to is str:
        return value
    elif cast_to is int:
        try:
            return int(value)
        except ValueError:
            raise ValueError(
                f"Environment variable {key} expected to be an integer, "
                "but got "
                f"'{value}'"
            )
    elif cast_to is bool:
        return value.lower() in ("true", "1", "yes")
    else:
        raise TypeError(f"Unsupported cast_to type: {cast_to}")


def get_env(
    key: str,
    default: Optional[Any] = None,
    cast_to: Type[Any] = str,
) -> Optional[Any]:
    return _get_env_value(key, default=default, cast_to=cast_to)


def require_env(
    key: str,
    cast_to: Type[Any] = str,
) -> Any:
    value = _get_env_value(key, cast_to=cast_to)
    if value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    return value


def validate_env_variables(
    required_vars: dict[
        str,
        Union[Type[str], Type[int], Type[bool]],
    ],
) -> None:
    """
    Validates a dictionary of required environment variables and their types.

    Args:
        required_vars: A dictionary where keys are environment variable
                       names and values are their expected types (str, int, or bool).

    Raises:
        ValueError: If any required environment variable is not set or
                    cannot be cast.
    """
    for key, cast_to in required_vars.items():
        require_env(key, cast_to=cast_to)
