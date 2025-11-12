import reflex as rx
from typing import TypedDict, Optional, cast
import datetime
import uuid
import logging
from app.states.audit_state import AuditState
from app.states.auth_state import AuthState
from app.states.contract_state import ContractState


class Client(TypedDict):
    id: str
    company_name: str
    contact_person: str
    contact_email: str
    datadog_channel: str
    bw_account_manager: str
    notes: str


class ClientWithRenewal(Client):
    days_remaining: int


class ClientState(rx.State):
    """Manages the state for the customer CRUD operations."""

    clients: list[Client] = []
    show_form_modal: bool = False
    is_editing: bool = False
    current_client_id: Optional[str] = None
    company_name: str = ""
    contact_person: str = ""
    contact_email: str = ""
    datadog_channel: str = ""
    bw_account_manager: str = ""
    notes: str = ""
    show_delete_alert: bool = False
    client_to_delete_id: Optional[str] = None
    error_message: str = ""
    AM_OPTIONS = [
        "Camila Nogueira",
        "Isabela Morassi",
        "Carolina Cunha",
        "Raphael Terra",
    ]
    DATADOG_CHANNEL_OPTIONS = ["Enterprise", "Mid-Market", "Comercial", "Outro"]

    @rx.var
    def clients_with_renewal(self) -> list[ClientWithRenewal]:
        """Returns clients with their contract renewal status. (Temporary)"""
        return []

    @rx.var
    def total_clients(self) -> int:
        return len(self.clients)

    @rx.var
    def total_services(self) -> int:
        return 0

    @rx.var
    def renewals_in_30_days(self) -> int:
        return 0

    @rx.var
    def expired_contracts(self) -> int:
        return 0

    @rx.var
    def upcoming_renewals(self) -> list[ClientWithRenewal]:
        """Returns clients with contracts expiring in the next 60 days. (Temporary)"""
        return []

    def _clear_form(self):
        """Resets all form fields to their default state."""
        self.company_name = ""
        self.contact_person = ""
        self.contact_email = ""
        self.datadog_channel = ""
        self.bw_account_manager = ""
        self.notes = ""
        self.is_editing = False
        self.current_client_id = None
        self.error_message = ""

    @rx.event
    def set_bw_account_manager(self, value: str):
        self.bw_account_manager = value

    @rx.event
    def set_datadog_channel(self, value: str):
        self.datadog_channel = value

    @rx.event
    def open_add_modal(self):
        """Opens the modal to add a new client."""
        self._clear_form()
        self.is_editing = False
        self.show_form_modal = True

    @rx.event
    def open_edit_modal(self, client_id: str):
        """Opens the modal to edit an existing client."""
        client = next((c for c in self.clients if c["id"] == client_id), None)
        if client:
            self.current_client_id = client["id"]
            self.company_name = client["company_name"]
            self.contact_person = client["contact_person"]
            self.contact_email = client["contact_email"]
            self.datadog_channel = client["datadog_channel"]
            self.bw_account_manager = client["bw_account_manager"]
            self.notes = client["notes"]
            self.is_editing = True
            self.show_form_modal = True
            self.error_message = ""

    @rx.event
    def close_modal(self):
        """Closes the client form modal."""
        self.show_form_modal = False
        self._clear_form()

    @rx.event
    async def save_client(self, form_data: dict):
        """Saves a new or existing client and logs the audit event."""
        self.company_name = form_data.get("company_name", "")
        self.contact_person = form_data.get("contact_person", "")
        self.contact_email = form_data.get("contact_email", "")
        self.bw_account_manager = form_data.get(
            "bw_account_manager", self.bw_account_manager
        )
        self.datadog_channel = form_data.get("datadog_channel", self.datadog_channel)
        self.notes = form_data.get("notes", "")
        if not self.company_name or not self.contact_person or (not self.contact_email):
            self.error_message = (
                "Nome da Empresa, Contratante e E-mail são obrigatórios."
            )
            return
        auth = await self.get_state(AuthState)
        audit = await self.get_state(AuditState)
        client_data: Client = {
            "id": self.current_client_id if self.is_editing else str(uuid.uuid4()),
            "company_name": self.company_name,
            "contact_person": self.contact_person,
            "contact_email": self.contact_email,
            "datadog_channel": self.datadog_channel,
            "bw_account_manager": self.bw_account_manager,
            "notes": self.notes,
        }
        if self.is_editing:
            original_client = next(
                (c for c in self.clients if c["id"] == self.current_client_id), None
            )
            self.clients = [
                client_data if c["id"] == self.current_client_id else c
                for c in self.clients
            ]
            if original_client:
                details = self._get_changed_fields(original_client, client_data)
                if details:
                    await audit.add_event(
                        user=auth.authenticated_user,
                        action="update",
                        client_id=client_data["id"],
                        client_name=client_data["company_name"],
                        details=details,
                    )
        else:
            self.clients.append(client_data)
            await audit.add_event(
                user=auth.authenticated_user,
                action="create",
                client_id=client_data["id"],
                client_name=client_data["company_name"],
                details=f"Cliente '{client_data['company_name']}' criado.",
            )
        self.close_modal()

    @rx.event
    def confirm_delete_client(self, client_id: str):
        """Shows the delete confirmation alert."""
        self.show_delete_alert = True
        self.client_to_delete_id = client_id

    @rx.event
    def cancel_delete(self):
        """Cancels the deletion process."""
        self.show_delete_alert = False
        self.client_to_delete_id = None

    @rx.event
    async def delete_client(self):
        """Deletes the selected client and logs the audit event."""
        if self.client_to_delete_id:
            client_to_delete = next(
                (c for c in self.clients if c["id"] == self.client_to_delete_id), None
            )
            if client_to_delete:
                auth = await self.get_state(AuthState)
                audit = await self.get_state(AuditState)
                contract_state = await self.get_state(ContractState)
                contract_state.delete_contracts_for_client(self.client_to_delete_id)
                await audit.add_event(
                    user=auth.authenticated_user,
                    action="delete",
                    client_id=client_to_delete["id"],
                    client_name=client_to_delete["company_name"],
                    details=f"Cliente '{client_to_delete['company_name']}' e todos os seus contratos foram excluídos.",
                )
                self.clients = [
                    c for c in self.clients if c["id"] != self.client_to_delete_id
                ]
        self.cancel_delete()

    def _get_changed_fields(self, old_data: Client, new_data: Client) -> str:
        """Compares two client dicts and returns a string of changes."""
        changes = []
        field_names = {
            "company_name": "Nome da Empresa",
            "contact_person": "Contratante",
            "contact_email": "E-mail",
            "datadog_channel": "Canal Datadog",
            "bw_account_manager": "AM BW Soluções",
            "notes": "Observações",
        }
        for key, new_value in new_data.items():
            old_value = old_data.get(key)
            if old_value != new_value:
                field_name = field_names.get(key, key)
                old_value_str = str(old_value or "N/A")
                new_value_str = str(new_value or "N/A")
                changes.append(
                    f"{field_name}: de '{old_value_str}' para '{new_value_str}'"
                )
        return "; ".join(changes)

    @rx.event
    async def run_migration_if_needed(self):
        """Triggers the data migration from old client structure to new contract structure."""
        contract_state = await self.get_state(ContractState)
        if not contract_state.migration_completed:
            await contract_state.migrate_legacy_data(self.clients)