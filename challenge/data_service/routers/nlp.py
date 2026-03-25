from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from data_service.middleware.auth import verify_token
from data_service.models.schemas import ErrorResponse, NLPRequest, NLPResponse
from data_service.services.csv_service import build_nlp_context, load_dataframe
from data_service.services.nlp_service import ask

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/nlp", tags=["NLP"])


@router.post(
    "",
    response_model=NLPResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Token inválido o ausente"},
        429: {"description": "Rate limit excedido — máximo 10 requests por minuto"},
        500: {"model": ErrorResponse, "description": "Error al consultar Claude API"},
    },
    summary="Consulta en lenguaje natural sobre el dataset",
    description="Recibe una pregunta en español y responde en lenguaje natural usando Claude API con el dataset CSV como contexto. Rate limit: 10 requests/minuto.",
)
@limiter.limit("10/minute")
def nlp_query(
    request: Request,
    body: NLPRequest,
    user: dict = Depends(verify_token),
) -> NLPResponse:
    try:
        df = load_dataframe()
        context = build_nlp_context(df)
        answer = ask(body.question, context)
        return NLPResponse(question=body.question, answer=answer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
