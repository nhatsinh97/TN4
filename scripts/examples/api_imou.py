async def async_api_devicePTZInfo(self, device_id: str) -> dict:  # pylint: disable=invalid-name
    """Get the current PTZ position information of the device. \
        (https://open.imoulife.com/book/en/http/device/operate/devicePTZInfo.html)."""
    # define the api endpoint
    api = "devicePTZInfo"
    # prepare the payload
    payload = {
        "deviceId": device_id,
        "channelId": "0",
    }
    # call the api
    return await self._async_call_api(api, payload)

async def async_get_image(self) -> Union[bytes, None]:
    """Get image snapshot."""
    if not await self._async_is_ready():
        return None
    _LOGGER.debug(
        "[%s] requested an image snapshot",
        self._device_name,
    )
    # request a snapshot and get the url
    data = await self.api_client.async_api_setDeviceSnapEnhanced(self._device_id)
    if "url" not in data:
        raise InvalidResponse(f"url not found in {data}")
    url = data["url"]
    # wait for the image to be available
    camera_wait_before_download = CAMERA_WAIT_BEFORE_DOWNLOAD
    if self._device_instance is not None:
        self._device_instance.get_camera_wait_before_download()
    await asyncio.sleep(camera_wait_before_download)
    # retrieve the image from the url
    session = self.api_client.get_session()
    if session is None:
        raise NotConnected()
    try:
        response = await session.request("GET", url, timeout=self.api_client.get_timeout())
        if response.status != 200:
            raise InvalidResponse(f"status code {response.status}")
        image = await response.read()
    except Exception as exception:
        raise InvalidResponse(f"unable to retrieve image from {url}: {exception}") from exception
    return image
