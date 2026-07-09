from datetime import date, datetime
import re

def parse_date(raw: str | None) -> date | None:
    if not raw:
        return None
    raw = raw.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def parse_amount(raw: str | None) -> tuple[int | None, int | None]:
    """"$1,001 - $15,000" -> (1001, 15000). Single values -> (v, v). Unknown -> (None, None)."""
    if not raw:
        return None, None
    nums = [int(n.replace(",", "")) for n in re.findall(r"[\d,]+", raw)]
    if not nums:
        return None, None
    if len(nums) == 1:
        return nums[0], nums[0]
    return min(nums), max(nums)