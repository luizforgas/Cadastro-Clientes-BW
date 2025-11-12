import reflex as rx
from typing import TypedDict, Optional
import datetime
import uuid
import logging


class Service(TypedDict):
    id: str
    contract_id: str
    service_type: str
    start_date: Optional[str]
    end_date: Optional[str]
    status: str
    tam_hours: Optional[int]
    support_type: Optional[str]
    licensing_provider: Optional[str]


class Contract(TypedDict):
    id: str
    client_id: str
    contract_number: str
    status: str
    notes: str


SERVICE_OPTIONS = [
    "Licenciamento",
    "Onboarding",
    "Suporte",
    "Atendimento 24x7",
    "Gestão Cloud",
    "Assessment",
    "TAM",
    "Alocação de Recurso",
]
SUPPORT_TYPE_OPTIONS = ["Starter", "Standard", "Premium", "Outro"]
LICENSING_PROVIDER_OPTIONS = ["BW Soluções", "AWS", "GCP", "Datadog"]
STATUS_OPTIONS = ["ativo", "inativo", "cancelado"]


class ContractState(rx.State):
    """Manages contracts and services for all clients."""

    contracts: list[Contract] = []
    services: list[Service] = []
    migration_completed: bool = False

    @rx.event
    async def migrate_legacy_data(self, legacy_clients: list[dict]):
        """Converts old client data structure into new Contract and Service models."""
        if self.migration_completed or not legacy_clients:
            return
        logging.info(f"Starting data migration for {len(legacy_clients)} clients.")
        for client in legacy_clients:
            if any(
                (
                    c
                    for c in self.contracts
                    if c["client_id"] == client["id"]
                    and c["contract_number"] == "Contrato Legacy"
                )
            ):
                continue
            if client.get("services") or client.get("contract_start_date"):
                contract_id = str(uuid.uuid4())
                legacy_contract = Contract(
                    id=contract_id,
                    client_id=client["id"],
                    contract_number="Contrato Legacy",
                    status="ativo",
                    notes=client.get("notes", ""),
                )
                self.contracts.append(legacy_contract)
                service_names = client.get("services", [])
                if not service_names and client.get("service_name"):
                    service_names = [client.get("service_name")]
                for service_name in service_names:
                    if not service_name:
                        continue
                    new_service = Service(
                        id=str(uuid.uuid4()),
                        contract_id=contract_id,
                        service_type=service_name,
                        start_date=client.get("contract_start_date"),
                        end_date=client.get("contract_end_date"),
                        status="ativo",
                        tam_hours=None,
                        support_type=None,
                        licensing_provider=None,
                    )
                    if service_name == "TAM":
                        new_service["tam_hours"] = client.get("tam_hours")
                    if service_name == "Suporte":
                        new_service["support_type"] = client.get("support_type")
                    if service_name == "Licenciamento":
                        new_service["licensing_provider"] = client.get(
                            "licensing_provider"
                        )
                    self.services.append(new_service)
        self.migration_completed = True
        logging.info("Data migration completed successfully.")

    @rx.event
    def create_contract(self, client_id: str, contract_number: str, notes: str):
        """Creates a new contract for a client."""
        new_contract = Contract(
            id=str(uuid.uuid4()),
            client_id=client_id,
            contract_number=contract_number,
            status="ativo",
            notes=notes,
        )
        self.contracts.append(new_contract)

    @rx.event
    def update_contract(self, contract_data: Contract):
        """Updates an existing contract."""
        self.contracts = [
            contract_data if c["id"] == contract_data["id"] else c
            for c in self.contracts
        ]

    @rx.event
    def delete_contract(self, contract_id: str):
        """Deletes a single contract and its associated services."""
        self.contracts = [c for c in self.contracts if c["id"] != contract_id]
        self.services = [s for s in self.services if s["contract_id"] != contract_id]

    @rx.event
    def add_service_to_contract(self, service_data: Service):
        """Adds a new service to an existing contract."""
        self.services.append(service_data)

    @rx.event
    def update_service(self, service_data: Service):
        """Updates an existing service."""
        self.services = [
            service_data if s["id"] == service_data["id"] else s for s in self.services
        ]

    @rx.event
    def delete_service(self, service_id: str):
        """Deletes a single service."""
        self.services = [s for s in self.services if s["id"] != service_id]

    @rx.event
    def delete_contracts_for_client(self, client_id: str):
        """Deletes all contracts and their associated services for a given client."""
        contracts_to_delete = [c for c in self.contracts if c["client_id"] == client_id]
        contract_ids_to_delete = {c["id"] for c in contracts_to_delete}
        self.contracts = [c for c in self.contracts if c["client_id"] != client_id]
        self.services = [
            s for s in self.services if s["contract_id"] not in contract_ids_to_delete
        ]

    def _get_days_remaining(self, end_date_str: str) -> int:
        """Calculates the number of days remaining until a service's end date."""
        if not end_date_str:
            return -999
        try:
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
            today = datetime.date.today()
            return (end_date - today).days
        except (ValueError, TypeError) as e:
            logging.exception(f"Error parsing date '{end_date_str}': {e}")
            return -999