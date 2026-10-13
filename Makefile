############################################################
# clean section
############################################################

.PHONY: clean
clean:
	-rm -rf must-gather*/
	-rm kubeconfig

############################################################
# run section
############################################################

.PHONY: run
run: clean
	$(PWD)/collection-scripts/gather

.PHONY: stop
stop:
	@for file in $$(find $(PWD)/collection-scripts -name "gather*") "oc adm inspect"; do \
		echo "Stopping $$(basename "$$file")"; \
		pid=$$(ps -ef | grep "$$file" | grep -v grep | awk '{print $$2}'); \
		if [ -n "$$pid" ]; then \
			kill $$pid; \
		fi; \
	done

.PHONY: kubeconfig
kubeconfig:
	oc config view --minify --raw > kubeconfig

.PHONY: run-image
run-image: kubeconfig
	-mkdir must-gather/
	${CONTAINER_ENGINE} run -v $(PWD)/kubeconfig:/kube/config --env KUBECONFIG=/kube/config \
		-v $(PWD)/must-gather:/must-gather $(IMAGE_NAME_AND_VERSION):$(TAG)

.PHONY: build-and-run-image
build-and-run-image: build-image run-image

############################################################
# build section
############################################################
CONTAINER_ENGINE ?= podman
CONTROLLER_NAME ?= $(shell cat COMPONENT_NAME)
IMG ?= $(CONTROLLER_NAME)
REGISTRY ?= quay.io/stolostron
TAG ?= latest
IMAGE_NAME_AND_VERSION ?= $(REGISTRY)/$(IMG)

.PHONY: build-image
build-image:
	git submodule update --init --recursive
	$(CONTAINER_ENGINE) build --platform linux/amd64 -t $(IMAGE_NAME_AND_VERSION):$(TAG) -f build/Dockerfile .
