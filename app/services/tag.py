from app.models.tag import Tag
from app.schemas.tag import TagCreate
from app.database import SessionDep
from sqlmodel import select
from fastapi import HTTPException

def create_tag(tag: TagCreate, user_id: int, session: SessionDep) -> Tag:
    db_tag = Tag(name=tag.name, user_id=user_id)
    session.add(db_tag)
    session.commit()
    session.refresh(db_tag)
    return db_tag

def get_tags(session: SessionDep, user_id: int, offset: int = 0, limit: int = 100):
    tags = session.exec(
        select(Tag).where(Tag.user_id == user_id).offset(offset).limit(limit)
    ).all()
    return tags

def get_tag(tag_id: int, user_id: int, session: SessionDep) -> Tag:
    tag = session.exec(select(Tag).where(Tag.id == tag_id)).first()
    # 404 (not 403) for security reasons, so the tags existence isn't leaked.
    if not tag or tag.user_id != user_id:
        raise HTTPException(status_code=404, detail="tag not found")
    return tag

def get_files_by_tag(tag_id: int, user_id: int, session: SessionDep):
    tag = get_tag(tag_id, user_id, session)
    return tag.files

def delete_tag(tag_id: int, user_id: int, session: SessionDep):
    tag = get_tag(tag_id, user_id, session)
    # Deleting the tag also clears its rows in the file/tag link table, which
    # detaches it from every file it was on (the files themselves are kept).
    session.delete(tag)
    session.commit()
    return {"ok": True}
