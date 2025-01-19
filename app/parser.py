from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class ResultParser:
    @staticmethod
    def parse_html(html_content):
        """Parse the HTML content and extract result data"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Get metadata
            metadata = {
                "title": soup.find("h3", {"align": "center"}).text.strip(),
                "header_image": "lms-head.png"  # This is hardcoded in the HTML
            }

            # Get student info
            student_info = {}
            info_table = soup.find("table", {"class": "table tab-content", "style": True})
            if info_table:
                rows = info_table.find_all("tr")
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) == 2:
                        key = cols[0].text.strip().rstrip("#:").lower().replace(" ", "_")
                        value = cols[1].text.strip()
                        student_info[key] = value

            # Get result table headers
            headers = []
            result_table = soup.find_all("table", {"class": "table tab-content"})[-1]
            header_row = result_table.find("tr")
            for th in header_row.find_all("th"):
                headers.append(th.text.strip().lower().replace(" ", "_"))

            # Get results
            results = []
            for row in result_table.find_all("tr")[1:]:  # Skip header row
                cols = row.find_all(["td"])
                if len(cols) == len(headers):
                    result = {}
                    for i, col in enumerate(cols):
                        result[headers[i]] = col.text.strip()
                    results.append(result)

            return {
                "metadata": metadata,
                "student_info": student_info,
                "headers": headers,
                "results": results
            }

        except Exception as e:
            logger.error(f"Error parsing HTML content: {str(e)}")
            raise ValueError("Failed to parse result HTML") from e
