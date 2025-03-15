## List of Guardrail Validators
The validators that we can use to guard LLM response can be found at: `https://hub.guardrailsai.com/`


## Running Locally
* Create a virtual environment
* Install the requirements in the requirements.txt file
* CD into the src folder
* Run `guardrails start --config config.py`
* The OpenAI compatible endpoint is available via Uvicorn at `http://127.0.0.1:8000`
* Running the validator locally, run the command `python client.py`

## Running on Docker
* Go to parent directory
* Run `docker build -f Dockerfile -t guardrails_server:1.0 .`
* 
