FROM ubuntu:latest

# Installa bash e altri strumenti necessari
RUN apt-get update && apt-get install -y bash

# Impostiamo la directory di lavoro nel container
WORKDIR /code

# Manteniamo il container in esecuzione con bash
CMD ["bash"]