import reflex as rx
from app.components.layout import page_layout
from app.states.client_state import ClientState, Client


def delete_confirmation_dialog() -> rx.Component:
    """A dialog to confirm client deletion."""
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title("Confirmar Exclusão"),
            rx.radix.primitives.dialog.description(
                "Você tem certeza que deseja excluir este cliente e todos os seus contratos? Esta ação não pode ser desfeita."
            ),
            rx.el.div(
                rx.radix.primitives.dialog.close(
                    rx.el.button(
                        "Cancelar",
                        on_click=ClientState.cancel_delete,
                        class_name="mt-4 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors",
                    )
                ),
                rx.el.button(
                    "Excluir",
                    on_click=ClientState.delete_client,
                    class_name="mt-4 ml-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors",
                ),
                class_name="flex justify-end pt-4",
            ),
            class_name="max-w-md p-6 bg-white rounded-lg shadow-xl",
        ),
        open=ClientState.show_delete_alert,
    )


def client_form_modal() -> rx.Component:
    """A simplified modal form for adding and editing basic client information."""
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title(
                rx.cond(
                    ClientState.is_editing, "Editar Cliente", "Adicionar Novo Cliente"
                ),
                class_name="text-2xl font-bold text-gray-800",
            ),
            rx.el.form(
                rx.el.div(
                    rx.cond(
                        ClientState.error_message != "",
                        rx.el.div(
                            rx.icon("badge_alert", class_name="h-4 w-4 mr-2"),
                            ClientState.error_message,
                            class_name="bg-red-100 text-red-700 p-3 rounded-lg mb-4 text-sm flex items-center",
                        ),
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Nome da Empresa",
                            class_name="text-sm font-medium text-gray-700",
                        ),
                        rx.el.input(
                            name="company_name",
                            default_value=ClientState.company_name,
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        class_name="col-span-2",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Contratante",
                            class_name="text-sm font-medium text-gray-700",
                        ),
                        rx.el.input(
                            name="contact_person",
                            default_value=ClientState.contact_person,
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                    ),
                    rx.el.div(
                        rx.el.label(
                            "E-mail do Contratante",
                            class_name="text-sm font-medium text-gray-700",
                        ),
                        rx.el.input(
                            name="contact_email",
                            type="email",
                            default_value=ClientState.contact_email,
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                    ),
                    rx.el.div(
                        rx.el.label(
                            "AM BW Soluções",
                            class_name="text-sm font-medium text-gray-700",
                        ),
                        rx.el.select(
                            rx.foreach(
                                ClientState.AM_OPTIONS,
                                lambda opt: rx.el.option(opt, value=opt),
                            ),
                            name="bw_account_manager",
                            default_value=ClientState.bw_account_manager,
                            class_name="mt-1 w-full p-2 border rounded-md bg-white",
                        ),
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Canal Datadog",
                            class_name="text-sm font-medium text-gray-700",
                        ),
                        rx.el.select(
                            rx.foreach(
                                ClientState.DATADOG_CHANNEL_OPTIONS,
                                lambda opt: rx.el.option(opt, value=opt),
                            ),
                            name="datadog_channel",
                            default_value=ClientState.datadog_channel,
                            class_name="mt-1 w-full p-2 border rounded-md bg-white",
                        ),
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Observações",
                            class_name="text-sm font-medium text-gray-700",
                        ),
                        rx.el.textarea(
                            name="notes",
                            default_value=ClientState.notes,
                            class_name="mt-1 w-full p-2 border rounded-md",
                        ),
                        class_name="col-span-2",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[60vh] overflow-y-auto p-1",
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancelar",
                        type="button",
                        on_click=ClientState.close_modal,
                        class_name="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors",
                    ),
                    rx.el.button(
                        "Salvar",
                        type="submit",
                        class_name="ml-4 px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 transition-colors",
                    ),
                    class_name="flex justify-end pt-6 border-t mt-6",
                ),
                on_submit=ClientState.save_client,
            ),
            class_name="bg-white rounded-xl shadow-lg p-6 max-w-3xl w-full",
        ),
        open=ClientState.show_form_modal,
    )


def client_row(client: Client) -> rx.Component:
    """A single row in the client table."""
    return rx.el.tr(
        rx.el.td(client["company_name"], class_name="p-4 font-medium text-gray-800"),
        rx.el.td(client["contact_person"], class_name="p-4 text-gray-600"),
        rx.el.td(client["contact_email"], class_name="p-4 text-gray-600"),
        rx.el.td(
            rx.el.a(
                rx.icon("eye", class_name="h-4 w-4"),
                href=f"/clientes/{client['id']}",
                class_name="p-2 text-gray-500 hover:bg-gray-100 rounded-md transition-colors",
            ),
            rx.el.button(
                rx.icon("file-pen-line", class_name="h-4 w-4"),
                on_click=lambda: ClientState.open_edit_modal(client["id"]),
                class_name="p-2 text-gray-500 hover:bg-gray-100 rounded-md transition-colors",
            ),
            rx.el.button(
                rx.icon("trash-2", class_name="h-4 w-4"),
                on_click=lambda: ClientState.confirm_delete_client(client["id"]),
                class_name="p-2 text-red-500 hover:bg-red-100 rounded-md transition-colors",
            ),
            class_name="p-4 text-right space-x-2",
        ),
        class_name="border-b hover:bg-gray-50",
    )


def clients_page() -> rx.Component:
    """The main page for listing and managing clients."""
    return page_layout(
        rx.el.div(
            client_form_modal(),
            delete_confirmation_dialog(),
            rx.el.div(
                rx.el.h1("Clientes", class_name="text-4xl font-bold text-gray-800"),
                rx.el.button(
                    rx.icon("circle-plus", class_name="mr-2 h-5 w-5"),
                    "Adicionar Cliente",
                    on_click=ClientState.open_add_modal,
                    class_name="flex items-center px-4 py-2 bg-violet-600 text-white rounded-lg shadow-sm hover:bg-violet-700 transition-colors font-medium",
                ),
                class_name="flex justify-between items-center mb-8",
            ),
            rx.el.div(
                rx.cond(
                    ClientState.clients.length() > 0,
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th(
                                    "Empresa",
                                    class_name="p-4 text-left font-semibold text-gray-600",
                                ),
                                rx.el.th(
                                    "Contratante",
                                    class_name="p-4 text-left font-semibold text-gray-600",
                                ),
                                rx.el.th(
                                    "E-mail",
                                    class_name="p-4 text-left font-semibold text-gray-600",
                                ),
                                rx.el.th("", class_name="w-32"),
                            )
                        ),
                        rx.el.tbody(rx.foreach(ClientState.clients, client_row)),
                        class_name="w-full table-auto",
                    ),
                    rx.el.div(
                        rx.icon("folder-search", class_name="h-16 w-16 text-gray-400"),
                        rx.el.p(
                            "Nenhum cliente cadastrado.",
                            class_name="mt-4 text-lg text-gray-500",
                        ),
                        rx.el.p(
                            "Clique em 'Adicionar Cliente' para começar.",
                            class_name="text-sm text-gray-400",
                        ),
                        class_name="flex flex-col items-center justify-center p-12 bg-white rounded-lg border-2 border-dashed",
                    ),
                ),
                class_name="bg-white rounded-lg shadow-sm border overflow-hidden",
            ),
        )
    )