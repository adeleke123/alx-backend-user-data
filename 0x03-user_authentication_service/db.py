#!/usr/bin/env python3
"""DB module
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from user import Base, User


class DB:
    """DB class for interacting with the database"""

    def __init__(self) -> None:
        """Initialize a new DB instance"""
        self._engine = create_engine("sqlite:///a.db")
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object"""
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """
        Add a new user to the database
        Args:
            email: Email of the user
            hashed_password: Hashed password of the user
        Returns:
            User: User object representing the newly added user
        """
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        return user

    def find_user_by(self, **kwargs) -> User:
        """
        Find a user in the database based on the provided arguments
        Args:
            **kwargs: keyword arguments to filter the user query
        Returns:
            User: User object representing the found user
        Raises:
            NoResultFound: If no user is found
            InvalidRequestError: If an invalid query argument is used
        """
        try:
            user = self._session.query(User).filter_by(**kwargs).one()
            return user
        except NoResultFound:
            raise
        except InvalidRequestError:
            raise

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        Update a user's attributes in the database based on user_id
        Args:
            user_id: ID of the user to be updated
            **kwargs: Keyword arguments for user attribute updates
        Raises:
            ValueError: If an invalid attribute is provided
        Returns: None
        """
        user: User = self.find_user_by(id=user_id)
        for key in kwargs:
            if hasattr(user, key):
                setattr(user, key, kwargs[key])
            else:
                raise ValueError()
        self._session.commit()
