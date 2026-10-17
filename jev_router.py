#!/usr/bin/env python3
"""
Ticket router — backing source for scenes 090 and 100 of the JEV video.

One support ticket, three typed questions, one round trip to Jev:

    team     (choice)  bộ phận nào nên xử lý
    refund   (noul)    khách có đang xin hoàn tiền không
    urgency  (score)   mức độ cấp bách, trên thang ba mức

Jev trả về quyết định kèm xác suất, không bao giờ trả về văn bản. Vậy nên
không có JSON nào phải parse, và cũng không có category nào bị bịa ra.

    export TYPESAFE_API_KEY=apikey_...
    python3 jev_router.py
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"

TICKET = (
    "Tôi bị trừ tiền hai lần cho gói tháng Chín. Vui lòng hoàn lại khoản "
    "thanh toán bị trùng. Mình đã gửi mail ba ngày trước mà chưa ai trả lời."
)

QUESTIONS = {
    "team": {
        "type": "choice",
        "instructions": "Bộ phận nào nên xử lý ticket này?",
        "criteria": {
            "billing": "Thanh toán, hóa đơn, hoàn tiền",
            "technical": "Lỗi, sự cố, tính năng không hoạt động",
            "account": "Đăng nhập, mật khẩu, thông tin tài khoản",
        },
    },
    "refund": {
        "type": "noul",
        "instructions": "Khách hàng có đang yêu cầu hoàn tiền không?",
        "criteria": {
            "true": "Khách hàng muốn được trả lại tiền.",
            "false": "Khách hàng không đề cập đến việc trả lại tiền.",
        },
    },
    "urgency": {
        "type": "score",
        "instructions": "Ticket này cấp bách đến mức nào?",
        "criteria": [
            "Không gấp, có thể xử lý trong tuần",
            "Bình thường, xử lý trong vòng hai ngày",
            "Cấp bách, cần xử lý ngay",
        ],
    },
}

# Ngưỡng này do mình tự đặt, dựa trên dữ liệu của mình — Jev không đặt nó hộ mình.
AUTO_ROUTE_MIN_CONFIDENCE = 0.75


def load_key():
    """Lấy API key từ environment, hoặc từ .env.local ở thư mục gốc của video.

    Key không bao giờ được viết vào file này — file này sẽ xuất hiện trên màn hình.
    """
    key = os.environ.get("TYPESAFE_API_KEY")
    if key:
        return key
    here = os.path.dirname(os.path.abspath(__file__))
    envfile = os.path.join(here, os.pardir, ".env.local")
    if os.path.exists(envfile):
        with open(envfile, encoding="utf-8") as f:
            for line in f:
                name, _, value = line.strip().partition("=")
                if name == "TYPESAFE_API_KEY" and value:
                    return value
    sys.exit("Chưa có TYPESAFE_API_KEY (environment hoặc .env.local)")


def ask(state, questions):
    key = load_key()
    body = json.dumps(
        {"model": MODEL, "state": state, "questions": questions}
    ).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req) as r:
            payload = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"{e.code} {e.reason}: {e.read().decode('utf-8', 'replace')[:400]}")
    return payload, (time.perf_counter() - started) * 1000


def main():
    res, ms = ask(TICKET, QUESTIONS)
    answers = res["answers"]
    usage = res["usage"]

    print(f"snapshot : {res['model']}")
    print(f"latency  : {ms:.0f} ms")
    print(f"cost     : ${usage.get('cost', 0):.6f}  ({usage['input_tokens']} input tokens)")
    print()

    team = answers["team"]
    print(f"team     : {team['choice']}  (confidence {team['confidence']:.2f})")
    for option, p in sorted(team["probabilities"].items(), key=lambda kv: -kv[1]):
        print(f"           {option:<10} {p:.3f}")

    print(f"refund   : {answers['refund']['noul']:.2f}")

    urgency = answers["urgency"]
    level = str(min(round(urgency["score"]), len(QUESTIONS["urgency"]["criteria"]) - 1))
    print(f"urgency  : {urgency['score']:.2f} — {urgency['legend'][level]}")
    print()

    # Quyết định cuối cùng nằm trong code của mình, không nằm trong model.
    if team["confidence"] >= AUTO_ROUTE_MIN_CONFIDENCE:
        print(f"→ tự động chuyển đến bộ phận {team['choice']}")
    else:
        print("→ không đủ chắc chắn, chuyển cho người thật xem lại")


if __name__ == "__main__":
    main()
