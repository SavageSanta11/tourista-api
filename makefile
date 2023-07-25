# Used by `image`, `push` & `deploy` targets, override as required
IMAGE_REG ?= ghcr.io
IMAGE_REPO ?= benc-uk/python-demoapp
IMAGE_TAG ?= latest

# Used by `deploy` target, sets Azure webap defaults, override as required
AZURE_RES_GROUP ?= temp-demoapps
AZURE_REGION ?= uksouth
AZURE_SITE_NAME ?= pythonapp-$(shell git rev-parse --short HEAD)

# Used by `test-api` target
TEST_HOST ?= localhost:4000

# Don't change
SRC_DIR := .

.PHONY: help lint lint-fix image push run deploy undeploy clean test-api .EXPORT_ALL_VARIABLES
.DEFAULT_GOAL := help

help:  ## 💬 This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

run: venv  ## 🏃 Run the server locally using Python & Flask
	. $(SRC_DIR)/.venv/Scripts/activate \
	&& python app.py

deploy:  ## 🚀 Deploy to Azure Web App 
	az group create --resource-group $(AZURE_RES_GROUP) --location $(AZURE_REGION) -o table
	az deployment group create --template-file deploy/webapp.bicep \
		--resource-group $(AZURE_RES_GROUP) \
		--parameters webappName=$(AZURE_SITE_NAME) \
		--parameters webappImage=$(IMAGE_REG)/$(IMAGE_REPO):$(IMAGE_TAG) -o table 
	@echo "### 🚀 Web app deployed to https://$(AZURE_SITE_NAME).azurewebsites.net/"

lint-fix: venv
	black $(SRC_DIR)

test: venv  ## 🎯 Unit tests for Flask app
	cd tests \
	&& python test1.py

test-report: venv  ## 🎯 Unit tests for Flask app (with report output)
	. $(SRC_DIR)/.venv/Scripts/activate \
	&& pytest -v --junitxml=test-results.xml

clean:  ## 🧹 Clean up project
	rm -rf $(SRC_DIR)/.venv
	rm -rf tests/node_modules
	rm -rf tests/package*
	rm -rf test-results.xml
	rm -rf $(SRC_DIR)/app/__pycache__
	rm -rf $(SRC_DIR)/app/tests/__pycache__
	rm -rf .pytest_cache
	rm -rf $(SRC_DIR)/.pytest_cache

# ============================================================================

venv: $(SRC_DIR)/.venv/touchfile

$(SRC_DIR)/.venv/touchfile: $(SRC_DIR)/requirements.txt
	python -m venv $(SRC_DIR)/.venv
	source $(SRC_DIR)/.venv/Scripts/Activate; pip install -Ur $(SRC_DIR)/requirements.txt
	touch $(SRC_DIR)/.venv/touchfile
