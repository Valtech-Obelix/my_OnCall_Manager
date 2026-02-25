import  requests
from    datetime                                            import datetime
from    typing                                              import Any

from    src.domain.exceptions                               import (  OpsGenieApiException
                                                                    , OpsGenieAuthException
                                                                    , OpsGenieNotFoundException
                                                                    , OpsGenieConnectionException
                                                                   )


class OpsGenieClient:
    """
    Ref: UC-004 v0.1
    - Kapselt REST-Aufrufe an OpsGenie
    - Keine Business-Logik
    """

    BASE_URL = "https://api.opsgenie.com/v2"

    def __init__(self, p_api_key: str):
        if not p_api_key:
            raise ValueError("OpsGenie API key is missing.")
        self._api_key = p_api_key

    def get_schedule_timeline(
        self,
        p_schedule_id: str,
        p_since: datetime | None = None
    ) -> dict[str, Any]:

        headers = {
            "Authorization": f"GenieKey {self._api_key}",
            "Content-Type": "application/json"
        }

        params = {}

        if p_since:
            # OpsGenie erwartet UTC ISO mit Z
            params["since"] = p_since.isoformat() + "Z"

        try:
            response = requests.get(
                f"{self.BASE_URL}/schedules/{p_schedule_id}/timeline",
                headers=headers,
                params=params,
                timeout=30
            )

        except requests.exceptions.ConnectionError as ex:
            raise OpsGenieConnectionException(str(ex))

        if response.status_code == 401:
            raise OpsGenieAuthException('Authentication failed')

        if response.status_code == 404:
            raise OpsGenieNotFoundException('Project not found')

        if response.status_code != 200:
            raise OpsGenieApiException(f'Unexpected API error: {response.status_code}')
        
        response.raise_for_status()

        return response.json()