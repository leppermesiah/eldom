"""Sample API Client."""
import asyncio
import logging
import socket

import aiohttp
import async_timeout

TIMEOUT = 10


_LOGGER: logging.Logger = logging.getLogger(__package__)

head = {"Content-type": "application/json; charset=UTF-8"}
URL = "iot.myeldom.com/api/"


class EldomApiClient:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str = None,
        password: str = None,
        token: str = None,
        uuid: str = None,
        deviceId: str = None,
    ) -> None:
        self._username = username
        self._password = password
        self._session = session
        self._token = token
        self._uuid = uuid
        self._deviceId = deviceId

    async def async_get_token(self) -> dict:
        """Get data from the API."""
        url = f"https://{URL}authenticate"
        return await self.api_wrapper(
            "post",
            url,
            data={
                "password": f"{self._password}",
                "rememberMe": True,
                "username": f"{self._username}",
            },
            headers=head,
        )

    async def async_get_devices(self) -> dict:
        """Get devices from the API"""
        url = f"https://{URL}device-list?page=1&size=10"
        headers = head
        headers["Authorization"] = f"Bearer {self._token}"
        headers["ionic-idd"] = "0"
        return await self.api_wrapper("get", url, headers=headers)

    async def async_get_status(self) -> dict:
        """Get the status of the device"""
        url = f"https://{URL}direct-req"
        headers = head
        headers["Authorization"] = f"Bearer {self._token}"
        headers["ionic-idd"] = self._uuid
        return await self.api_wrapper(
            "post",
            url,
            data={
                "CID": "1",
                "CRC": "00000000",
                "ID": self._deviceId,
                "Req": "GetStatus",
            },
            headers=headers,
        )

    async def async_get_parameters(self) -> dict:
        """Get the status of the device"""
        url = f"https://{URL}direct-req"
        headers = head
        headers["Authorization"] = f"Bearer {self._token}"
        headers["ionic-idd"] = self._uuid
        return await self.api_wrapper(
            "post",
            url,
            data={
                "CID": "1",
                "CRC": "00000000",
                "ID": self._deviceId,
                "Req": "GetParams",
            },
            headers=headers,
        )

    async def async_turn_on_or_off(self, value: str) -> dict:
        """Get the status of the device"""
        url = f"https://{URL}direct-req"
        headers = head
        headers["Authorization"] = f"Bearer {self._token}"
        headers["ionic-idd"] = self._uuid
        return await self.api_wrapper(
            "post",
            url,
            data={
                "CID": "1",
                "CRC": "00000000",
                "ID": self._deviceId,
                "Req": value,
            },
            headers=headers,
        )

    async def async_set_parameter(self, value: dict) -> dict:
        """Set a parameter"""
        url = f"https://{URL}direct-req"
        headers = head
        headers["Authorization"] = f"Bearer {self._token}"
        headers["ionic-idd"] = self._uuid
        return await self.api_wrapper(
            "post",
            url,
            data=value,
            headers=headers,
        )

    async def api_wrapper(
        self, method: str, url: str, data: dict = {}, headers: dict = {}
    ) -> dict:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(TIMEOUT, loop=asyncio.get_event_loop()):
                if method == "get":
                    response = await self._session.get(url, headers=headers, ssl=False)
                    _LOGGER.info(await response.json())
                    return await response.json()

                elif method == "put":
                    await self._session.put(url, headers=headers, json=data, ssl=False)

                elif method == "patch":
                    await self._session.patch(
                        url, headers=headers, json=data, ssl=False
                    )

                elif method == "post":
                    response = await self._session.post(
                        url, headers=headers, json=data, ssl=False
                    )
                    return await response.json()

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)
