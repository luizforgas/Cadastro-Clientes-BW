import reflex as rx
from app.states.auth_state import AuthState
from app.states.base_state import BaseState
from app.states.client_detail_state import ClientDetailState
from app.states.client_detail_state import ClientDetailState
from app.states.client_state import ClientState
from app.pages.login import login_page
from app.pages.register import register_page
from app.pages.dashboard import dashboard_page
from app.pages.clients_page import clients_page
from app.pages.audit_trail_page import audit_trail_page
from app.pages.client_detail_page import client_detail_page


def index() -> rx.Component:
    """
    The main app entry point.
    Redirects to the dashboard if authenticated, otherwise to the login page.
    """
    return rx.cond(AuthState.is_authenticated, dashboard_page(), login_page())


auth_and_migrate = [BaseState.require_login, ClientState.run_migration_if_needed]
app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, route="/", on_load=auth_and_migrate)
app.add_page(login_page, route="/login")
app.add_page(register_page, route="/register")
app.add_page(clients_page, route="/clientes", on_load=auth_and_migrate)
app.add_page(audit_trail_page, route="/audit-trail", on_load=auth_and_migrate)
app.add_page(
    client_detail_page,
    route="/clientes/[client_id]",
    on_load=[ClientDetailState.load_client_details, BaseState.require_login],
)