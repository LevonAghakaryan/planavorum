from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from core.database import get_db
from app.repositories.wedding import WeddingRepository

router = APIRouter(tags=["Frontend Pages"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def get_home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/wedding/{slug}/{token}/manage", response_class=HTMLResponse)
def get_wedding_manage_page(
    slug: str,
    token: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Slug + token-ով ստուգում ենք DB-ում.
      • Slug-ը գտնում է ճիշտ հարսանիքը
      • Token-ը հաստատում է, որ հղումը ճիշտ տիրոջն է
    Ճիշտ լինելու դեպքում template-ին փոխանցվում են weddingId + weddingToken,
    որոնք JS-ը կօգտագործի ամեն API request-ում։
    """
    repo    = WeddingRepository(db)
    wedding = repo.get_by_slug(slug)

    if not wedding:
        raise HTTPException(status_code=404, detail="Հարսանիք չի գտնվել")

    import secrets
    if not secrets.compare_digest(wedding.token, token):
        raise HTTPException(status_code=403, detail="Մուտքն արգելված է")

    return templates.TemplateResponse("manage.html", {
        "request":      request,
        "wedding_id":   wedding.id,
        "wedding_token": wedding.token,   # JS-ը կօգտագործի X-Wedding-Token header-ում
    })