import reflex as rx
from app.states.auth_state import AuthState


class BaseState(rx.State):
    """A base state that provides authentication checks for page loads."""

    @rx.event
    async def require_login(self):
        """
        An event handler that checks if a user is authenticated.
        If not, it redirects to the login page.
        This should be used in the `on_load` trigger for protected pages.
        """
        auth_state = await self.get_state(AuthState)
        if not auth_state.is_authenticated:
            return rx.redirect("/login")