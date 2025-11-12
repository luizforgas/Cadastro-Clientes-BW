import reflex as rx
from app.states.auth_state import AuthState


def register_form() -> rx.Component:
    """The registration form component."""
    return rx.el.form(
        rx.el.div(
            rx.el.h2(
                "Crie sua conta",
                class_name="text-center text-4xl font-bold tracking-tight text-gray-900",
            ),
            rx.el.p(
                "Já possui uma conta? ",
                rx.el.a(
                    "Faça login",
                    href="/login",
                    class_name="font-semibold text-violet-600 hover:text-violet-500",
                ),
                class_name="mt-2 text-center text-sm text-gray-600",
            ),
            class_name="mb-8",
        ),
        rx.cond(
            AuthState.error_message != "",
            rx.el.div(
                rx.icon("badge_alert", class_name="h-4 w-4 mr-2"),
                rx.el.span(AuthState.error_message),
                class_name="flex items-center bg-red-100 text-red-700 p-3 rounded-lg mb-6 text-sm",
            ),
        ),
        rx.el.div(
            rx.el.label("Usuário", class_name="text-sm font-medium text-gray-700"),
            rx.el.input(
                placeholder="seu.usuario",
                name="username",
                class_name="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-violet-500 focus:border-violet-500",
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.label("Senha", class_name="text-sm font-medium text-gray-700"),
            rx.el.input(
                placeholder="••••••••",
                type="password",
                name="password",
                class_name="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-violet-500 focus:border-violet-500",
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.label(
                "Confirmar Senha", class_name="text-sm font-medium text-gray-700"
            ),
            rx.el.input(
                placeholder="••••••••",
                type="password",
                name="confirm_password",
                class_name="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-1 focus:ring-violet-500 focus:border-violet-500",
            ),
            class_name="mb-6",
        ),
        rx.el.button(
            "Registrar",
            type="submit",
            class_name="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-sm shadow-sm text-sm font-medium text-white bg-violet-600 hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-violet-500",
        ),
        on_submit=AuthState.register,
        reset_on_submit=False,
        class_name="w-full max-w-md",
    )


def register_page() -> rx.Component:
    """The UI for the registration page."""
    return rx.el.div(
        rx.el.div(
            rx.icon("box", class_name="h-10 w-10 text-violet-600 mb-4"),
            class_name="flex justify-center",
        ),
        register_form(),
        class_name="flex min-h-screen flex-col justify-center items-center bg-gray-50 p-4 font-['Lato']",
    )