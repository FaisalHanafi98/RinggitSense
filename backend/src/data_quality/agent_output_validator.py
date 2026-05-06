"""
RinggitSense - Agent output quality validation.

Validates that agent outputs conform to data quality rules
beyond schema validation (which Pydantic handles).
These are semantic/business-logic validations.
"""
from src.schemas.agents.advisor import AdviceResponse
from src.schemas.agents.categorizer import CategorizerOutput
from src.schemas.agents.debt_detector import DebtDetectorOutput
from src.schemas.agents.enums import DebtTier


class AgentOutputValidator:
    """Validates agent outputs for semantic correctness.

    Pydantic already handles structural validation (types, ranges).
    This class handles cross-field business rules.
    """

    def validate_categorizer_output(self, output: CategorizerOutput) -> list[str]:
        """Validate AG-01 output beyond schema.

        Returns list of error messages (empty = valid).
        """
        errors: list[str] = []

        # Reasoning must be substantive (not just whitespace)
        if not output.reasoning.strip():
            errors.append("Categorizer reasoning is empty or whitespace")

        # Low confidence should have reasoning explaining uncertainty
        if output.confidence < 0.5 and len(output.reasoning) < 10:
            errors.append(
                "Low confidence output should have detailed reasoning"
            )

        return errors

    def validate_debt_detector_output(
        self, output: DebtDetectorOutput
    ) -> list[str]:
        """Validate AG-02 output beyond schema.

        Returns list of error messages (empty = valid).
        """
        errors: list[str] = []

        # If debt-related, must have a tier
        if output.is_debt_related and output.debt_tier is None:
            errors.append(
                "Debt-related transaction must have a debt_tier"
            )

        # If not debt-related, should not have a tier
        if not output.is_debt_related and output.debt_tier is not None:
            errors.append(
                "Non-debt transaction should not have a debt_tier"
            )

        # FORMAL and BNPL should have a provider
        if (
            output.debt_tier in (DebtTier.FORMAL, DebtTier.BNPL)
            and not output.provider
        ):
            errors.append(
                f"{output.debt_tier.value} debt should have a provider"
            )

        # HUTANG should have person_name
        if output.debt_tier == DebtTier.HUTANG and not output.person_name:
            errors.append("HUTANG debt should have a person_name")

        return errors

    def validate_advisor_output(self, output: AdviceResponse) -> list[str]:
        """Validate AG-06 output beyond schema.

        Returns list of error messages (empty = valid).
        """
        errors: list[str] = []

        # Disclaimer is MANDATORY — blocking defect if absent or trivial
        if not output.disclaimer or len(output.disclaimer.strip()) < 20:
            errors.append(
                "Advisor output MUST have a substantive disclaimer"
            )

        # Recommendations should have valid priority ordering
        priorities = [r.priority for r in output.recommendations]
        if priorities and priorities != sorted(priorities):
            errors.append(
                "Recommendations should be ordered by priority (1=highest)"
            )

        # Each recommendation must have at least one action step
        for i, rec in enumerate(output.recommendations):
            if not rec.action_steps:
                errors.append(
                    f"Recommendation {i + 1} ({rec.title}) has no action steps"
                )

        return errors
