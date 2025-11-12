import reflex as rx
from app.components.layout import page_layout
from app.states.audit_state import AuditState, AuditEvent


def audit_row(event: AuditEvent) -> rx.Component:
    """A single row in the audit trail table."""
    return rx.el.tr(
        rx.el.td(event["timestamp"], class_name="p-4 text-sm text-gray-600"),
        rx.el.td(event["user"], class_name="p-4 font-medium text-gray-800"),
        rx.el.td(
            rx.el.span(
                event["action"],
                class_name=rx.match(
                    event["action"],
                    (
                        "create",
                        "px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800",
                    ),
                    (
                        "update",
                        "px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800",
                    ),
                    (
                        "delete",
                        "px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800",
                    ),
                    "px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800",
                ),
            ),
            class_name="p-4",
        ),
        rx.el.td(event["client_name"], class_name="p-4 text-gray-700"),
        rx.el.td(
            event["details"], class_name="p-4 text-sm text-gray-500 max-w-md truncate"
        ),
        class_name="border-b hover:bg-gray-50",
    )


def audit_trail_page() -> rx.Component:
    """The page for viewing the audit trail."""
    return page_layout(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Trilha de Auditoria", class_name="text-4xl font-bold text-gray-800"
                ),
                rx.el.div(
                    rx.icon("search", class_name="h-5 w-5 text-gray-400"),
                    rx.el.input(
                        placeholder="Buscar por usuário, ação, cliente...",
                        on_change=AuditState.set_search_query.debounce(300),
                        class_name="w-full pl-10 pr-4 py-2 bg-transparent focus:outline-none",
                        default_value=AuditState.search_query,
                    ),
                    class_name="relative flex items-center w-full max-w-md bg-white border rounded-lg shadow-sm",
                ),
                class_name="flex justify-between items-center mb-8",
            ),
            rx.el.div(
                rx.cond(
                    AuditState.filtered_audit_events.length() > 0,
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th(
                                    "Timestamp",
                                    class_name="p-4 text-left font-semibold text-gray-600",
                                ),
                                rx.el.th(
                                    "Usuário",
                                    class_name="p-4 text-left font-semibold text-gray-600",
                                ),
                                rx.el.th(
                                    "Ação",
                                    class_name="p-4 text-left font-semibold text-gray-600",
                                ),
                                rx.el.th(
                                    "Cliente",
                                    class_name="p-4 text-left font-semibold text-gray-600",
                                ),
                                rx.el.th(
                                    "Detalhes",
                                    class_name="p-4 text-left font-semibold text-gray-600",
                                ),
                            )
                        ),
                        rx.el.tbody(
                            rx.foreach(AuditState.filtered_audit_events, audit_row)
                        ),
                        class_name="w-full table-auto",
                    ),
                    rx.el.div(
                        rx.icon("folder-search", class_name="h-16 w-16 text-gray-400"),
                        rx.el.p(
                            "Nenhum evento de auditoria encontrado.",
                            class_name="mt-4 text-lg text-gray-500",
                        ),
                        class_name="flex flex-col items-center justify-center p-12 bg-white rounded-lg border-2 border-dashed",
                    ),
                ),
                class_name="bg-white rounded-lg shadow-sm border overflow-x-auto",
            ),
        )
    )