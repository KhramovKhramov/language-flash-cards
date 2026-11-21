from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Response, status

from src.application.use_cases.health.health_check import HealthCheckUseCase
from src.entrypoints.api.health.schemas import HealthCheckResponseSchema

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Checking the status of the system",
    response_model=HealthCheckResponseSchema,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": HealthCheckResponseSchema,
            "description": "A required component is unavailable",
        },
    },
)
@inject
async def health_check(
    response: Response,
    use_case: FromDishka[HealthCheckUseCase],
):
    result = await use_case.execute()
    if not result.is_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return result
