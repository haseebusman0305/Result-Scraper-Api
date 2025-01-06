from flask import Blueprint, request, jsonify, current_app
from .scraper import UAFScraper
from .parser import ResultParser
from functools import lru_cache
from config import Config
import re
import time

api = Blueprint("api", __name__)
scraper = UAFScraper()


def validate_reg_number(reg_number):
    pattern = r"^\d{4}-[a-zA-Z]+-\d{4}$"
    return bool(re.match(pattern, reg_number))


@lru_cache(maxsize=100)
def get_cached_result(reg_number):
    html_content = scraper.get_result_html(reg_number)
    return ResultParser.parse_html(html_content)


@api.route("/result", methods=["GET"])
def get_result():
    reg_number = request.args.get("reg_number")
    if not reg_number:
        return jsonify({"error": "Registration number is required"}), 400

    if not validate_reg_number(reg_number):
        return jsonify({"error": "Invalid registration number format"}), 400

    try:
        start_time = time.time()
        parsed_data = get_cached_result(reg_number)

        response = {
            "status": "success",
            "response_time": f"{(time.time() - start_time):.2f}s",
            "data": {
                "title": parsed_data["metadata"]["title"],
                "header_image": parsed_data["metadata"]["header_image"],
                "student_info": parsed_data["student_info"],
                "result_table": {
                    "headers": parsed_data["headers"],
                    "rows": parsed_data["results"],
                },
            },
        }

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": "Failed to fetch result", "details": str(e)}), 500
