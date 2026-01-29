from dataclasses import fields as dc_fields

def orm_to_core(orm_obj, core_cls):
    core_field_names = {f.name for f in dc_fields(core_cls)}
    data = {k: getattr(orm_obj, k) for k in core_field_names if hasattr(orm_obj, k)}
    return core_cls(**data)

def core_to_orm(core_obj, orm_cls):
    orm_field_names = {c.name for c in orm_cls.__table__.columns}
    data = {k: getattr(core_obj, k) for k in orm_field_names if hasattr(core_obj, k)}
    return orm_cls(**data)
