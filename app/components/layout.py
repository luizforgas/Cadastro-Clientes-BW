import reflex as rx
from app.states.auth_state import AuthState


def sidebar_item(name: str, href: str, icon: str) -> rx.Component:
    """A single item in the sidebar."""
    return rx.el.a(
        rx.icon(icon, class_name="h-5 w-5"),
        rx.el.span(name),
        href=href,
        class_name="flex items-center gap-3 rounded-lg px-3 py-2 text-gray-700 transition-all hover:bg-violet-100 hover:text-violet-800",
    )


def sidebar() -> rx.Component:
    """The sidebar for navigation."""
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    rx.icon("box", class_name="h-8 w-8 text-violet-600"),
                    rx.el.span(
                        "BW Soluções", class_name="text-xl font-bold text-gray-800"
                    ),
                    href="/",
                    class_name="flex items-center gap-2",
                ),
                class_name="flex h-16 items-center border-b px-6",
            ),
            rx.el.nav(
                sidebar_item("Dashboard", "/", "layout-dashboard"),
                sidebar_item("Clientes", "/clientes", "users"),
                sidebar_item("Trilha de Auditoria", "/audit-trail", "history"),
                class_name="flex flex-col gap-1 p-4 font-medium",
            ),
            class_name="flex-1 overflow-y-auto",
        ),
        class_name="hidden md:flex flex-col h-screen w-64 border-r bg-gray-50",
    )


def header() -> rx.Component:
    """The header of the application."""
    return rx.el.header(
        rx.el.div(class_name="md:hidden"),
        rx.el.div(class_name="flex-1"),
        rx.el.div(
            rx.el.p(
                "Olá, ",
                rx.el.span(AuthState.authenticated_user, class_name="font-semibold"),
                class_name="text-sm text-gray-700",
            ),
            rx.el.button(
                rx.icon("log-out", class_name="h-5 w-5"),
                "Sair",
                on_click=AuthState.logout,
                class_name="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-100 transition-colors",
            ),
            class_name="flex items-center gap-4",
        ),
        class_name="flex items-center h-16 border-b bg-white px-6 shadow-sm",
    )


def page_layout(child: rx.Component) -> rx.Component:
    """The main layout for all authenticated pages."""
    return rx.el.div(
        sidebar(),
        rx.el.div(
            header(),
            rx.el.main(child, class_name="flex-1 p-6 lg:p-8 overflow-y-auto"),
            class_name="flex flex-col flex-1",
        ),
        class_name="flex min-h-screen w-full bg-gray-100 font-['Lato']",
    )