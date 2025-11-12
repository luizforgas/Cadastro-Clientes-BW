import reflex as rx
import bcrypt
import time
from typing import TypedDict, Optional


class User(TypedDict):
    username: str
    password_hash: str


USERS_DB: dict[str, User] = {}


class AuthState(rx.State):
    """Handles user authentication, registration, and session management."""

    username: str = ""
    password: str = ""
    confirm_password: str = ""
    error_message: str = ""
    is_loading: bool = False
    authenticated_user: str = ""

    @rx.var
    def is_authenticated(self) -> bool:
        """Checks if a user is currently authenticated."""
        return self.authenticated_user != ""

    def _set_error(self, message: str):
        """Helper to set the error message and clear it after a delay."""
        self.error_message = message

    def _clear_errors(self):
        """Clears all form-related error messages."""
        self.error_message = ""

    def _clear_fields(self):
        """Clears all form fields."""
        self.username = ""
        self.password = ""
        self.confirm_password = ""

    @rx.event
    def register(self, form_data: dict):
        """Registers a new user."""
        self.username = form_data["username"]
        self.password = form_data["password"]
        self.confirm_password = form_data["confirm_password"]
        self._clear_errors()
        if not self.username or not self.password:
            self._set_error("Username and password are required.")
            return
        if self.password != self.confirm_password:
            self._set_error("Passwords do not match.")
            return
        if self.username in USERS_DB:
            self._set_error("Username already exists.")
            return
        hashed_password = bcrypt.hashpw(self.password.encode("utf-8"), bcrypt.gensalt())
        user_data: User = {
            "username": self.username,
            "password_hash": hashed_password.decode("utf-8"),
        }
        USERS_DB[self.username] = user_data
        self.authenticated_user = self.username
        self._clear_fields()
        return rx.redirect("/")

    @rx.event
    def login(self, form_data: dict):
        """Logs in an existing user."""
        self.username = form_data["username"]
        self.password = form_data["password"]
        self.is_loading = True
        yield
        time.sleep(0.5)
        self._clear_errors()
        user_data = USERS_DB.get(self.username)
        if not user_data:
            self.error_message = "Invalid username or password."
            self.is_loading = False
            return
        stored_hash = user_data["password_hash"].encode("utf-8")
        if bcrypt.checkpw(self.password.encode("utf-8"), stored_hash):
            self.authenticated_user = self.username
            self._clear_fields()
            self.is_loading = False
            return rx.redirect("/")
        else:
            self.error_message = "Invalid username or password."
            self.is_loading = False

    @rx.event
    def logout(self):
        """Logs out the current user."""
        self.reset()
        self._clear_fields()
        self._clear_errors()
        return rx.redirect("/login")

    @rx.event
    def on_load(self):
        """Event to run on page load to check authentication."""
        if not self.is_authenticated:
            return rx.redirect("/login")