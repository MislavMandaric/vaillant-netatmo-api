"""Module containing exceptions when communicating with the Netatmo API."""

from __future__ import annotations


class UnsuportedArgumentsException(Exception):
    """Exception which is thrown when provided parameter is not valid."""


class BadResponseException(Exception):
    """Exception which is thrown when server is unavailable or returns errors."""
