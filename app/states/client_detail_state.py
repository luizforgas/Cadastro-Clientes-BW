import reflex as rx
from typing import Optional
import logging
import datetime
import uuid
from .client_state import ClientState, Client
from .auth_state import AuthState
from .audit_state import AuditState
from .contract_state import (
    ContractState,
    Contract,
    Service,
    SERVICE_OPTIONS,
    SUPPORT_TYPE_OPTIONS,
    LICENSING_PROVIDER_OPTIONS,
    STATUS_OPTIONS,
)


class ClientDetailState(rx.State):
    """Manages the state for viewing a single client's details and its contracts/services."""

    client: Optional[Client] = None
    client_contracts: list[Contract] = []
    show_contract_modal: bool = False
    show_service_modal: bool = False
    show_delete_contract_alert: bool = False
    show_delete_service_alert: bool = False
    is_editing_contract: bool = False
    is_editing_service: bool = False
    error_message: str = ""
    contract_id_to_edit: Optional[str] = None
    contract_number: str = ""
    contract_status: str = "ativo"
    contract_notes: str = ""
    service_id_to_edit: Optional[str] = None
    contract_id_for_new_service: Optional[str] = None
    service_type: str = ""
    service_start_date: str = ""
    service_end_date: str = ""
    service_status: str = "ativo"
    service_tam_hours: Optional[int] = None
    service_support_type: str = ""
    service_licensing_provider: str = ""
    id_to_delete: Optional[str] = None
    SERVICE_OPTIONS = SERVICE_OPTIONS
    SUPPORT_TYPE_OPTIONS = SUPPORT_TYPE_OPTIONS
    LICENSING_PROVIDER_OPTIONS = LICENSING_PROVIDER_OPTIONS
    STATUS_OPTIONS = STATUS_OPTIONS

    @rx.var
    async def services_by_contract(self) -> dict[str, list[Service]]:
        """Groups services by their contract ID for easy rendering."""
        contract_state = await self.get_state(ContractState)
        grouped: dict[str, list[Service]] = {}
        if not self.client or not contract_state:
            return grouped
        client_contract_ids = {c["id"] for c in self.client_contracts}
        for service in contract_state.services:
            if service["contract_id"] in client_contract_ids:
                if service["contract_id"] not in grouped:
                    grouped[service["contract_id"]] = []
                grouped[service["contract_id"]].append(service)
        return grouped

    @rx.var
    async def services_days_remaining(self) -> dict[str, int]:
        """Calculates days remaining for each service, accessible by service ID."""
        contract_state = await self.get_state(ContractState)
        days_map: dict[str, int] = {}
        for service in contract_state.services:
            days_map[service["id"]] = self.get_days_remaining(service.get("end_date"))
        return days_map

    @rx.event
    def get_days_remaining(self, end_date_str: str | None) -> int:
        """Helper to calculate days remaining until an end date."""
        if not end_date_str:
            return 9999
        try:
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
            return (end_date - datetime.date.today()).days
        except (ValueError, TypeError) as e:
            logging.exception(f"Error parsing date: {e}")
            return 9999

    def _get_renewal_badge_color(self, days: int) -> str:
        """Helper to determine badge color based on days remaining."""
        if days < 7:
            return "bg-red-100 text-red-800"
        if days < 30:
            return "bg-yellow-100 text-yellow-800"
        return "bg-green-100 text-green-800"

    @rx.event
    async def load_client_details(self):
        """Loads all client-related details, including contracts and services."""
        auth_state = await self.get_state(AuthState)
        if not auth_state.is_authenticated:
            return rx.redirect("/login")
        self.client = None
        self.client_contracts = []
        client_id = self.router.page.params.get("client_id")
        if not client_id:
            logging.error("No client_id in URL, redirecting.")
            return rx.redirect("/clientes")
        client_state = await self.get_state(ClientState)
        contract_state = await self.get_state(ContractState)
        found_client = next(
            (c for c in client_state.clients if c["id"] == client_id), None
        )
        if not found_client:
            logging.warning(f"Client with id {client_id} not found.")
            return rx.redirect("/clientes")
        self.client = found_client
        self.client_contracts = sorted(
            [c for c in contract_state.contracts if c["client_id"] == client_id],
            key=lambda c: c["contract_number"],
        )

    @rx.event
    async def trigger_edit_modal(self):
        """Triggers the edit modal in the ClientState."""
        if self.client:
            client_state = await self.get_state(ClientState)
            client_state.open_edit_modal(self.client["id"])
            return rx.redirect("/clientes")

    def _clear_contract_form(self):
        self.is_editing_contract = False
        self.contract_id_to_edit = None
        self.contract_number = ""
        self.contract_status = "ativo"
        self.contract_notes = ""
        self.error_message = ""

    @rx.event
    def open_add_contract_modal(self):
        self._clear_contract_form()
        self.show_contract_modal = True

    @rx.event
    def open_edit_contract_modal(self, contract: Contract):
        self._clear_contract_form()
        self.is_editing_contract = True
        self.contract_id_to_edit = contract["id"]
        self.contract_number = contract["contract_number"]
        self.contract_status = contract["status"]
        self.contract_notes = contract["notes"]
        self.show_contract_modal = True

    @rx.event
    def close_contract_modal(self):
        self.show_contract_modal = False
        self._clear_contract_form()

    @rx.event
    async def save_contract(self, form_data: dict):
        if not form_data.get("contract_number"):
            self.error_message = "O número do contrato é obrigatório."
            return
        contract_state = await self.get_state(ContractState)
        audit_state = await self.get_state(AuditState)
        auth_state = await self.get_state(AuthState)
        if self.is_editing_contract:
            contract_data = Contract(
                id=self.contract_id_to_edit,
                client_id=self.client["id"],
                contract_number=form_data["contract_number"],
                status=form_data["status"],
                notes=form_data["notes"],
            )
            contract_state.update_contract(contract_data)
            action_details = (
                f"Contrato '{contract_data['contract_number']}' atualizado."
            )
            action_type = "update"
        else:
            contract_data = Contract(
                id=str(uuid.uuid4()),
                client_id=self.client["id"],
                contract_number=form_data["contract_number"],
                status=form_data["status"],
                notes=form_data["notes"],
            )
            contract_state.create_contract(
                self.client["id"],
                contract_data["contract_number"],
                contract_data["notes"],
            )
            action_details = f"Contrato '{contract_data['contract_number']}' criado."
            action_type = "create"
        await audit_state.add_event(
            user=auth_state.authenticated_user,
            action=action_type,
            client_id=self.client["id"],
            client_name=self.client["company_name"],
            details=action_details,
        )
        self.close_contract_modal()
        return ClientDetailState.load_client_details

    @rx.event
    def confirm_delete_contract(self, contract_id: str):
        self.id_to_delete = contract_id
        self.show_delete_contract_alert = True

    @rx.event
    async def delete_contract(self):
        if self.id_to_delete:
            contract_state = await self.get_state(ContractState)
            audit_state = await self.get_state(AuditState)
            auth_state = await self.get_state(AuthState)
            contract_to_delete = next(
                (c for c in contract_state.contracts if c["id"] == self.id_to_delete),
                None,
            )
            if contract_to_delete:
                contract_state.delete_contract(self.id_to_delete)
                await audit_state.add_event(
                    user=auth_state.authenticated_user,
                    action="delete",
                    client_id=self.client["id"],
                    client_name=self.client["company_name"],
                    details=f"Contrato '{contract_to_delete['contract_number']}' e seus serviços foram excluídos.",
                )
        self.show_delete_contract_alert = False
        self.id_to_delete = None
        return ClientDetailState.load_client_details

    def _clear_service_form(self):
        self.is_editing_service = False
        self.service_id_to_edit = None
        self.contract_id_for_new_service = None
        self.service_type = ""
        self.service_start_date = ""
        self.service_end_date = ""
        self.service_status = "ativo"
        self.service_tam_hours = None
        self.service_support_type = ""
        self.service_licensing_provider = ""
        self.error_message = ""

    @rx.event
    def open_add_service_modal(self, contract_id: str):
        self._clear_service_form()
        self.contract_id_for_new_service = contract_id
        self.service_type = SERVICE_OPTIONS[0]
        self.show_service_modal = True

    @rx.event
    def open_edit_service_modal(self, service: Service):
        self._clear_service_form()
        self.is_editing_service = True
        self.service_id_to_edit = service["id"]
        self.contract_id_for_new_service = service["contract_id"]
        self.service_type = service["service_type"]
        self.service_start_date = service["start_date"] or ""
        self.service_end_date = service["end_date"] or ""
        self.service_status = service["status"]
        self.service_tam_hours = service.get("tam_hours")
        self.service_support_type = service.get("support_type") or ""
        self.service_licensing_provider = service.get("licensing_provider") or ""
        self.show_service_modal = True

    @rx.event
    def close_service_modal(self):
        self.show_service_modal = False
        self._clear_service_form()

    @rx.event
    async def save_service(self, form_data: dict):
        if not form_data.get("service_type"):
            self.error_message = "O tipo de serviço é obrigatório."
            return
        contract_state = await self.get_state(ContractState)
        audit_state = await self.get_state(AuditState)
        auth_state = await self.get_state(AuthState)
        contract_id = self.contract_id_for_new_service
        service_data = Service(
            id=self.service_id_to_edit
            if self.is_editing_service
            else str(uuid.uuid4()),
            contract_id=contract_id,
            service_type=form_data["service_type"],
            start_date=form_data.get("start_date"),
            end_date=form_data.get("end_date"),
            status=form_data["status"],
            tam_hours=int(form_data["tam_hours"])
            if form_data.get("tam_hours")
            else None,
            support_type=form_data.get("support_type"),
            licensing_provider=form_data.get("licensing_provider"),
        )
        if self.is_editing_service:
            contract_state.update_service(service_data)
            action_details = f"Serviço '{service_data['service_type']}' atualizado."
            action_type = "update"
        else:
            contract_state.add_service_to_contract(service_data)
            action_details = f"Serviço '{service_data['service_type']}' adicionado."
            action_type = "create"
        await audit_state.add_event(
            user=auth_state.authenticated_user,
            action=action_type,
            client_id=self.client["id"],
            client_name=self.client["company_name"],
            details=action_details,
        )
        self.close_service_modal()
        return ClientDetailState.load_client_details

    @rx.event
    def confirm_delete_service(self, service_id: str):
        self.id_to_delete = service_id
        self.show_delete_service_alert = True

    @rx.event
    async def delete_service(self):
        if self.id_to_delete:
            contract_state = await self.get_state(ContractState)
            audit_state = await self.get_state(AuditState)
            auth_state = await self.get_state(AuthState)
            service_to_delete = next(
                (s for s in contract_state.services if s["id"] == self.id_to_delete),
                None,
            )
            if service_to_delete:
                contract_state.delete_service(self.id_to_delete)
                await audit_state.add_event(
                    user=auth_state.authenticated_user,
                    action="delete",
                    client_id=self.client["id"],
                    client_name=self.client["company_name"],
                    details=f"Serviço '{service_to_delete['service_type']}' foi excluído.",
                )
        self.show_delete_service_alert = False
        self.id_to_delete = None
        return ClientDetailState.load_client_details

    @rx.event
    def cancel_delete(self):
        self.show_delete_contract_alert = False
        self.show_delete_service_alert = False
        self.id_to_delete = None