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


def get_env_int(
    key: str,
    default: int,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
) -> int:
    """
    Fetches an environment variable as an integer with optional default, min, and max validation.

    Args:
        key: The name of the environment variable.
        default: The default value to return if the environment variable is not set.
        min_value: Optional minimum allowed value for the integer.
        max_value: Optional maximum allowed value for the integer.

    Returns:
        The integer value of the environment variable or the default.

    Raises:
        ValueError: If the environment variable is not a valid integer or
                    is outside the specified min/max range.
    """
    value = _get_env_value(key, default=default, cast_to=int)

    if min_value is not None and value < min_value:
        raise ValueError(
            f"Environment variable {key} value {value} is less than "
            f"the minimum allowed value {min_value}"
        )
    if max_value is not None and value > max_value:
        raise ValueError(
            f"Environment variable {key} value {value} is greater than "
            f"the maximum allowed value {max_value}"
        )
    return value


def get_env_bool(key: str, default: bool) -> bool:
    """
    Fetches an environment variable as a boolean with a default value.

    Args:
        key: The name of the environment variable.
        default: The default value to return if the environment variable is not set.

    Returns:
        The boolean value of the environment variable or the default.
    """
    return _get_env_value(key, default=default, cast_to=bool)


def get_env_list(
    key: str, default: list[str], separator: str = ","
) -> list[str]:
    """
    Fetches an environment variable as a list of strings with a default value and custom separator.

    Args:
        key: The name of the environment variable.
        default: The default value to return if the environment variable is not set.
        separator: The string used to separate values in the environment variable.

    Returns:
        A list of strings from the environment variable or the default.
    """
    value = _get_env_value(key, default=None, cast_to=str)
    if not value:
        return default
    return [item.strip() for item in value.split(separator) if item.strip()]

