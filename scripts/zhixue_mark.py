import io
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests
from PIL import Image


ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = ROOT / "zhixue_mark.config.json"
DEFAULT_OUT_DIR = Path.cwd() / "zhixue_work"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def load_config():
    config_path = os.environ.get("ZHIXUE_MARK_CONFIG")
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(
            "missing config file; create zhixue_mark.config.json from "
            "zhixue_mark.config.example.json or set ZHIXUE_MARK_CONFIG"
        )
    config = json.loads(path.read_text(encoding="utf-8"))
    required = ["markingPaperId", "topicNumStr", "referer", "cookie"]
    missing = [key for key in required if not config.get(key)]
    if missing:
        raise ValueError(f"missing required config keys: {', '.join(missing)}")
    return config, path


CONFIG, CONFIG_PATH = load_config()
OUT_DIR = Path(CONFIG.get("outDir") or DEFAULT_OUT_DIR).resolve()
OUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_PATH = OUT_DIR / "current.json"
EVENT_LOG_PATH = OUT_DIR / "events.jsonl"
PENDING_REVIEW_PATH = OUT_DIR / "pending_regrade.jsonl"
DEFAULT_BLANK_THRESHOLD = float(CONFIG.get("blankThreshold", 0.01))
DEFAULT_BLANK_AUTO_THRESHOLD = float(CONFIG.get("blankAutoThreshold", DEFAULT_BLANK_THRESHOLD))
DEFAULT_BLANK_REVIEW_THRESHOLD = float(
    CONFIG.get("blankReviewThreshold", max(DEFAULT_BLANK_AUTO_THRESHOLD * 1.5, 0.015))
)
DEFAULT_ANSWER_AREA_START = float(CONFIG.get("answerAreaStartFraction", 0.18))
DEFAULT_ANSWER_AREA_AUTO_THRESHOLD = float(CONFIG.get("answerAreaAutoThreshold", 0.004))
DEFAULT_ANSWER_AREA_REVIEW_THRESHOLD = float(CONFIG.get("answerAreaReviewThreshold", 0.008))


def append_event(kind, payload):
    record = {
        "ts": utc_now(),
        "kind": kind,
        "payload": payload,
    }
    with EVENT_LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_session():
    session = requests.Session()
    headers = {
        "Cookie": CONFIG["cookie"],
        "User-Agent": "Mozilla/5.0",
        "Referer": CONFIG["referer"],
        "Origin": "https://www.zhixue.com",
    }
    token = CONFIG.get("token")
    if token:
        headers["token"] = token
    session.headers.update(headers)
    return session


def response_debug_text(response):
    text = response.text.strip()
    if not text:
        return "<empty response>"
    return text[:1000]


def fetch_current(session, retries=6, delay=1.0):
    last_payload = None
    last_debug = None
    for attempt in range(retries):
        response = session.post(
            "https://pt-ali-bj.zhixue.com/marking/marking/personal/scanrecorddetail/",
            data={
                "markingPaperId": CONFIG["markingPaperId"],
                "isSpecify": "false",
                "topicNumStr": CONFIG["topicNumStr"],
                "isArbitration": "false",
                "isContinueMarkButton": "false",
                "withOutPreLoad": "true",
            },
            timeout=120,
        )
        response.raise_for_status()
        try:
            payload = response.json()
        except requests.exceptions.JSONDecodeError as exc:
            last_debug = response_debug_text(response)
            if attempt < retries - 1:
                time.sleep(delay)
                continue
            raise RuntimeError(
                "scanrecorddetail did not return JSON; this usually means the "
                "cookie/referer is expired or points at a different task. "
                f"response excerpt: {last_debug}"
            ) from exc

        last_payload = payload
        topic_info = payload.get("data", {}).get("topicInfo")
        detail = (topic_info or {}).get("detail")
        image_ids = detail.get("topicImageIds") if detail else None
        if topic_info and detail and image_ids:
            return topic_info
        last_debug = json.dumps(payload, ensure_ascii=False)
        if attempt < retries - 1:
            time.sleep(delay)

    raise RuntimeError(
        "scanrecorddetail returned no usable topicInfo: "
        + (last_debug or json.dumps(last_payload, ensure_ascii=False))
    )


def download_image(session, url):
    response = session.get(url, timeout=120)
    response.raise_for_status()
    return Image.open(io.BytesIO(response.content))


def dark_ratio(image):
    gray = image.convert("L")
    arr = np.array(gray)
    return float((arr < 200).mean())


