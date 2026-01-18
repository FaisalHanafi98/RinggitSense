"""
Pytest configuration and fixtures for RinggitSense tests
"""
import pytest


@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio as the async backend."""
    return "asyncio"
