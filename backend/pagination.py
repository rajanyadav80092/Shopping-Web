"""Offset aur cursor (keyset) pagination helpers.

Dono helpers kisi bhi SQLAlchemy Query ke saath chalte hain. Sorting hamesha
ek unique id column par hoti hai, taaki order deterministic rahe (bina ORDER BY
ke database kisi bhi order me rows de sakta hai, to pages me duplicate/gap aa jaate hain).

Cursor pagination yahan id par isliye chalti hai kyunki id unique hai aur
hamesha badhti hai. Agar kabhi kisi non-unique column (created_at, price) par
sort karna ho to cursor (value, id) ka jodi banana padega.
"""

DEFAULT_PER_PAGE = 20
MAX_PER_PAGE = 100
MAX_PAGE = 1_000_000
MAX_ID = 2**63 - 1  # SQLite/Postgres bigint se bada number bind karne par error aata hai


class PaginationError(ValueError):
    """page / per_page / cursor galat hai. View me ye 400 response ban jaata hai."""


def parse_int(raw, name, default, minimum=1, maximum=None, clamp=True):
    """Query-string ki value ko int me badalta hai.

    - value nahi aayi (None ya khali) -> default
    - int nahi hai ya minimum se chhoti hai -> PaginationError
    - maximum se badi hai -> clamp=True par maximum de deta hai, warna PaginationError
    """
    if raw is None or raw.strip() == "":
        return default
    try:
        value = int(raw)
    except ValueError:
        raise PaginationError(f"{name} must be an integer") from None
    if value < minimum:
        raise PaginationError(f"{name} must be >= {minimum}")
    if maximum is not None and value > maximum:
        if clamp:
            return maximum
        raise PaginationError(f"{name} must be <= {maximum}")
    return value


def offset_paginate(query, id_col, page, per_page, descending=True):
    """LIMIT/OFFSET pagination. Total count aur page numbers deta hai.

    Dhyan: har request par COUNT(*) chalta hai aur deep page par database
    OFFSET tak ki saari rows skip karta hai, isliye badi table par slow hota hai.
    Naye ya delete hue rows page ke beech me aaye to duplicate ya gap ho sakta hai.
    """
    order = id_col.desc() if descending else id_col.asc()
    total = query.order_by(None).count()
    rows = query.order_by(order).offset((page - 1) * per_page).limit(per_page).all()
    pages = max(1, -(-total // per_page))  # ceil division
    meta = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages,
        "has_next": page < pages,
        "has_prev": page > 1,
    }
    return rows, meta


def cursor_paginate(query, id_col, cursor, limit, descending=True):
    """Keyset pagination: "last dekhi hui id ke baad ki rows do".

    WHERE id < cursor (descending) ya id > cursor (ascending) index se seedha
    wahin pahunchta hai, to page kitna bhi deep ho speed same rehti hai, aur beech me
    insert/delete hone se duplicate ya gap nahi aata.

    limit + 1 rows mangwate hain taaki pata chale aage aur data hai ya nahi
    (extra COUNT query ki zaroorat nahi).
    """
    if cursor is not None:
        query = query.filter(id_col < cursor if descending else id_col > cursor)
    order = id_col.desc() if descending else id_col.asc()
    rows = query.order_by(order).limit(limit + 1).all()
    has_more = len(rows) > limit
    rows = rows[:limit]
    next_cursor = getattr(rows[-1], id_col.key) if has_more else None
    return rows, {"next_cursor": next_cursor, "has_more": has_more}