from homeassistant import config_entries
import voluptuous as vol
from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_NAME,
    CONF_NAME_REGEXP,
    CONF_SKIP_REGEXP,
    CONF_SCAN_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_USER,
    DEFAULT_PASSWORD,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
)

class WattBoxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WattBox."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Validate input here if needed
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)
            except Exception:
                errors["base"] = "unknown"

        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
            vol.Optional(CONF_USERNAME, default=DEFAULT_USER): str,
            vol.Optional(CONF_PASSWORD, default=DEFAULT_PASSWORD): str,
            vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            vol.Optional(CONF_NAME_REGEXP): str,
            vol.Optional(CONF_SKIP_REGEXP): str,
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(cv.time_period, cv.positive_timedelta),
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)