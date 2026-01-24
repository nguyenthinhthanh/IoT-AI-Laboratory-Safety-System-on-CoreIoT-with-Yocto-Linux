import time
import logging
import subprocess

log = logging.getLogger("provision-webserver-manager")

class ProvisionWebserverManager:
    """
    Manage WiFi provisioning services via systemd
    """

    FRONTEND_SERVICE = "provision-web-frontend.service"
    BACKEND_SERVICE  = "provision-web-backend.service"

    def __init__(self):
        log.info("ProvisionManager initialized")

    def _run(self, cmd: list[str], check: bool = True):
        log.debug("Running command: %s", " ".join(cmd))
        result = subprocess.run(cmd, check=check, capture_output=True, text=True,)

        if result.returncode != 0:
            log.error(
                "Command failed (%d): %s | stderr=%s",
                result.returncode,
                " ".join(cmd),
                result.stderr.strip(),
            )

        return result.returncode == 0

    def _run_with_retry(
        self,
        cmd: list[str],
        retries: int = 3,
        delay: float = 2.0,
    ):
        for attempt in range(1, retries + 1):
            log.info(
                "Exec (attempt %d/%d): %s",
                attempt,
                retries,
                " ".join(cmd),
            )

            if self._run(cmd, False):
                return True

            if attempt < retries:
                log.warning("Retrying in %.1fs...", delay)
                time.sleep(delay)

        raise RuntimeError(f"Command failed after {retries} attempts: {' '.join(cmd)}")

    def _is_active(self, service):
        result = subprocess.run(
            ["systemctl", "is-active", service],
            capture_output=True,
            text=True
        )
        return result.stdout.strip() == "active"


    def start(self):
        """
        Start provisioning UI + backend
        """
        log.info("========== STARTING PROVISIONING WEBSERVER ==========")
        self._run_with_retry(
            ["systemctl", "start", self.FRONTEND_SERVICE]
        )
        self._run_with_retry(
            ["systemctl", "start", self.BACKEND_SERVICE]
        )

        if not self.is_running():
            raise RuntimeError("Failed to start provisioning webserver services")
        log.info("Provisioning webserver successfully started")

    def stop(self):
        """
        Stop provisioning UI + backend
        """
        log.info("========== STOPPING PROVISIONING WEBSERVER ==========")
        self._run(
            ["systemctl", "stop", self.BACKEND_SERVICE],
            check=False,
        )
        self._run(
            ["systemctl", "stop", self.FRONTEND_SERVICE],
            check=False,
        )
        log.info("Provisioning webserver successfully stopped")

    def restart(self):
        log.info("========== RESTARTING PROVISIONING WEBSERVER ==========")
        self._run_with_retry(
            ["systemctl", "restart", self.FRONTEND_SERVICE]
        )
        self._run_with_retry(
            ["systemctl", "restart", self.BACKEND_SERVICE]
        )
        log.info("Provisioning webserver successfully restarted")

    def is_running(self):
        """
        Check if provisioning is active
        """
        return self._is_active(self.FRONTEND_SERVICE) and self._is_active(self.BACKEND_SERVICE)