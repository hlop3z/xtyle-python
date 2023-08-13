"""
Module: Preact Database

This module provides a DatabaseManager class for managing Preact components in a SQLite database.
"""

import sqlite3


class DatabaseManager:
    """Preact Database"""

    def __init__(self, db_name: str):
        """
        Initialize the DatabaseManager with the specified database name.

        :param db_name: The name of the SQLite database.
        """
        self.db_name = db_name
        self.initialize_table()

    def _connect(self):
        """
        Connect to the SQLite database and create a cursor.
        """
        self.connection = sqlite3.connect(self.db_name)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def _close(self):
        """
        Commit changes and close the database connection.
        """
        self.connection.commit()
        self.connection.close()

    def set(
        self,
        name: str,
        docs: str = "",
        component: str = "",
        props: str = "",
        style: str = "",
        code_style: str = "",
        code_component: str = "",
    ):
        """
        Add or update a component's information in the database.

        :param name: The name of the component.
        :param docs: Documentation for the component.
        :param component: component of the component.
        :param props: Props of the component.
        :param style: Style of the component.
        :param code_style: Compiled style code.
        :param code_component: Transformed component code.
        """
        self._connect()

        self.cursor.execute("SELECT id FROM Component WHERE name=?", (name,))
        existing_component = self.cursor.fetchone()

        if existing_component:
            # Update existing component
            self.cursor.execute(
                """UPDATE Component SET 
                    docs=?, component=?, props=?, style=?, code_style=?, code_component=? 
                WHERE name=?""",
                (docs, component, props, style, code_style, code_component, name),
            )
        else:
            # Create new component
            self.cursor.execute(
                """INSERT INTO Component (
                name, docs, component, props, style, code_style, code_component
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (name, docs, component, props, style, code_style, code_component),
            )
        self._close()

    def get(self, name: str):
        """
        Retrieve a component's information from the database by its name.

        :param name: The name of the component.
        :return: The component's information as a dictionary.
        """
        self._connect()

        self.cursor.execute("SELECT * FROM Component WHERE name=?", (name,))
        component = self.cursor.fetchone()

        self._close()
        return component

    def all(self):
        """
        Retrieve information of all components from the database.

        :return: A list of dictionaries containing information of all components.
        """
        self._connect()

        self.cursor.execute("SELECT * FROM Component")
        components = self.cursor.fetchall()

        self._close()
        return components

    def delete(self, name: str):
        """
        Delete a component from the database by its name.

        :param name: The name of the component to be deleted.
        """
        self._connect()

        self.cursor.execute("DELETE FROM Component WHERE name=?", (name,))

        self._close()

    def delete_all(self, name: str):
        """
        Delete all components from the database.
        """
        self._connect()

        self.cursor.execute("DELETE FROM Component", (name,))

        self._close()

    def initialize_table(self):
        """
        Initialize the 'Component' table in the database if it doesn't exist.
        """
        self._connect()

        # Create the 'Component' table if it doesn't exist
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS Component (
                id INTEGER PRIMARY KEY, 
                name TEXT UNIQUE, 
                docs TEXT,
                component TEXT,
                props TEXT,
                style TEXT,
                code_style TEXT,
                code_component TEXT
            )"""
        )
        self._close()