def answer_area_dark_ratio(image, start_fraction=DEFAULT_ANSWER_AREA_START):
    gray = image.convert("L")
    arr = np.array(gray)
    start_row = max(0, min(arr.shape[0], int(arr.shape[0] * start_fraction)))
    crop = arr[start_row:, :]
    if crop.size == 0:
        return dark_ratio(image)
    return float((crop < 200).mean())


def collect_image_paths(path):
    target = Path(path).resolve()
    if target.is_file():
        return [target]
    if not target.exists():
        raise FileNotFoundError(f"path does not exist: {target}")
    paths = []
    for item in sorted(target.rglob("*")):
        if item.is_file() and item.suffix.lower() in IMAGE_SUFFIXES:
            paths.append(item)
    if not paths:
        raise FileNotFoundError(f"no image files found under: {target}")
    return paths


def calc_blank_threshold_stats(paths):
    ratios = []
    for path in paths:
        with Image.open(path) as image:
            ratios.append(dark_ratio(image))
    arr = np.array(ratios, dtype=float)
    stats = {
        "count": int(arr.size),
        "min": float(arr.min()),
        "p50": float(np.quantile(arr, 0.50)),
        "p90": float(np.quantile(arr, 0.90)),
        "p95": float(np.quantile(arr, 0.95)),
        "p99": float(np.quantile(arr, 0.99)),
        "max": float(arr.max()),
        "mean": float(arr.mean()),
    }
    strict_threshold = stats["p90"]
    recommended_threshold = min(stats["p95"], stats["max"])
    return stats, strict_threshold, recommended_threshold


def save_current(info, image):
    user_code = info["detail"]["userCode"]
    image_path = OUT_DIR / f"current_{user_code}.png"
    image.save(image_path)
    full_dark_ratio = dark_ratio(image)
    answer_dark_ratio = answer_area_dark_ratio(image)
    data = {
        "userCode": user_code,
        "itemId": info["item"]["id"],
        "imageUrl": info["detail"]["topicImageIds"][0],
        "imagePath": str(image_path),
        "darkRatio": full_dark_ratio,
        "answerAreaDarkRatio": answer_dark_ratio,
        "markingPaperId": CONFIG["markingPaperId"],
        "topicNumStr": CONFIG["topicNumStr"],
        "savedAt": utc_now(),
    }
    CACHE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    append_event(
        "save_current",
        {"userCode": user_code, "darkRatio": data["darkRatio"], "answerAreaDarkRatio": data["answerAreaDarkRatio"]},
    )
    return data


def commit_score(session, item_id, score, mark_content="[]"):
    response = session.post(
        "https://pt-ali-bj.zhixue.com/marking/marking/commitTopic/",
        data={
            "markingPaperId": CONFIG["markingPaperId"],
            "id": item_id,
            "markingScores": "{'" + CONFIG["topicNumStr"] + "':" + str(score) + "}",
            "isBack": "false",
            "keep": "false",
            "superiority": "normal0",
            "markContent": mark_content,
            "isArbitration": "false",
            "exceptionType": "0",
            "preScores": "",
        },
        timeout=120,
    )
    response.raise_for_status()
    try:
        payload = response.json()
    except requests.exceptions.JSONDecodeError as exc:
        raise RuntimeError(
            "commitTopic did not return JSON; response excerpt: "
            + response_debug_text(response)
        ) from exc
    return payload


