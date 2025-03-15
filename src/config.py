import yaml
import time
import logging
from builtins import str, int
from dotenv import load_dotenv
from typing import Callable, Dict, Optional, List

from guardrails import Guard
from fuzzysearch import find_near_matches
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
    ErrorSpan
)

def load_config(file_path='config.yaml'):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
config = load_config()

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@register_validator(name="guardrails/ban_list", data_type="string")
class CustomBanList(Validator):
    """Validates that output does not have banned words, using fuzzy search.

    **Key Properties**

    | Property                      | Description                       |
    | ----------------------------- | --------------------------------- |
    | Name for `format` attribute   | `guardrails/ban_list`             |
    | Supported data types          | `string`                          |
    | Programmatic fix              | Removes banned word.              |

    Args:
        banned_words (List[str]): A list of banned words to check for in output.
        max_l_dist (int): Maximum Levenshtein distance for fuzzy search. Default is 1.
        on_fail (str): A string that describes the behaviour of the function when there's a failure. Defaults to "noop"
    """  # noqa

    # If you don't have any init args, you can omit the __init__ method.
    def __init__(
            self,
            banned_words: str,
            max_l_dist: int = 0,
            on_fail: Optional[Callable] = "noop",
    ):

        super().__init__(
            banned_words=banned_words,
            max_l_dist=max_l_dist,
            on_fail=on_fail
        )

        self._banned_words = banned_words
        self._max_l_dist = max_l_dist

    def validate(self, llm_output: str, metadata: Optional[Dict]) -> ValidationResult:
        """Validates that output does not have banned words."""
        start_time = time.time()
        logger.info(f"(ban list validator guard) The input to ban_list is {llm_output}")
        spaceless_value = llm_output.replace(" ", "").lower()
        # list of tuples (character, index in original string)
        spaceless_index_map = []

        actual_index = 0
        for i in range(len(llm_output)):
            actual_index += 1
            spaceless_index_map.append((llm_output[i], actual_index))
        all_matches = []
        for banned_word in self._banned_words:
            spaceless_banned_word = banned_word.replace(" ", "").lower()
            matches = find_near_matches(spaceless_banned_word, spaceless_value, max_l_dist=self._max_l_dist)
            all_matches.extend(matches)

        if len(all_matches) > 0:
            error_spans = []
            fix_value = llm_output
            for match in all_matches:
                actual_start = spaceless_index_map[match.start][1]
                actual_end = spaceless_index_map[match.end - 1][1]
                triggering_text = llm_output[actual_start:actual_end]
                fix_value = fix_value.replace(triggering_text, "")
                error_spans.append(ErrorSpan(
                    start=actual_start,
                    end=actual_end,
                    reason=f"Found match with banned word '{match.matched}' in the triggering text '{triggering_text}'"
                ))
            logger.info(f"(ban list validator guard) The output to ban_list is fail, the time taken was {(time.time() - start_time):.3f} seconds.")
            return FailResult(
                error_message="Ban List: contains banned words",
                error_spans=error_spans,
                fix_value=fix_value
            )
        logger.info(f"(ban list validator guard) The output to ban_list is pass, the time taken was {(time.time() - start_time):.3f} seconds.")
        return PassResult()

# Specifying Guardrails Module
# Ban List Guardrails
CustomBanListModule = CustomBanList(
    banned_words=config["validator"]["ban_list"]["banned_words"],
    max_l_dist=config["validator"]["ban_list"]["max_l_dist"],
    on_fail=config["validator"]["ban_list"]["on_fail"]
)

# /v1/guard_basic - Profanity Free and Ban List Guardrails
guard_basic = Guard(name="ban_list").use(
    CustomBanListModule
)