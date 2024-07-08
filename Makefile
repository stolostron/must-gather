############################################################
# clean section
############################################################

.PHONY: clean
clean:
	-rm -rf must-gather/

############################################################
# run section
############################################################

.PHONY: run
run: clean
	./collection-scripts/gather

.PHONY: run-image
run-image:
	-mkdir must-gather/
	oc config view --minify --raw > kubeconfig
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
	$(CONTAINER_ENGINE) build --platform linux/amd64 -t $(IMAGE_NAME_AND_VERSION):$(TAG) -f Dockerfile
