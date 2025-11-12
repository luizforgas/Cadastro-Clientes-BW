import reflex as rx
from app.components.layout import page_layout
from app.states.client_detail_state import (
    ClientDetailState,
    Contract,
    Service,
    SERVICE_OPTIONS,
    SUPPORT_TYPE_OPTIONS,
    LICENSING_PROVIDER_OPTIONS,
    STATUS_OPTIONS,
)


def detail_item(label: str, value: rx.Var) -> rx.Component:
    """A reusable component for displaying a detail item."""
    return rx.el.div(
        rx.el.p(label, class_name="text-sm font-medium text-gray-500"),
        rx.el.p(value, class_name="text-base text-gray-900"),
    )


def service_row(service: Service) -> rx.Component:
    days_remaining = ClientDetailState.services_days_remaining[service["id"]]
    return rx.el.tr(
        rx.el.td(service["service_type"], class_name="p-3"),
        rx.el.td(
            rx.match(
                service["service_type"],
                ("TAM", f"{service['tam_hours'].to(int)}h"),
                ("Suporte", service["support_type"]),
                ("Licenciamento", service["licensing_provider"]),
                "-",
            ),
            class_name="p-3 text-gray-600",
        ),
        rx.el.td(service["start_date"], class_name="p-3"),
        rx.el.td(service["end_date"], class_name="p-3"),
        rx.el.td(
            rx.el.span(
                service["status"].capitalize(),
                class_name="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800",
            ),
            class_name="p-3",
        ),
        rx.el.td(
            rx.el.span(
                rx.cond(days_remaining < 9999, f"{days_remaining} dias", "N/A"),
                class_name=rx.cond(
                    days_remaining < 9999,
                    rx.cond(
                        days_remaining < 7,
                        "px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800",
                        rx.cond(
                            days_remaining < 30,
                            "px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800",
                            "px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800",
                        ),
                    ),
                    "text-gray-500",
                ),
            ),
            class_name="p-3",
        ),
        rx.el.td(
            rx.el.button(
                rx.icon("file-pen-line", class_name="h-4 w-4"),
                on_click=lambda: ClientDetailState.open_edit_service_modal(service),
                class_name="p-2 text-gray-500 hover:bg-gray-100 rounded-md",
            ),
            rx.el.button(
                rx.icon("trash-2", class_name="h-4 w-4"),
                on_click=lambda: ClientDetailState.confirm_delete_service(
                    service["id"]
                ),
                class_name="p-2 text-red-500 hover:bg-red-100 rounded-md",
            ),
            class_name="p-3 text-right space-x-1",
        ),
        class_name="border-b text-sm text-gray-700",
    )


