# Projeto: Sistema de Cadastro de Clientes - BW Soluções

## ✅ Fases Concluídas (v1.0)
- ✅ Fase 1: Sistema de Autenticação e Layout Base
- ✅ Fase 2: CRUD de Clientes com Formulários Completos  
- ✅ Fase 3: Trilha de Auditoria e Dashboard
- ✅ Fase 4: Página de Detalhes do Cliente

---

## 🔄 REFATORAÇÃO: Múltiplos Contratos por Cliente

### ✅ Fase 1: Reestruturação do Modelo de Dados
- ✅ Criar novo modelo `Contract` separado de `Client`
- ✅ Criar modelo `Service` com campos específicos (tipo, vigência, detalhes)
- ✅ Atualizar modelo `Client` para remover campos de contrato/serviço
- ✅ Estabelecer relacionamento Cliente → Contratos → Serviços
- ✅ Migrar dados existentes para nova estrutura (se houver)

---

### ✅ Fase 2: Simplificação do Formulário de Cliente
- ✅ Remover todos os campos de serviço, contrato e vigência do formulário de cliente
- ✅ Manter apenas: company_name, contact_person, contact_email, bw_account_manager, datadog_channel, notes
- ✅ Atualizar validações do formulário (remover validações de serviços)
- ✅ Formulário simplificado e funcional

---

### Fase 3: Interface de Gerenciamento de Contratos e Serviços (EM ANDAMENTO)
- [ ] Atualizar página de detalhes do cliente para mostrar lista de contratos
- [ ] Criar modal/formulário para adicionar novo contrato ao cliente
- [ ] Adicionar botão "Adicionar Contrato" na página de detalhes
- [ ] Para cada contrato, exibir lista de serviços associados em tabela
- [ ] Criar modal/formulário para adicionar serviço a um contrato específico
- [ ] Implementar campos condicionais por tipo de serviço (TAM → horas, Suporte → tipo, Licenciamento → fornecedor)
- [ ] Adicionar campos de vigência (data início e fim) em cada serviço
- [ ] Implementar cálculo de "dias para renovação" por serviço
- [ ] Adicionar funcionalidade de editar e excluir contratos
- [ ] Adicionar funcionalidade de editar e excluir serviços

---

### Fase 4: Dashboard e Renovações por Serviço
- [ ] Atualizar cálculo de métricas do dashboard (baseado em serviços, não em clientes)
- [ ] Implementar card "Serviços Ativos" (total de serviços com status ativo)
- [ ] Implementar card "Renovações Próximas" (serviços com vigência < 30 dias)
- [ ] Implementar card "Serviços Vencidos" (serviços com data de fim no passado)
- [ ] Criar tabela de "Renovações de Serviços" mostrando: cliente, contrato, tipo de serviço, dias restantes
- [ ] Adicionar indicadores visuais por urgência (vermelho < 7 dias, amarelo < 30 dias, verde > 30 dias)
- [ ] Implementar ordenação por data de vencimento (mais urgentes primeiro)

---

**Status:** Fases 1 e 2 concluídas. Iniciando Fase 3 - Interface de Contratos e Serviços.