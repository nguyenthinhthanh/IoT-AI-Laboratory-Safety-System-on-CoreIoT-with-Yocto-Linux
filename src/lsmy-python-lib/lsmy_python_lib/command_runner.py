import time
import logging
import subprocess

log = logging.getLogger("command-runner")

def run_cmd(cmd: list[str], check: bool = True):
    """
    Run a system command with logging.

    :param cmd: Command as list of strings
    :param check: Raise exception on failure if True
    :return: True if command succeeds, False otherwise
    """
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

def run_cmd_with_retry(cmd: list[str], retries: int = 3, delay: float = 2.0,):
    """
    Run a command with retry mechanism.

    :param cmd: Command as list of strings
    :param retries: Number of retry attempts
    :param delay: Delay between retries (seconds)
    """
    for attempt in range(1, retries + 1):
        log.info(
            "Exec (attempt %d/%d): %s",
            attempt,
            retries,
            " ".join(cmd),
        )

        if run_cmd(cmd, check=False):
            return True

        if attempt < retries:
            log.warning("Retrying in %.1fs...", delay)
            time.sleep(delay)

    raise RuntimeError(f"Command failed after {retries} attempts: {' '.join(cmd)}")
