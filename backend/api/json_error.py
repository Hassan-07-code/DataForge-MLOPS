import pandas as pd
from fastapi import HTTPException


def validate_features(model, dataframe: pd.DataFrame):
    """
    Validate incoming dataframe against the trained pipeline.

    Raises HTTPException(400) if columns do not match.
    """

    expected = list(model.feature_names_in_)
    received = list(dataframe.columns)

    missing = sorted(set(expected) - set(received))
    extra = sorted(set(received) - set(expected))

    if missing or extra:

        raise HTTPException(
            status_code=400,
            detail={
                "message": "Input features do not match the trained model.",
                "expected": expected,
                "received": received,
                "missing": missing,
                "extra": extra
            }
        )

    # Keep exact training order
    return dataframe[expected]