def contract_card(contract: Contract) -> rx.Component:
    """A card for a single contract, showing its services in a table."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h4(
                    contract["contract_number"],
                    class_name="text-lg font-semibold text-gray-800",
                ),
                rx.el.span(
                    contract["status"].capitalize(),
                    class_name="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800",
                ),
                class_name="flex items-center gap-3",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("circle_plus", class_name="mr-2 h-4 w-4"),
                    "Adicionar Serviço",
                    on_click=lambda: ClientDetailState.open_add_service_modal(
                        contract["id"]
                    ),
                    class_name="flex items-center text-xs px-3 py-1.5 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 font-medium",
                ),
                rx.el.button(
                    rx.icon("file-pen-line", class_name="h-4 w-4"),
                    on_click=lambda: ClientDetailState.open_edit_contract_modal(
                        contract
                    ),
                    class_name="p-2 text-gray-500 hover:bg-gray-100 rounded-md",
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="h-4 w-4"),
                    on_click=lambda: ClientDetailState.confirm_delete_contract(
                        contract["id"]
                    ),
                    class_name="p-2 text-red-500 hover:bg-red-100 rounded-md",
                ),
                class_name="flex items-center gap-1",
            ),
            class_name="flex justify-between items-center p-4 border-b",
        ),
        rx.el.div(
            rx.el.p(contract["notes"], class_name="text-sm text-gray-600 mb-4"),
            rx.cond(
                ClientDetailState.services_by_contract.contains(contract["id"]),
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Serviço",
                                class_name="p-3 text-left font-semibold text-gray-600",
                            ),
                            rx.el.th(
                                "Detalhes",
                                class_name="p-3 text-left font-semibold text-gray-600",
                            ),
                            rx.el.th(
                                "Início",
                                class_name="p-3 text-left font-semibold text-gray-600",
                            ),
                            rx.el.th(
                                "Fim",
                                class_name="p-3 text-left font-semibold text-gray-600",
                            ),
                            rx.el.th(
                                "Status",
                                class_name="p-3 text-left font-semibold text-gray-600",
                            ),
                            rx.el.th(
                                "Renovação",
                                class_name="p-3 text-left font-semibold text-gray-600",
                            ),
                            rx.el.th("", class_name="w-24"),
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            ClientDetailState.services_by_contract[contract["id"]],
                            service_row,
                        )
                    ),
                    class_name="w-full table-auto",
                ),
                rx.el.div(
                    "Nenhum serviço neste contrato. Adicione um para começar.",
                    class_name="text-center text-sm text-gray-500 py-6",
                ),
            ),
            class_name="p-4",
        ),
        class_name="bg-white rounded-lg border shadow-sm",
    )


def contract_form_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title(
                rx.cond(
                    ClientDetailState.is_editing_contract,
                    "Editar Contrato",
                    "Adicionar Novo Contrato",
                ),
                class_name="text-xl font-bold text-gray-800",
            ),
            rx.el.form(
                rx.el.div(
                    rx.el.label("Número do Contrato", class_name="text-sm font-medium"),
                    rx.el.input(
                        name="contract_number",
                        default_value=ClientDetailState.contract_number,
                        class_name="mt-1 w-full p-2 border rounded-md",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.label("Status", class_name="text-sm font-medium"),
                    rx.el.select(
                        rx.foreach(
                            STATUS_OPTIONS,
                            lambda opt: rx.el.option(opt.capitalize(), value=opt),
                        ),
                        name="status",
                        default_value=ClientDetailState.contract_status,
                        class_name="mt-1 w-full p-2 border rounded-md bg-white",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.label("Observações", class_name="text-sm font-medium"),
                    rx.el.textarea(
                        name="notes",
                        default_value=ClientDetailState.contract_notes,
                        class_name="mt-1 w-full p-2 border rounded-md h-24",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancelar",
                        type="button",
                        on_click=ClientDetailState.close_contract_modal,
                        class_name="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300",
                    ),
                    rx.el.button(
                        "Salvar",
                        type="submit",
                        class_name="ml-4 px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700",
                    ),
                    class_name="flex justify-end pt-4 border-t",
                ),
                on_submit=ClientDetailState.save_contract,
            ),
            class_name="bg-white rounded-xl shadow-lg p-6 max-w-lg w-full",
        ),
        open=ClientDetailState.show_contract_modal,
    )


def service_form_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title(
                rx.cond(
                    ClientDetailState.is_editing_service,
                    "Editar Serviço",
                    "Adicionar Novo Serviço",
                ),
                class_name="text-xl font-bold text-gray-800",
            ),
            rx.el.form(
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Tipo de Serviço", class_name="text-sm font-medium"
                        ),
                        rx.el.select(
                            rx.foreach(
                                SERVICE_OPTIONS,
                                lambda opt: rx.el.option(opt, value=opt),
                            ),
                            name="service_type",
                            default_value=ClientDetailState.service_type,
                            on_change=ClientDetailState.set_service_type,
                            class_name="mt-1 w-full p-2 border rounded-md bg-white",
                        ),
                    ),
                    rx.el.div(
                        rx.el.label("Status", class_name="text-sm font-medium"),
                        rx.el.select(
                            rx.foreach(
                                STATUS_OPTIONS,
                                lambda opt: rx.el.option(opt.capitalize(), value=opt),
                            ),
                            name="status",
                            default_value=ClientDetailState.service_status,
                            class_name="mt-1 w-full p-2 border rounded-md bg-white",
                        ),
                    ),
                    rx.el.div(
                        rx.el.label("Data de Início", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="start_date",
                            type="date",
                            default_value=ClientDetailState.service_start_date,
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                    ),
                    rx.el.div(
                        rx.el.label("Data de Fim", class_name="text-sm font-medium"),
                        rx.el.input(
                            name="end_date",
                            type="date",
                            default_value=ClientDetailState.service_end_date,
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                    ),
                    rx.cond(
                        ClientDetailState.service_type == "TAM",
                        rx.el.div(
                            rx.el.label(
                                "Horas de TAM", class_name="text-sm font-medium"
                            ),
                            rx.el.input(
                                name="tam_hours",
                                type="number",
                                default_value=ClientDetailState.service_tam_hours.to_string(),
                                class_name="mt-1 w-full p-2 border rounded-md",
                            ),
                        ),
                    ),
                    rx.cond(
                        ClientDetailState.service_type == "Suporte",
                        rx.el.div(
                            rx.el.label(
                                "Tipo de Suporte", class_name="text-sm font-medium"
                            ),
                            rx.el.select(
                                rx.foreach(
                                    SUPPORT_TYPE_OPTIONS,
                                    lambda opt: rx.el.option(opt, value=opt),
                                ),
                                name="support_type",
                                default_value=ClientDetailState.service_support_type,
                                class_name="mt-1 w-full p-2 border rounded-md bg-white",
                            ),
                        ),
                    ),
                    rx.cond(
                        ClientDetailState.service_type == "Licenciamento",
                        rx.el.div(
                            rx.el.label(
                                "Fornecedor do Licenciamento",
                                class_name="text-sm font-medium",
                            ),
                            rx.el.select(
                                rx.foreach(
                                    LICENSING_PROVIDER_OPTIONS,
                                    lambda opt: rx.el.option(opt, value=opt),
                                ),
                                name="licensing_provider",
                                default_value=ClientDetailState.service_licensing_provider,
                                class_name="mt-1 w-full p-2 border rounded-md bg-white",
                            ),
                        ),
                    ),
                    class_name="grid grid-cols-2 gap-4 max-h-[60vh] overflow-y-auto p-1",
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancelar",
                        type="button",
                        on_click=ClientDetailState.close_service_modal,
                        class_name="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300",
                    ),
                    rx.el.button(
                        "Salvar",
                        type="submit",
                        class_name="ml-4 px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700",
                    ),
                    class_name="flex justify-end pt-4 border-t mt-4",
                ),
                on_submit=ClientDetailState.save_service,
            ),
            class_name="bg-white rounded-xl shadow-lg p-6 max-w-3xl w-full",
        ),
        open=ClientDetailState.show_service_modal,
    )


def delete_confirmation_dialog(
    title, description, on_confirm, on_cancel, open_var
) -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title(title, class_name="text-lg font-bold"),
            rx.radix.primitives.dialog.description(
                description, class_name="mt-2 text-sm text-gray-600"
            ),
            rx.el.div(
                rx.el.button(
                    "Cancelar",
                    on_click=on_cancel,
                    class_name="mt-4 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300",
                ),
                rx.el.button(
                    "Excluir",
                    on_click=on_confirm,
                    class_name="mt-4 ml-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700",
                ),
                class_name="flex justify-end pt-4",
            ),
            class_name="max-w-md p-6 bg-white rounded-lg shadow-xl",
        ),
        open=open_var,
    )


def client_detail_page() -> rx.Component:
    """The page for viewing a single client's details and their contracts."""
    return page_layout(
        rx.cond(
            ClientDetailState.client,
            rx.el.div(
                contract_form_modal(),
                service_form_modal(),
                delete_confirmation_dialog(
                    title="Confirmar Exclusão de Contrato",
                    description="Você tem certeza que deseja excluir este contrato e todos os seus serviços? Esta ação não pode ser desfeita.",
                    on_confirm=ClientDetailState.delete_contract,
                    on_cancel=ClientDetailState.cancel_delete,
                    open_var=ClientDetailState.show_delete_contract_alert,
                ),
                delete_confirmation_dialog(
                    title="Confirmar Exclusão de Serviço",
                    description="Você tem certeza que deseja excluir este serviço?",
                    on_confirm=ClientDetailState.delete_service,
                    on_cancel=ClientDetailState.cancel_delete,
                    open_var=ClientDetailState.show_delete_service_alert,
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.a(
                            rx.icon("arrow-left", class_name="h-4 w-4 mr-2"),
                            "Voltar para Clientes",
                            href="/clientes",
                            class_name="flex items-center text-sm font-medium text-gray-600 hover:text-gray-900",
                        ),
                        rx.el.h1(
                            ClientDetailState.client["company_name"],
                            class_name="text-4xl font-bold text-gray-800 mt-2",
                        ),
                    ),
                    rx.el.button(
                        rx.icon("file-pen-line", class_name="mr-2 h-4 w-4"),
                        "Editar Cliente",
                        on_click=ClientDetailState.trigger_edit_modal,
                        class_name="flex items-center px-4 py-2 bg-violet-600 text-white rounded-lg shadow-sm hover:bg-violet-700 transition-colors font-medium",
                    ),
                    class_name="flex justify-between items-start mb-8",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.h3(
                                "Detalhes do Cliente",
                                class_name="text-lg font-semibold text-gray-700 border-b pb-2 mb-4",
                            ),
                            rx.el.div(
                                detail_item(
                                    "Contratante",
                                    ClientDetailState.client["contact_person"],
                                ),
                                detail_item(
                                    "E-mail", ClientDetailState.client["contact_email"]
                                ),
                                detail_item(
                                    "AM BW Soluções",
                                    ClientDetailState.client["bw_account_manager"],
                                ),
                                detail_item(
                                    "Canal Datadog",
                                    ClientDetailState.client["datadog_channel"],
                                ),
                                class_name="grid grid-cols-2 gap-4",
                            ),
                            class_name="bg-white p-6 rounded-lg shadow-sm border",
                        ),
                        rx.cond(
                            ClientDetailState.client["notes"] != "",
                            rx.el.div(
                                rx.el.h3(
                                    "Observações",
                                    class_name="text-lg font-semibold text-gray-700 border-b pb-2 mb-4",
                                ),
                                rx.el.p(
                                    ClientDetailState.client["notes"],
                                    class_name="text-gray-700 whitespace-pre-wrap",
                                ),
                                class_name="bg-white p-6 rounded-lg shadow-sm border",
                            ),
                        ),
                        class_name="space-y-6 col-span-2 lg:col-span-1",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.h3(
                                "Contratos",
                                class_name="text-lg font-semibold text-gray-700",
                            ),
                            rx.el.button(
                                rx.icon("circle_plus", class_name="mr-2 h-4 w-4"),
                                "Adicionar Contrato",
                                on_click=ClientDetailState.open_add_contract_modal,
                                class_name="flex items-center text-sm px-3 py-1.5 bg-violet-50 text-violet-700 rounded-md hover:bg-violet-100 font-medium",
                            ),
                            class_name="flex justify-between items-center border-b pb-3 mb-4",
                        ),
                        rx.cond(
                            ClientDetailState.client_contracts.length() > 0,
                            rx.el.div(
                                rx.foreach(
                                    ClientDetailState.client_contracts, contract_card
                                ),
                                class_name="space-y-6",
                            ),
                            rx.el.div(
                                rx.icon(
                                    "file-search", class_name="h-12 w-12 text-gray-400"
                                ),
                                rx.el.p(
                                    "Nenhum contrato encontrado.",
                                    class_name="mt-3 text-gray-500",
                                ),
                                rx.el.p(
                                    "Clique em 'Adicionar Contrato' para começar.",
                                    class_name="text-sm text-gray-400",
                                ),
                                class_name="flex flex-col items-center justify-center p-12 text-center bg-gray-50 rounded-lg border-2 border-dashed",
                            ),
                        ),
                        class_name="bg-white p-6 rounded-lg shadow-sm border col-span-2",
                    ),
                    class_name="grid grid-cols-2 gap-6 items-start",
                ),
            ),
            rx.el.div(
                rx.icon(
                    "loader-circle", class_name="h-12 w-12 text-gray-400 animate-spin"
                ),
                rx.el.p(
                    "Carregando cliente...", class_name="mt-4 text-lg text-gray-500"
                ),
                class_name="flex flex-col items-center justify-center h-full",
            ),
        )
    )