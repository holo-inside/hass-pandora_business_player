"""Configuration flow for the Pandora Business platform."""

import json
import logging
from typing import Any, Self

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import AbortFlow, FlowResult

from .const import (
    PANDORAREMOTE,
    CONF_ADVANCED_OPTIONS,
    DEFAULT_ENTITY_NAME,
    DOMAIN,
)
from .schema import DATA_SCHEMA
from .utils import host_valid
from .pandora_client import PandoraClient

_LOGGER = logging.getLogger(__name__)


class PandoraBusinessConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
    host: str | None = None

    def __init__(self):
        """Initiliase the configuration flow."""

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Pandora options callback."""
        return PandoraBusinessOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            self.host = user_input[CONF_HOST]
            self._name = user_input[CONF_NAME]
            self._username = user_input[CONF_USERNAME]
            self._password = user_input[CONF_PASSWORD]

            try:
                await self._async_validate_input(
                    self.host, self._username, self._password
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=self._name,
                    data={
                        CONF_HOST: self.host,
                        CONF_NAME: self._name,
                        CONF_USERNAME: self._username,
                        CONF_PASSWORD: self._password,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(DATA_SCHEMA),
            errors=errors,
        )

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle user-confirmation of discovered node."""
        context = self.context
        errors = {}
        name = context[CONF_NAME]
        self.host = context[CONF_HOST]
        title = DEFAULT_ENTITY_NAME

        placeholders = {
            CONF_NAME: name,
            CONF_HOST: self.host,
        }
        context["title_placeholders"] = placeholders
        if user_input is not None:
            try:
                await self._async_setuniqueid(self.host, self._username)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            else:
                user_input = {CONF_HOST: self.host, CONF_NAME: title}
                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="confirm",
            description_placeholders=placeholders,
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        """Add reconfigure step to allow to reconfigure a config entry."""
        errors = {}
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            self.host = user_input[CONF_HOST]
            errors = await self._async_validate_input(self.host, self._username, self._password)
            if not errors:
                return self.async_update_reload_and_abort(
                    entry, data_updates=user_input
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=entry.data[CONF_HOST]): str,
                }
            ),
            errors=errors,
        )

    def is_matching(self, other_flow: Self) -> bool:
        """Return True if other_flow is matching this flow."""
        return other_flow.host == self.host

    async def _async_setuniqueid(self, host, username, reconfigure=False):
        self._async_abort_entries_match({CONF_HOST: host})

        if not reconfigure:

            await self.async_set_unique_id(
                f"{username}@{host}"
            )
            self._abort_if_unique_id_configured()

    async def _async_validate_input(self, host, username, password):
        """Validate the user input allows us to connect."""
        try:
            if not host_valid(host):
                raise CannotConnect

            client = PandoraClient(host, username, password)
            if not await self.hass.async_add_executor_job(client.login):
                raise CannotConnect

            if not await self.hass.async_add_executor_job(client.get_stations):
                raise CannotConnect

            await self._async_setuniqueid(host, username)
        except Exception as ex:
            _LOGGER.error("Error connecting to Pandora Business: %s", ex)
            raise CannotConnect from ex


class PandoraBusinessOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options for Pandora Business."""

    def __init__(self, config_entry):
        """Initialize Pandora options flow."""
        _LOGGER.debug(
            "Config options flow initiated for: %s, %s, %s",
            config_entry.title,
            config_entry.data[CONF_HOST],
            config_entry.unique_id,
        )
        self._name = config_entry.title
        self._config_entry = config_entry
        self._remote = None

        self._advanced_options = config_entry.options.get(CONF_ADVANCED_OPTIONS, False)
        self._user_input = None

    async def async_step_init(
        self,
        user_input=None,  # pylint: disable=unused-argument
    ) -> FlowResult:
        """Set up the option flow."""
        if self._config_entry.entry_id not in self.hass.data[DOMAIN]:
            errmsg = (
                "Pandora device has not been available "
                f"since last Home Assistant restart: {self._config_entry.title}"
            )
            _LOGGER.error(errmsg)
            raise AbortFlow(errmsg)

        self._remote = self.hass.data[DOMAIN][self._config_entry.entry_id][PANDORAREMOTE]

        if self._remote.device_setup:
            return await self.async_step_user()

        return await self.async_step_retry()

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input:
            self._user_input = self._store_user_input(user_input)
            if self._advanced_options:
                return await self.async_step_advanced()

            advanced_input = self._fake_advanced_input()
            user_input = {**self._user_input, **advanced_input}
            return self.async_create_entry(title="", data=user_input)

        schema = self._create_options_schema()
        return self.async_show_form(
            step_id="user",
            description_placeholders={CONF_NAME: self._name},
            data_schema=vol.Schema(schema),
            errors=errors,
        )

    async def async_step_advanced(self, user_input=None) -> FlowResult:
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input:
            try:
                advanced_input = self._store_advanced_input(user_input)
                user_input = {**self._user_input, **advanced_input}
                return self.async_create_entry(title="", data=user_input)
            except json.decoder.JSONDecodeError:
                errors["base"] = "invalid_sources"
            except InvalidCommand:
                errors["base"] = "invalid_command"

        schema = self._create_advanced_options_schema()
        return self.async_show_form(
            step_id="advanced",
            description_placeholders={CONF_NAME: self._name},
            data_schema=vol.Schema(schema),
            errors=errors,
        )

    def _store_user_input(self, user_input):
        self._advanced_options = user_input.get(CONF_ADVANCED_OPTIONS)

        return user_input

    def _store_advanced_input(self, user_input):
        return user_input

    def _fake_advanced_input(self):
        advanced_input = {}
        return advanced_input

    async def async_step_retry(self, user_input=None):  # pylint: disable=unused-argument
        """Handle a failed connection."""
        errors = {"base": "cannot_connect"}

        return self.async_show_form(
            step_id="retry",
            data_schema=vol.Schema({}),
            errors=errors,
        )

    def _create_options_schema(self):
        return {
            vol.Optional(CONF_ADVANCED_OPTIONS, default=self._advanced_options): bool,
        }

    def _create_advanced_options_schema(self):
        return {
        }

class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidCommand(exceptions.HomeAssistantError):
    """Error to indicate an invalid command was used."""
