"""Base Entity component for wattbox."""
import logging
from typing import Any, Callable, Dict, Literal

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, DOMAIN_DATA, TOPIC_UPDATE

_LOGGER = logging.getLogger(__name__)


class WattBoxEntity(Entity):
    """WattBox Entity class."""

    _async_unsub_dispatcher_connect: Callable
    _attr_should_poll: Literal[False] = False

    def __init__(  # pylint: disable=unused-argument
        self, hass: HomeAssistant, name: str, *args
    ) -> None:
        self.hass = hass
        self._attr_extra_state_attributes: Dict[str, Any] = dict()
        self.wattbox_name: str = name
        self.topic: str = TOPIC_UPDATE.format(DOMAIN, self.wattbox_name)

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""

        @callback
        def update() -> None:
            """Update the state."""
            self.async_schedule_update_ha_state(True)

        self._async_unsub_dispatcher_connect = async_dispatcher_connect(
            self.hass, self.topic, update
        )

    async def async_will_remove_from_hass(self) -> None:
        """Disconnect dispatcher listener when removed."""
        if hasattr(self, "_async_unsub_dispatcher_connect"):
            self._async_unsub_dispatcher_connect()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this WattBox device."""
        wattbox_data = self.hass.data[DOMAIN_DATA][self.wattbox_name]
        host = wattbox_data["host"]

        # Build basic device info
        device_info = DeviceInfo(
            identifiers={(DOMAIN, self.wattbox_name)},
            name=self.wattbox_name,
            manufacturer="Snapav",
            model="WattBox",
        )

        # Try to get MAC address from ARP table
        try:
            from getmac import get_mac_address  # pylint: disable=import-outside-toplevel

            mac = get_mac_address(ip=host)
            if mac:
                # Add MAC address as a connection
                device_info["connections"] = {(dr.CONNECTION_NETWORK_MAC, mac)}
                _LOGGER.debug(
                    "Found MAC address %s for WattBox %s at %s",
                    mac,
                    self.wattbox_name,
                    host,
                )
            else:
                _LOGGER.debug(
                    "Could not find MAC address for WattBox %s at %s in ARP table",
                    self.wattbox_name,
                    host,
                )
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.debug(
                "Error getting MAC address for WattBox %s at %s: %s",
                self.wattbox_name,
                host,
                err,
            )

        return device_info
