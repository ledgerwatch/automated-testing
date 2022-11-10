default: automated-tests

# Runs 2x dev nodes of erigon (using dockerhub images), 
# builds automated-testing docker image and then uses it to run tests
automated-tests:
	./docker/run.sh
