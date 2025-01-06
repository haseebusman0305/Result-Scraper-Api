from bs4 import BeautifulSoup


class ResultParser:
    @staticmethod
    def parse_html(html_content):
        soup = BeautifulSoup(html_content, "html.parser")

        # Get metadata
        metadata = {
            "title": (
                soup.find("h3", {"align": "center"}).text.strip()
                if soup.find("h3", {"align": "center"})
                else ""
            ),
            "header_image": (
                soup.find("img", {"src": "lms-head.png"}).get("src")
                if soup.find("img", {"src": "lms-head.png"})
                else ""
            ),
        }

        # Get student info
        info_table = soup.find("table", {"style": lambda x: x and "width:50%" in x})
        student_info = {}
        if info_table:
            for row in info_table.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) == 2:
                    key = cols[0].text.strip()
                    value = cols[1].text.strip()
                    student_info[key] = value

        # Get results table headers
        results_table = soup.find_all("table")[1]
        headers = []
        if results_table:
            header_row = results_table.find("tr")
            if header_row:
                headers = [th.text.strip() for th in header_row.find_all("th")]

        # Get results
        results = []
        if results_table:
            rows = results_table.find_all("tr")[1:]  # Skip header row
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 12:
                    result = {
                        headers[0]: cols[0].text.strip(),
                        headers[1]: cols[1].text.strip(),
                        headers[2]: cols[2].text.strip(),
                        headers[3]: cols[3].text.strip(),
                        headers[4]: cols[4].text.strip(),
                        headers[5]: cols[5].text.strip(),
                        headers[6]: cols[6].text.strip(),
                        headers[7]: cols[7].text.strip(),
                        headers[8]: cols[8].text.strip(),
                        headers[9]: cols[9].text.strip(),
                        headers[10]: cols[10].text.strip(),
                        headers[11]: cols[11].text.strip(),
                    }
                    results.append(result)

        return {
            "metadata": metadata,
            "student_info": student_info,
            "headers": headers,
            "results": results,
        }
