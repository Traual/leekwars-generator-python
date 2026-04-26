import os
import datetime
from urllib import request as urllib_request

from . import log as Log
from .util import json_util as Json, util as Util


TAG = "Data"

fullmoon = []


def check_data(api: str) -> None:
    os.makedirs("data", exist_ok=True)

    print("Check api: " + api)
    print("Load weapons from API...")
    weapons = Json.parse_object(_get(api + "weapon/get-all", ""))["weapons"]
    Util.write_file(Json.to_json(weapons), "data/weapons.json")

    print("Load chips from API...")
    chips = Json.parse_object(_get(api + "chip/get-all", ""))["chips"]
    Util.write_file(Json.to_json(chips), "data/chips.json")

    print("Load summons from API...")
    summons = Json.parse_object(_get(api + "summon/get-templates", ""))["summon_templates"]
    Util.write_file(Json.to_json(summons), "data/summons.json")

    print("Load fullmoon from API...")
    f = Json.parse_array(_get(api + "fight/fullmoon", ""))
    for d in f:
        # Parse ISO date and convert to local date
        date_utc = datetime.datetime.fromisoformat(d).replace(tzinfo=datetime.timezone.utc)
        date_local = date_utc.astimezone().date()
        fullmoon.append(date_local)
    Util.write_file(Json.to_json(f), "data/fullmoon.json")

    print("Load components from API...")
    components = Json.parse_object(_get(api + "component/get-all/dfgdfgzegktyrtytm", ""))
    Util.write_file(Json.to_json(components), "data/components.json")


def _get(url: str, url_parameters: str):
    Log.i(TAG, "get " + url)
    try:
        req = urllib_request.Request(url, headers={"accept": "application/json"})
        with urllib_request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        import traceback
        traceback.print_exc()
    return None


def is_full_moon() -> bool:
    today = datetime.date.today()
    for d in fullmoon:
        if d == today:
            return True
    return False
