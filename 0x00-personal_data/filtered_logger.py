#!/usr/bin/env python3
"""
Personal data: Contains functions for filtering sensitive data and logging
"""

import re
import logging
from typing import List
import mysql.connector
import os


PII_FIELDS = ("name", "email", "phone", "ssn", "password")


class RedactingFormatter(logging.Formatter):
    """Redacting Formatter class for log messages."""
    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """Constructor for the RedactingFormatter class."""
        self.fields = fields
        super(RedactingFormatter, self).__init__(self.FORMAT)

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats log message by redacting sensitive fields using `filter_datum`
        """
        return filter_datum(self.fields, self.REDACTION,
                            super().format(record), self.SEPARATOR)


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """
    Returns the log message with sensitive fields obfuscated.
    Args:
        fields: list of strings representing all fields to obfuscate.
        redaction: string representing by what the field will be obfuscated.
        message: string representing the log line.
        separator: a string representing the character separating all
                    fields in the log line
    Returns:
        The obfuscated log message.
    """
    for field in fields:
        message = re.sub(rf"{field}=.*?{separator}",
                         f"{field}={redaction}{separator}", message)
    return message


def get_logger() -> logging.Logger:
    """
    Creates a logger named "user_data" and returns it.
    Returns:
        The created logger.
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(RedactingFormatter(PII_FIELDS))
    logger.addHandler(stream_handler)

    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """
    Returns a MySQL database connection.
    Returns:
        The MySQL database connector.
    """
    user_name = os.getenv('PERSONAL_DATA_DB_USERNAME', 'root')
    pword = os.getenv('PERSONAL_DATA_DB_PASSWORD', '')
    host = os.getenv('PERSONAL_DATA_DB_HOST', 'localhost')
    dbase = os.getenv('PERSONAL_DATA_DB_NAME')

    db_connect = mysql.connector.connect(
        user=user_name,
        password=pword,
        host=host,
        database=dbase)
    return db_connect


def main():
    """
    The main function that retrieves data from the database and prints it.
    """
    db_connection = get_db()
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    for row in data:
        for column_value in row:
            print(column_value)

    cursor.close()
    db_connection.close()


if __name__ == '__main__':
    main()
