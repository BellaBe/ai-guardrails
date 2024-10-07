# Variables
PYTHON=poetry run python
NATS_SERVER=/opt/homebrew/bin/nats-server
SRC_DIR=src

# Commands
.PHONY: help nats-server start-input-guardrail start-output-guardrail start-orchestrator start-all run-all stop-all test

help:
	@echo "Available commands:"
	@echo "  make nats-server            Start the NATS server"
	@echo "  make start-input-guardrail  Start the Input Guardrail service"
	@echo "  make start-output-guardrail Start the Output Guardrail service"
	@echo "  make start-orchestrator     Start the Orchestrator service"
	@echo "  make start-all              Start all services together using main.py"
	@echo "  make run-all                Run all services individually (Orchestrator, Input Guardrail, Output Guardrail)"
	@echo "  make stop-all               Stop all running services"
	@echo "  make test                   Run unit tests"

# Start NATS server
nats-server:
	@echo "Starting NATS server..."
	$(NATS_SERVER)

# Start Input Guardrail service
start-input-guardrail:
	@echo "Starting Input Guardrail service..."
	poetry run $(PYTHON) -m $(SRC_DIR).services.input_guardrail_service

# Start Output Guardrail service
start-output-guardrail:
	@echo "Starting Output Guardrail service..."
	poetry run $(PYTHON) -m $(SRC_DIR).services.output_guardrail_service

# Start Orchestrator service
start-orchestrator:
	@echo "Starting Orchestrator service..."
	poetry run $(PYTHON) -m $(SRC_DIR).services.orchestrator_service

# Start all services using main.py
start-all:
	@echo "Starting all services using main.py..."
	poetry run $(PYTHON) -m $(SRC_DIR).main

# Run all services concurrently (nats-server must be running separately)
run-all:
	@echo "Running all services individually (orchestrator, input, and output guardrails)..."
	@$(MAKE) start-orchestrator &
	@$(MAKE) start-input-guardrail &
	@$(MAKE) start-output-guardrail &

# Stop all services
stop-all:
	@echo "Stopping all services..."
	@pkill -f 'python $(SRC_DIR)/services/input_guardrail_service.py' || true
	@pkill -f 'python $(SRC_DIR)/services/output_guardrail_service.py' || true
	@pkill -f 'python $(SRC_DIR)/services/orchestrator_service.py' || true
	@pkill -f 'python $(SRC_DIR)/main.py' || true

# Run tests
test:
	@echo "Running tests..."
	poetry run pytest
