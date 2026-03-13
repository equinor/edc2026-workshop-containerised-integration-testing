from threading import Thread, Event
from typing import Optional, Any

from docker.errors import APIError
from loguru import logger
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import WaitStrategy


class LogDockerContainer(DockerContainer):
    def __init__(
        self,
        image: str = "",
        docker_client_kw: Optional[dict[str, Any]] = None,
        _wait_strategy: Optional[WaitStrategy] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            image=image,
            docker_client_kw=docker_client_kw,
            _wait_strategy=_wait_strategy,
            **kwargs,
        )
        self._stop_logs: Event = Event()
        self._logging_thread: Optional[Thread] = None

    def start(self) -> "LogDockerContainer":
        super().start()

        self._stop_logs.clear()
        self._logging_thread = Thread(
            target=self._stream_logs,
            name=f"{self._name}-logs",
            daemon=True,
        )
        self._logging_thread.start()
        return self

    def stop(self, force: bool = False, delete_volume: bool = True) -> None:
        self._stop_logs.set()
        if self._logging_thread and self._logging_thread.is_alive():
            self._logging_thread.join(timeout=2)

        super().stop(force=True, delete_volume=delete_volume)

    def _stream_logs(self) -> None:
        container = self.get_wrapped_container()
        if not container:
            return

        try:
            for line in container.logs(
                stream=True,
                follow=True,
                stdout=True,
                stderr=True,
                tail=0,
            ):
                if self._stop_logs.is_set():
                    break
                logger.info(f"{self._name}: {line.decode(errors='replace').rstrip()}")
        except APIError as e:
            logger.debug(f"{self._name}: log stream ended: {e}")
        except Exception as e:
            logger.debug(f"{self._name}: log stream crashed: {e}")
