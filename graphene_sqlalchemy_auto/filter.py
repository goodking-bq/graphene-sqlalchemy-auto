from sqlalchemy import not_, or_


def filter_query(query, model, filters):
    """make query

    Arguments:
        query {query} -- sqlalchemyquery
        model {model} -- model
        filters {list} -- filter list,like [{key: a,val:a,op:aa}] or {key:val}

    Returns:
        query -- sqlalchemy query
    """
    if isinstance(filters, (dict,)):
        conditions = []
        conditions = construct_conditions(conditions, filters, model)
        query = query.filter(*conditions)
        return query
    for _filter in filters:
        conditions = []
        if isinstance(_filter, (list,)):
            for __filter in _filter:
                conditions = construct_conditions(conditions, __filter, model)
            condition = or_(*conditions)
            query = query.filter(condition)
        if isinstance(_filter, (dict,)):
            conditions = construct_conditions(conditions, _filter, model)
            query = query.filter(*conditions)
    return query


def construct_conditions(conditions, _filter, model):
    """
    """
    op = _filter.get("op")
    if not op:
        for column_name in _filter:
            v = _filter[column_name]
            c = getattr(model, column_name)
            conditions.append(c == v)
        return conditions
    column_name = _filter.get("key")
    v = _filter.get("val")
    c = getattr(model, column_name)
    if not c or not op or not v:
        pass
    if op == "==":
        conditions.append(c == v)
    if op == "!=":
        conditions.append(c != v)
    if op == "<=":
        conditions.append(c <= v)
    if op == ">=":
        conditions.append(c >= v)
    if op == ">":
        conditions.append(c > v)
    if op == "<":
        conditions.append(c < v)
    if op == "starts":
        conditions.append(c.ilike(v + "%"))
    if op == "ends":
        conditions.append(c.ilike("%" + v))
    if op == "contains":
        conditions.append(c.contains(v))
    if op == "in":
        conditions.append(c.in_(v))
    if op == "notin":
        conditions.append(not_(c.in_(v)))
    if op == "any":
        conditions.append(c.any(**v))  # v is like {"column_name","2"}
    return conditions
