#!/usr/bin/env python3

import sys
import subprocess
import re


def webfetch(url: str) -> dict:
    """
    Fetch content from a URL using curl and convert HTML to Markdown using pandoc.

    Args:
        url (str): URL starting with http:// or https://

    Returns:
        dict: Result information
    """

    if not re.match(r"^https?://", url):
        return {
            "success": False,
            "message": "Invalid URL. Please provide a URL starting with http:// or https://",
            "data": None
        }

    try:
        # Download HTML as bytes
        curl_result = subprocess.run(
            [
                "curl",
                "--silent",
                "-L",
                "-f",
                "--",
                url
            ],
            capture_output=True,
            text=False,   # wichtig: Bytes behalten
            shell=False
        )

        if curl_result.returncode != 0:
            return {
                "success": False,
                "message": f"Curl failed with exit code {curl_result.returncode}",
                "data": curl_result.stderr.decode("utf-8", errors="replace")
            }

        # HTML bytes -> pandoc
        pandoc_result = subprocess.run(
            [
                "pandoc",
                "-f",
                "html",
                "-t",
                "gfm"
            ],
            input=curl_result.stdout,
            capture_output=True,
            text=False,   # ebenfalls Bytes
            shell=False
        )

        if pandoc_result.returncode != 0:
            return {
                "success": False,
                "message": f"Pandoc failed with exit code {pandoc_result.returncode}",
                "data": pandoc_result.stderr.decode("utf-8", errors="replace")
            }

        return {
            "success": True,
            "message": "OK",
            "data": pandoc_result.stdout.decode(
                "utf-8",
                errors="replace"
            )
        }

    except FileNotFoundError as e:
        return {
            "success": False,
            "message": f"Required program not found: {e}",
            "data": None
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "data": None
        }


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print(
            "Error: Please provide exactly 1 argument.",
            file=sys.stderr
        )
        sys.exit(1)

    result = webfetch(sys.argv[1])

    if result["success"]:
        print(result["data"])
    else:
        print(
            f"Error: {result['message']}",
            file=sys.stderr
        )
        sys.exit(1)