def search_marked(session, page_index=0, score="", superiority=""):
    response = session.post(
        "https://pt-ali-bj.zhixue.com/marking/marking/personal/searchMarked/",
        data={
            "markingPaperId": CONFIG["markingPaperId"],
            "topicSorts": '["14"]',
            "topicNumStr": CONFIG["topicNumStr"],
            "score": score,
            "pageIndex": str(page_index),
            "isArbitration": "false",
            "superiority": superiority,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


def find_marked_trace_by_user_code(session, user_code, max_pages=80):
    for page_index in range(max_pages):
        payload = search_marked(session, page_index=page_index)
        for item in payload.get("pageList", []):
            if item.get("userCode") == user_code:
                return item
        page_info = payload.get("pageInfo") or {}
        total_page = int(page_info.get("totalPage") or 0)
        if total_page and page_index + 1 >= total_page:
            break
    return None


def load_marked(session, trace_id):
    response = session.post(
        "https://pt-ali-bj.zhixue.com/marking/marking/personal/loadMarked/",
        data={
            "markingPaperId": CONFIG["markingPaperId"],
            "id": trace_id,
            "isArbitration": "false",
            "topicNumStr": CONFIG["topicNumStr"],
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


def classify_blank_ratio(
    full_ratio,
    answer_ratio,
    auto_threshold=DEFAULT_BLANK_AUTO_THRESHOLD,
    review_threshold=DEFAULT_BLANK_REVIEW_THRESHOLD,
    answer_auto_threshold=DEFAULT_ANSWER_AREA_AUTO_THRESHOLD,
    answer_review_threshold=DEFAULT_ANSWER_AREA_REVIEW_THRESHOLD,
):
    if answer_ratio <= answer_auto_threshold and full_ratio <= auto_threshold * 2:
        return "auto_blank"
    if answer_ratio <= answer_review_threshold or full_ratio <= review_threshold:
        return "review_blank_zone"
    return "non_blank"


def command_current():
    session = build_session()
    info = fetch_current(session)
    image = download_image(session, info["detail"]["topicImageIds"][0])
    data = save_current(info, image)
    data["blankClass"] = classify_blank_ratio(data["darkRatio"], data["answerAreaDarkRatio"])
    print(json.dumps(data, ensure_ascii=False, indent=2))


def command_commit(score):
    session = build_session()
    data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    result = commit_score(session, data["itemId"], score)
    append_event("commit", {"userCode": data["userCode"], "score": score, "result": result})
    print(
        json.dumps(
            {"committed": score, "userCode": data["userCode"], "result": result},
            ensure_ascii=False,
            indent=2,
        )
    )


def command_recommit(item_id, score, user_code=None):
    session = build_session()
    result = commit_score(session, item_id, score)
    payload = {"itemId": item_id, "score": score, "result": result}
    if user_code:
        payload["userCode"] = user_code
    append_event("recommit", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def command_grade(score, threshold=DEFAULT_BLANK_THRESHOLD, max_count=200):
    session = build_session()
    data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    commit_result = commit_score(session, data["itemId"], score)
    append_event("commit", {"userCode": data["userCode"], "score": score, "result": commit_result})
    skipped = []
    for _ in range(max_count):
        info = fetch_current(session)
        image = download_image(session, info["detail"]["topicImageIds"][0])
        next_data = save_current(info, image)
        if classify_blank_ratio(next_data["darkRatio"], next_data["answerAreaDarkRatio"]) == "non_blank":
            print(
                json.dumps(
                    {
                        "committed": score,
                        "committedUserCode": data["userCode"],
                        "commitResult": commit_result,
                        "stoppedOn": next_data,
                        "skippedCount": len(skipped),
                        "skipped": skipped,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return
        blank_result = commit_score(session, next_data["itemId"], 0)
        append_event(
            "auto_blank_commit",
            {
                "userCode": next_data["userCode"],
                "score": 0,
                "darkRatio": next_data["darkRatio"],
                "result": blank_result,
            },
        )
        skipped.append({"userCode": next_data["userCode"], "darkRatio": next_data["darkRatio"]})

    print(
        json.dumps(
            {
                "committed": score,
                "committedUserCode": data["userCode"],
                "commitResult": commit_result,
                "stopped": "max_count",
                "skippedCount": len(skipped),
                "skipped": skipped,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def command_skip_blanks(threshold=DEFAULT_BLANK_THRESHOLD, max_count=200):
    session = build_session()
    skipped = []
    for _ in range(max_count):
        info = fetch_current(session)
        image = download_image(session, info["detail"]["topicImageIds"][0])
        data = save_current(info, image)
        if classify_blank_ratio(data["darkRatio"], data["answerAreaDarkRatio"]) == "non_blank":
            print(
                json.dumps(
                    {"stoppedOn": data, "skippedCount": len(skipped), "skipped": skipped},
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return
        result = commit_score(session, data["itemId"], 0)
        append_event(
            "auto_blank_commit",
            {
                "userCode": data["userCode"],
                "score": 0,
                "darkRatio": data["darkRatio"],
                "result": result,
            },
        )
        skipped.append({"userCode": data["userCode"], "darkRatio": data["darkRatio"]})
    print(json.dumps({"stopped": "max_count", "skippedCount": len(skipped), "skipped": skipped}, ensure_ascii=False, indent=2))


def command_calibrate_blanks(path):
    paths = collect_image_paths(path)
    stats, strict_threshold, recommended_threshold = calc_blank_threshold_stats(paths)
    print(
        json.dumps(
            {
                "source": str(Path(path).resolve()),
                "stats": stats,
                "strictThreshold": strict_threshold,
                "recommendedThreshold": recommended_threshold,
                "rule": (
                    "Calibrate from confirmed blank papers. Use auto_blank only "
                    "below the recommended threshold and review anything above it."
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def command_status():
    payload = {
        "configPath": str(CONFIG_PATH),
        "outDir": str(OUT_DIR),
        "cachePath": str(CACHE_PATH),
        "eventLogPath": str(EVENT_LOG_PATH),
        "markingPaperId": CONFIG["markingPaperId"],
        "topicNumStr": CONFIG["topicNumStr"],
        "blankThreshold": DEFAULT_BLANK_THRESHOLD,
        "blankAutoThreshold": DEFAULT_BLANK_AUTO_THRESHOLD,
        "blankReviewThreshold": DEFAULT_BLANK_REVIEW_THRESHOLD,
        "answerAreaStartFraction": DEFAULT_ANSWER_AREA_START,
        "answerAreaAutoThreshold": DEFAULT_ANSWER_AREA_AUTO_THRESHOLD,
        "answerAreaReviewThreshold": DEFAULT_ANSWER_AREA_REVIEW_THRESHOLD,
        "hasCache": CACHE_PATH.exists(),
    }
    if CACHE_PATH.exists():
        payload["current"] = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def append_pending_regrade(payload):
    with PENDING_REVIEW_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def command_batch_zero(count, full_threshold=None, answer_threshold=None):
    session = build_session()
    processed = []
    for _ in range(count):
        info = fetch_current(session)
        image = download_image(session, info["detail"]["topicImageIds"][0])
        data = save_current(info, image)
        result = commit_score(session, data["itemId"], 0)
        append_event("commit", {"userCode": data["userCode"], "score": 0, "result": result})
        pending_payload = {
            "userCode": data["userCode"],
            "itemId": data["itemId"],
            "imagePath": data["imagePath"],
            "darkRatio": data["darkRatio"],
            "answerAreaDarkRatio": data["answerAreaDarkRatio"],
            "markingPaperId": data["markingPaperId"],
            "topicNumStr": data["topicNumStr"],
        }
        if full_threshold is not None:
            pending_payload["fullThreshold"] = full_threshold
        if answer_threshold is not None:
            pending_payload["answerThreshold"] = answer_threshold
        append_pending_regrade(pending_payload)
        processed.append(
            {
                "userCode": data["userCode"],
                "imagePath": data["imagePath"],
                "darkRatio": data["darkRatio"],
                "answerAreaDarkRatio": data["answerAreaDarkRatio"],
            }
        )
    print(json.dumps({"count": len(processed), "processed": processed}, ensure_ascii=False, indent=2))


def command_recommit_user(user_code, score):
    session = build_session()
    trace = find_marked_trace_by_user_code(session, user_code)
    if not trace:
        raise RuntimeError(f"marked trace not found for userCode={user_code}")
    detail = load_marked(session, trace["id"])
    item_id = detail["data"]["topicInfo"]["item"]["id"]
    result = commit_score(session, item_id, score)
    payload = {
        "userCode": user_code,
        "traceId": trace["id"],
        "itemId": item_id,
        "score": score,
        "result": result,
    }
    append_event("recommit_user", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main():
    if len(sys.argv) < 2:
        print(
            "usage: zhixue_mark.py current|commit SCORE|recommit ITEM_ID SCORE [USER_CODE]|recommit-user USER_CODE SCORE|"
            "batch-zero COUNT|grade SCORE [THRESHOLD]|skip-blanks [THRESHOLD]|calibrate-blanks PATH|status"
        )
        raise SystemExit(2)

    cmd = sys.argv[1]
    if cmd == "current":
        command_current()
        return
    if cmd == "commit":
        command_commit(int(sys.argv[2]))
        return
    if cmd == "recommit":
        user_code = sys.argv[4] if len(sys.argv) > 4 else None
        command_recommit(sys.argv[2], int(sys.argv[3]), user_code=user_code)
        return
    if cmd == "recommit-user":
        command_recommit_user(sys.argv[2], int(sys.argv[3]))
        return
    if cmd == "batch-zero":
        command_batch_zero(int(sys.argv[2]))
        return
    if cmd == "grade":
        threshold = float(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_BLANK_THRESHOLD
        command_grade(int(sys.argv[2]), threshold=threshold)
        return
    if cmd == "skip-blanks":
        threshold = float(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_BLANK_THRESHOLD
        command_skip_blanks(threshold=threshold)
        return
    if cmd == "calibrate-blanks":
        command_calibrate_blanks(sys.argv[2])
        return
    if cmd == "status":
        command_status()
        return
    raise SystemExit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
