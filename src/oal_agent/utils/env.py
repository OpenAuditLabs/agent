"""Environment utilities."""

import os
from typing import Optional, Type, TypeVar, Union, overload

T = TypeVar("T", str, int, bool)


@overload
def _get_env_value(
    key: str, default: Optional[str] = None, cast_to: Type[str] = str
): ...


@overload
def _get_env_value(
    key: str, default: Optional[int] = None, cast_to: Type[int] = int
): ...


@overload
def _get_env_value(
    key: str, default: Optional[bool] = None, cast_to: Type[bool] = bool
): ...


@overload
def _get_env_value(
    key: str,
    default: Optional[Union[str, int, bool]] = None,
    cast_to: Union[Type[str], Type[int], Type[bool]] = str,
): ...


def _get_env_value(
    key: str,
    default: Optional[Union[str, int, bool]] = None,
    cast_to: Union[Type[str], Type[int], Type[bool]] = str,
) -> Optional[Union[str, int, bool]]:
    """
    Internal helper to get an environment variable, apply a default, and cast its type.
    """
    value = os.getenv(key)

    if value is None:
        if default is not None:
            return default
        return None

    if cast_to is str:
        return value
    elif cast_to is int:
        try:
            return int(value)
        except ValueError:
            raise ValueError(
                f"Environment variable {key} expected to be an integer, "
                f"but got '{value}'"
            )
    elif cast_to is bool:
        # Treat 'true', '1', 'yes' as True (case-insensitive), anything else as False
        return value.lower() in ("true", "1", "yes")
    else:
        raise TypeError(f"Unsupported cast_to type: {cast_to}")


def get_env(
    key: str,
    default: Optional[Union[str, int, bool]] = None,
    cast_to: Union[Type[str], Type[int], Type[bool]] = str,
) -> Optional[Union[str, int, bool]]:
    """
    Get an environment variable with an optional default value and type casting.

    Args:
        key: The name of the environment variable.
        default: The default value to return if the variable is not set.
        cast_to: The type to cast the environment variable to (str, int, or bool).

    Returns:
        The value of the environment variable, cast to the specified type, or the default value.
    """
    return _get_env_value(key, default=default, cast_to=cast_to)


def require_env(
    key: str, cast_to: Union[Type[str], Type[int], Type[bool]] = str
) -> Union[str, int, bool]:
    """
    Get a required environment variable, raising an error if it's not set.
    Supports optional type casting.

    Args:
        key: The name of the environment variable.
        cast_to: The type to cast the environment variable to (str, int, or bool).

    Returns:
        The value of the environment variable, cast to the specified type.

    Raises:
        ValueError: If the required environment variable is not set or cannot be cast.
    """
    value = _get_env_value(key, cast_to=cast_to)
    if value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    return value
