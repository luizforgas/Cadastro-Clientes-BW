import reflex as rx
from app.components.layout import page_layout
from app.states.client_state import ClientState, ClientWithRenewal


def metric_card(title: str, value: rx.Var, icon: str, color: str) -> rx.Component:
    """A card to display a single metric."""
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name=f"h-8 w-8 {color}"),
            class_name="p-3 bg-gray-100 rounded-lg",
        ),
        rx.el.div(
            rx.el.p(title, class_name="text-sm font-medium text-gray-500"),
            rx.el.p(value, class_name="text-2xl font-bold text-gray-800"),
            class_name="",
        ),
        class_name="flex items-center gap-4 p-5 bg-white rounded-xl shadow-sm border",
    )


def dashboard_page() -> rx.Component:
    """The dashboard page, which is a protected route."""
    return page_layout(
        rx.el.div(
            rx.el.h1("Dashboard", class_name="text-4xl font-bold text-gray-800"),
            rx.el.p(
                "Bem-vindo ao sistema de gerenciamento de clientes da BW Soluções.",
                class_name="mt-2 text-base text-gray-600 mb-8",
            ),
            rx.el.div(
                metric_card(
                    "Total de Clientes",
                    ClientState.total_clients.to_string(),
                    "building",
                    "text-blue-500",
                ),
                metric_card(
                    "Serviços Ativos (em breve)", "-", "briefcase", "text-green-500"
                ),
                metric_card(
                    "Renovações Próximas (em breve)",
                    "-",
                    "alarm-clock",
                    "text-yellow-500",
                ),
                metric_card(
                    "Contratos Vencidos (em breve)", "-", "calendar-x", "text-red-500"
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6",
            ),
            rx.el.div(
                rx.el.h2(
                    "Renovações de Serviços (em breve)",
                    class_name="text-xl font-semibold text-gray-700 mb-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon("wrench", class_name="h-12 w-12 text-gray-400"),
                        rx.el.p(
                            "A visualização de renovações por serviço está em desenvolvimento.",
                            class_name="mt-4 text-gray-600",
                        ),
                        class_name="flex flex-col items-center justify-center p-10 text-center bg-gray-50 rounded-lg",
                    ),
                    class_name="bg-white rounded-xl shadow-sm border overflow-hidden",
                ),
                class_name="mt-10",
            ),
            class_name="w-full",
        )
    )