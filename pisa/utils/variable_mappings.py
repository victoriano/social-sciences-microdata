"""Variable mappings across PISA years."""

# Common variable mappings across years
VARIABLE_MAPPINGS = {
    2006: {
        "student_id": "StIDStd",
        "country": "Country",
        "math_score": ["PV1MATH", "PV2MATH", "PV3MATH", "PV4MATH", "PV5MATH"],
    },
    2009: {
        "student_id": "StIDStd",
        "country": "Country",
        "math_score": ["PV1MATH", "PV2MATH", "PV3MATH", "PV4MATH", "PV5MATH"],
    },
    2012: {
        "student_id": "StIDStd", 
        "country": "CNT",
        "math_score": ["PV1MATH", "PV2MATH", "PV3MATH", "PV4MATH", "PV5MATH"],
    },
    2015: {
        "student_id": "CNTSTUID",
        "country": "CNTRYID",
        "math_score": ["PV1MATH", "PV2MATH", "PV3MATH", "PV4MATH", "PV5MATH"],
    },
    2018: {
        "student_id": "CNTSTUID",
        "country": "CNTRYID", 
        "math_score": ["PV1MATH", "PV2MATH", "PV3MATH", "PV4MATH", "PV5MATH"],
    },
    2022: {
        "student_id": "CNTSTUID",
        "country": "CNTRYID",
        "math_score": ["PV1MATH", "PV2MATH", "PV3MATH", "PV4MATH", "PV5MATH"],
    }
}

def get_variable_name(year: int, variable: str) -> str:
    """Get the actual variable name for a given year."""
    return VARIABLE_MAPPINGS.get(year, {}).get(variable, variable)

def harmonize_variables(df, year: int):
    """Harmonize variable names across years."""
    mapping = VARIABLE_MAPPINGS.get(year, {})
    # Implementation here
    return df
