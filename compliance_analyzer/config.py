import os

# Conflicting clauses and compliance configuration
COMPLIANCE_RULES = {
    "conflicting_clauses": [
        {
            "id": "governing_law_conflict",
            "name": "Governing Law Contradiction",
            "description": "Checks for multiple conflicting governing jurisdictions in the same agreement.",
            "patterns": ["governing law", "jurisdiction", "exclusive jurisdiction", "laws of"],
            "severity": "High"
        },
        {
            "id": "liability_conflict",
            "name": "Limitation of Liability Inconsistency",
            "description": "Checks if liability limit contradicts itself (e.g. capped vs uncapped).",
            "patterns": ["limitation of liability", "indemnification", "unlimited liability", "maximum liability"],
            "severity": "Medium"
        },
        {
            "id": "ip_ownership_conflict",
            "name": "Intellectual Property Ownership Dispute",
            "description": "Checks for conflicting ownership claims (e.g. exclusive assignment vs shared licensing).",
            "patterns": ["intellectual property", "ownership", "jointly owned", "exclusive ownership", "assigns to"],
            "severity": "High"
        }
    ],
    "pii_patterns": {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone": r"\+?[0-9]{1,4}?[-.\s]?\(?[0-9]{1,3}?\)?[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}",
        "api_key": r"(?:api[_-]?key|secret|token|auth[_-]?token|access[_-]?token)[\s:=']{1,5}[a-zA-Z0-9\-_\.~]{16,}",
    }
}
