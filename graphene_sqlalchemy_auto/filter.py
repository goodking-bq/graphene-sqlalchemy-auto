from sqlalchemy import not_, or_


def filter_query(query, model, filters):
    """make query

    Arguments:
        query {query} -- sqlalchemy query
        model {model} -- model
        filters {list} -- filter list,like [{key: a,val:a,op:aa}]

    Returns:
        query -- sqlalchemy query
    examples:
        filters: {"column":id,"op":"==","val":1}
        filters: {"column1":1,"column1":2}
        filters: [{"column":id,"op":"==","val":1},{"column2":id,"op":"==","val":1}]
    """
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
    c = getattr(model, _filter.get("key"))
    v = _filter.get("val")
    op = _filter.get("op")
    if not op:  # if not op?,default  is `==` like {"column1":1,"column2":2}
        for key in _filter:
            conditions.append(key == _filter[key])
        return conditions
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
    return conditions
