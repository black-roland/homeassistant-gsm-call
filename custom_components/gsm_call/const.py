# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging
from enum import Enum

_LOGGER = logging.getLogger(__name__)

DOMAIN = "gsm_call"

CONF_AT_COMMAND = "at_command"
CONF_DIAL_TIMEOUT_SEC = "dial_timeout_sec"
CONF_CALL_DURATION_SEC = "call_duration_sec"
CONF_HARDWARE = "hardware"

EVENT_GSM_CALL_ENDED = f"{DOMAIN}_ended"
ATTR_PHONE_NUMBER = "phone_number"
ATTR_REASON = "reason"


class EndedReason(str, Enum):
    NOT_ANSWERED = "not_answered"
    DECLINED = "declined"
    ANSWERED = "answered"
