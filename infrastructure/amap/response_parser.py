import json

from typing import Any


class AmapResponseParser:

    @staticmethod
    def parse(result: Any):

        if not result:
            return None

        if isinstance(result, dict):
            return result

        if isinstance(result, str):

            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return result

        if isinstance(result, list):

            for item in result:

                if not isinstance(item, dict):
                    continue

                if item.get('type') != 'text':
                    continue

                text = item.get('text')

                if not text:
                    continue

                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return text

        return result
