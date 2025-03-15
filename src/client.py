import os
import time
import yaml

from guardrails import Guard, settings

def load_config(file_path='config.yaml'):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
config = load_config()

os.environ["OPENAI_API_BASE"] = config['api']['client']['openai_api_base']

settings.use_server = True

# /v1/guard_basic
start_time = time.time()
ban_list_guard = Guard(name="ban_list")
ban_list_guard_outcome = ban_list_guard.validate(
    llm_output='This is a test sentence that will not fail the guardrails validator'
)
end_time = time.time() - start_time
print(f"the time is {round(end_time, 2)} seconds")
print(ban_list_guard.name + " validation_passed is " + str(ban_list_guard_outcome.validation_passed))
print(ban_list_guard_outcome.validation_summaries[0].error_spans[0].reason if not ban_list_guard_outcome.validation_passed else None)