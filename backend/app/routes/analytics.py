from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.services.business_analyst import (
    answer_business_question
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


class BusinessQuestion(BaseModel):
    question: str
    month: str = "2018-06"


class BusinessAnswer(BaseModel):
    answer: str
    evidence: list[str]
    likely_driver: str
    recommended_actions: list[str]


class BusinessQuestionResponse(BaseModel):
    question: str
    month: str
    question_type: str
    answer: BusinessAnswer


@router.post(
    "/business-question",
    response_model=BusinessQuestionResponse
)
def business_question(request: BusinessQuestion):

    try:
        result = answer_business_question(
            request.question,
            request.month
        )

        return {
            "question": result["question"],
            "month": result["month"],
            "question_type": result["question_type"],
            "answer": result["answer"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )