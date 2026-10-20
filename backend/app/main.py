from datetime import date
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from .db import Base, engine, get_db
from . import models as m, schemas as s
from .security import hash_password, verify_password, create_token, current_user
from .config import settings

app = FastAPI(title="BetterDays API", version="0.1.0", description="Mobile MVP API")
origins = [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins if origins != ["*"] else ["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        if db.scalar(select(m.Challenge.id).limit(1)) is None:
            db.add_all([
                m.Challenge(title="Move for 20 minutes", description="Walk, stretch, dance or work out.", duration_days=7),
                m.Challenge(title="Mindful hydration", description="Build a water routine that works for you.", duration_days=5),
                m.Challenge(title="Cook one meal at home", description="Try a simple homemade meal.", duration_days=7),
            ])
            db.commit()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/register", response_model=s.TokenOut, status_code=201)
def register(payload: s.UserCreate, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.scalar(select(m.User).where(m.User.email == email)):
        raise HTTPException(409, "Email is already registered")
    user = m.User(name=payload.name.strip(), email=email, password_hash=hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    return {"access_token": create_token(user.id), "user": user}

@app.post("/auth/login", response_model=s.TokenOut)
def login(payload: s.UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(select(m.User).where(m.User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Email or password is incorrect")
    return {"access_token": create_token(user.id), "user": user}

@app.get("/me", response_model=s.UserOut)
def me(user: m.User = Depends(current_user)):
    return user

@app.patch("/me", response_model=s.UserOut)
def update_me(payload: s.ProfileUpdate, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    user.name = payload.name.strip(); user.bio = payload.bio.strip()
    db.commit(); db.refresh(user); return user

@app.get("/recipes", response_model=list[s.RecipeOut])
def recipes(q: str | None = None, category: str | None = None, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    query = select(m.Recipe).where((m.Recipe.is_public == True) | (m.Recipe.user_id == user.id)).order_by(m.Recipe.created_at.desc())
    if category: query = query.where(m.Recipe.category == category)
    if q: query = query.where(m.Recipe.title.ilike(f"%{q}%"))
    return list(db.scalars(query.limit(100)))

@app.post("/recipes", response_model=s.RecipeOut, status_code=201)
def create_recipe(payload: s.RecipeCreate, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    recipe = m.Recipe(user_id=user.id, **payload.model_dump())
    db.add(recipe); db.commit(); db.refresh(recipe); return recipe

@app.get("/recipes/{recipe_id}", response_model=s.RecipeOut)
def recipe_detail(recipe_id: int, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    recipe = db.get(m.Recipe, recipe_id)
    if not recipe or (not recipe.is_public and recipe.user_id != user.id): raise HTTPException(404, "Recipe not found")
    return recipe

@app.delete("/recipes/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    recipe = db.get(m.Recipe, recipe_id)
    if not recipe or recipe.user_id != user.id: raise HTTPException(404, "Recipe not found")
    db.delete(recipe); db.commit()

@app.get("/habits/today")
def today_habits(db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    rows = db.scalars(select(m.HabitCheckin).where(m.HabitCheckin.user_id == user.id, m.HabitCheckin.checkin_date == date.today()))
    return [{"habit_key": r.habit_key, "completed": r.completed, "checkin_date": str(r.checkin_date)} for r in rows]

@app.put("/habits/checkin")
def checkin(payload: s.HabitIn, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    d = payload.checkin_date or date.today()
    row = db.scalar(select(m.HabitCheckin).where(m.HabitCheckin.user_id == user.id, m.HabitCheckin.habit_key == payload.habit_key, m.HabitCheckin.checkin_date == d))
    if row: row.completed = payload.completed
    else: db.add(m.HabitCheckin(user_id=user.id, habit_key=payload.habit_key, checkin_date=d, completed=payload.completed))
    db.commit()
    return {"habit_key": payload.habit_key, "completed": payload.completed, "checkin_date": str(d)}

@app.get("/water/today")
def get_water(db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    row = db.scalar(select(m.WaterLog).where(m.WaterLog.user_id == user.id, m.WaterLog.log_date == date.today()))
    return {"glasses": row.glasses if row else 0, "log_date": str(date.today())}

@app.put("/water/today")
def set_water(payload: s.WaterIn, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    d = payload.log_date or date.today()
    row = db.scalar(select(m.WaterLog).where(m.WaterLog.user_id == user.id, m.WaterLog.log_date == d))
    if row: row.glasses = payload.glasses
    else: db.add(m.WaterLog(user_id=user.id, log_date=d, glasses=payload.glasses))
    db.commit()
    return {"glasses": payload.glasses, "log_date": str(d)}

@app.get("/community")
def community(db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    posts = db.scalars(select(m.CommunityPost).order_by(m.CommunityPost.created_at.desc()).limit(50)).all()
    out = []
    for post in posts:
        author = db.get(m.User, post.user_id)
        count = db.scalar(select(func.count()).select_from(m.Cheer).where(m.Cheer.post_id == post.id)) or 0
        mine = db.scalar(select(m.Cheer.id).where(m.Cheer.post_id == post.id, m.Cheer.user_id == user.id)) is not None
        out.append({"id":post.id,"user_id":post.user_id,"name":author.name if author else "Member","body":post.body,"created_at":post.created_at,"cheers":count,"cheered_by_me":mine})
    return out

@app.post("/community", response_model=s.PostOut, status_code=201)
def create_post(payload: s.PostIn, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    post = m.CommunityPost(user_id=user.id, body=payload.body.strip())
    db.add(post); db.commit(); db.refresh(post)
    return {"id":post.id,"user_id":user.id,"name":user.name,"body":post.body,"created_at":post.created_at,"cheers":0,"cheered_by_me":False}

@app.post("/community/{post_id}/cheer")
def cheer(post_id: int, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    post = db.get(m.CommunityPost, post_id)
    if not post: raise HTTPException(404, "Post not found")
    existing = db.scalar(select(m.Cheer).where(m.Cheer.post_id == post_id, m.Cheer.user_id == user.id))
    if existing: db.delete(existing); action = "removed"
    else: db.add(m.Cheer(user_id=user.id, post_id=post_id)); action = "added"
    db.commit()
    return {"status": action}

@app.get("/challenges", response_model=list[s.ChallengeOut])
def challenges(db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    result = []
    for c in db.scalars(select(m.Challenge).order_by(m.Challenge.id)):
        members = db.scalar(select(func.count()).select_from(m.ChallengeMembership).where(m.ChallengeMembership.challenge_id == c.id)) or 0
        joined = db.scalar(select(m.ChallengeMembership.id).where(m.ChallengeMembership.challenge_id == c.id, m.ChallengeMembership.user_id == user.id)) is not None
        result.append({"id":c.id,"title":c.title,"description":c.description,"duration_days":c.duration_days,"members":members,"joined":joined})
    return result

@app.post("/challenges/{challenge_id}/join")
def join_challenge(challenge_id: int, db: Session = Depends(get_db), user: m.User = Depends(current_user)):
    c = db.get(m.Challenge, challenge_id)
    if not c: raise HTTPException(404, "Challenge not found")
    existing = db.scalar(select(m.ChallengeMembership).where(m.ChallengeMembership.challenge_id == challenge_id, m.ChallengeMembership.user_id == user.id))
    if existing: db.delete(existing); status = "left"
    else: db.add(m.ChallengeMembership(challenge_id=challenge_id, user_id=user.id)); status = "joined"
    db.commit(); return {"status": status}
