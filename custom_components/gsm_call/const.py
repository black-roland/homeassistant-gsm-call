# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging
from enum import Enum

_LOGGER = logging.getLogger(__name__)

DOMAIN = "gsm_call"

CONF_AT_COMMAND = "at_command"
CONF_CALL_DURATION_SEC = "call_duration_sec"
CONF_HARDWARE = "hardware"

EVENT_GSM_CALL_COMPETED = f"{DOMAIN}_completed"
ATTR_PHONE_NUMBER = "phone_number"
ATTR_CALL_STATE = "call_state"


class CallState(str, Enum):
    TIMEDOUT = "timedout"
    DECLINED = "declined"
    ANSWERED = "answered"
